import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

class AudioRecorderWidget extends ConsumerStatefulWidget {
  final Function(List<int> audioBytes) onAudioRecorded;
  final VoidCallback? onRecordingStarted;
  final VoidCallback? onRecordingStopped;
  
  const AudioRecorderWidget({
    super.key,
    required this.onAudioRecorded,
    this.onRecordingStarted,
    this.onRecordingStopped,
  });

  @override
  ConsumerState<AudioRecorderWidget> createState() => _AudioRecorderWidgetState();
}

class _AudioRecorderWidgetState extends ConsumerState<AudioRecorderWidget> {
  bool _isRecording = false;
  bool _isInitialized = false;
  Timer? _recordingTimer;
  int _recordingDuration = 0;
  final AudioRecorder _audioRecorder = AudioRecorder();

  @override
  void initState() {
    super.initState();
    _initializeRecorder();
  }

  Future<void> _initializeRecorder() async {
    try {
      // Check if we're on web (audio recording not supported)
      if (kIsWeb) {
        _showSnackBar('Audio recording not supported on web. Please use the mobile app for voice features.');
        return;
      }

      // Check if we're on a platform that supports audio recording
      if (!await _audioRecorder.hasPermission()) {
        _showSnackBar('Audio recording not supported on this platform');
        return;
      }

      // Check microphone permission
      final status = await Permission.microphone.request();
      if (status != PermissionStatus.granted) {
        _showSnackBar('Microphone permission denied');
        return;
      }

      setState(() => _isInitialized = true);
    } catch (e) {
      _showSnackBar('Error initializing audio recorder: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_isInitialized) {
      return const SizedBox(
        width: 48,
        height: 48,
        child: Center(child: CircularProgressIndicator()),
      );
    }

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Recording indicator
        if (_isRecording)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.red.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(
                    color: Colors.red,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  '${(_recordingDuration / 1000).toStringAsFixed(1)}s',
                  style: const TextStyle(
                    color: Colors.red,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        
        // Record button
        IconButton(
          icon: Icon(_isRecording ? Icons.stop : Icons.mic),
          onPressed: _toggleRecording,
          tooltip: _isRecording ? 'Stop Recording' : 'Start Recording',
          color: _isRecording ? Colors.red : null,
          iconSize: 28,
        ),
      ],
    );
  }

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      await _stopRecording();
    } else {
      await _startRecording();
    }
  }

  Future<void> _startRecording() async {
    try {
      if (!_isInitialized) {
        _showSnackBar('Audio recorder not initialized');
        return;
      }

      // Start recording
      final tempDir = await getTemporaryDirectory();
      final tempPath = '${tempDir.path}/temp_audio.wav';
      
      await _audioRecorder.start(
        const RecordConfig(
          encoder: AudioEncoder.wav,
          sampleRate: 24000, // Match backend expectation
          bitRate: 256000,
        ),
        path: tempPath,
      );

      setState(() => _isRecording = true);
      widget.onRecordingStarted?.call();

      // Start timer for recording duration
      _recordingTimer = Timer.periodic(const Duration(milliseconds: 100), (timer) {
        setState(() => _recordingDuration += 100);
      });

      _showSnackBar('Recording started... Tap to stop');
    } catch (e) {
      _showSnackBar('Error starting recording: $e');
    }
  }

  Future<void> _stopRecording() async {
    try {
      if (!_isRecording) return;

      // Stop timer
      _recordingTimer?.cancel();
      
      setState(() {
        _isRecording = false;
        _recordingDuration = 0;
      });
      
      widget.onRecordingStopped?.call();

      // Stop recording and get the file path
      final path = await _audioRecorder.stop();
      
      if (path != null) {
        final tempFile = File(path);
        if (await tempFile.exists()) {
          final audioBytes = await tempFile.readAsBytes();
          widget.onAudioRecorded(audioBytes);
          _showSnackBar('Audio recording completed!');
        } else {
          _showSnackBar('Error: Audio file not found');
        }
      } else {
        _showSnackBar('Error: Failed to stop recording');
      }
      
    } catch (e) {
      _showSnackBar('Error stopping recording: $e');
    }
  }

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  @override
  void dispose() {
    _recordingTimer?.cancel();
    super.dispose();
  }
}
