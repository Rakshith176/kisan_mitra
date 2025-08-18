import 'dart:async';
import 'dart:convert';
import 'dart:html' as html;
import 'dart:typed_data';

import 'web_recorder.dart';

class _WebRecorder implements WebRecorder {
  html.MediaRecorder? _recorder;
  final List<html.Blob> _chunks = [];
  html.MediaStream? _stream;

  @override
  Future<void> start() async {
    try {
      // Get user media
      _stream = await html.window.navigator.mediaDevices!.getUserMedia({'audio': true});
      _chunks.clear();

      // Create MediaRecorder with supported format
      _recorder = html.MediaRecorder(_stream!, {'mimeType': 'audio/webm;codecs=opus'});

      // Set up event listeners
      _recorder!.addEventListener('dataavailable', (event) {
        final blobEvent = event as html.BlobEvent;
        final blob = blobEvent.data;
        if (blob != null && blob.size > 0) {
          _chunks.add(blob);
        }
      });

      _recorder!.start();
    } catch (e) {
      throw Exception('Failed to start web recording: $e');
    }
  }

  @override
  Future<String?> stop() async {
    if (_recorder == null) return null;

    final completer = Completer<String?>();
    
    _recorder!.addEventListener('stop', (event) async {
      try {
        // Create blob from chunks
        final blob = html.Blob(_chunks, 'audio/webm');

        // Convert to base64
        final reader = html.FileReader();
        reader.readAsArrayBuffer(blob);
        
        reader.onLoad.listen((event) {
          final result = reader.result as Uint8List;
          final b64 = base64Encode(result);

          // Cleanup
          _stream?.getTracks().forEach((track) => track.stop());
          _recorder = null;
          _chunks.clear();
          completer.complete(b64);
        });
      } catch (e) {
        completer.complete(null);
      }
    });

    _recorder!.stop();
    return completer.future;
  }
}

WebRecorder createWebRecorderImpl() => _WebRecorder();
