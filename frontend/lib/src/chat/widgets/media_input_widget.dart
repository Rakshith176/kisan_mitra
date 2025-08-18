import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:permission_handler/permission_handler.dart';

import '../../state/chat_provider.dart';
import 'audio_recorder_widget.dart';

class MediaInputWidget extends ConsumerStatefulWidget {
  final String clientId;
  final String sessionId;
  final String language;
  
  const MediaInputWidget({
    super.key,
    required this.clientId,
    required this.sessionId,
    required this.language,
  });

  @override
  ConsumerState<MediaInputWidget> createState() => _MediaInputWidgetState();
}

class _MediaInputWidgetState extends ConsumerState<MediaInputWidget> {
  final ImagePicker _imagePicker = ImagePicker();
  bool _isProcessing = false;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        // Image picker button
        IconButton(
          icon: const Icon(Icons.image),
          onPressed: _isProcessing ? null : _pickImage,
          tooltip: 'Send Image',
        ),
        
        // Voice recording button
        AudioRecorderWidget(
          onAudioRecorded: _onAudioRecorded,
          onRecordingStarted: () => setState(() {}),
          onRecordingStopped: () => setState(() {}),
        ),
        
        const SizedBox(width: 8),
      ],
    );
  }

  Future<void> _pickImage() async {
    try {
      setState(() => _isProcessing = true);
      
      // Check camera permission
      final status = await Permission.camera.status;
      if (status.isDenied) {
        final result = await Permission.camera.request();
        if (result.isDenied) {
          _showSnackBar('Camera permission is required to take photos');
          return;
        }
      }

      // Pick image from camera or gallery
      final XFile? image = await showModalBottomSheet<XFile?>(
        context: context,
        builder: (context) => Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('Take Photo'),
              onTap: () async {
                Navigator.pop(context, await _imagePicker.pickImage(
                  source: ImageSource.camera,
                  maxWidth: 1024,
                  maxHeight: 1024,
                  imageQuality: 80,
                ));
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('Choose from Gallery'),
              onTap: () async {
                Navigator.pop(context, await _imagePicker.pickImage(
                  source: ImageSource.gallery,
                  maxWidth: 1024,
                  maxHeight: 1024,
                  imageQuality: 80,
                ));
              },
            ),
          ],
        ),
      );

      if (image != null) {
        await _processAndSendImage(image);
      }
    } catch (e) {
      _showSnackBar('Error picking image: $e');
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  Future<void> _processAndSendImage(XFile imageFile) async {
    try {
      // Read image file
      final bytes = await imageFile.readAsBytes();
      
      // Convert to base64
      final base64String = base64Encode(bytes);
      
      // Determine mime type
      final mimeType = _getMimeType(imageFile.path);
      
      // Ensure connection
      await ref.read(chatControllerProvider.notifier).connect(
        sessionId: widget.sessionId,
        clientId: widget.clientId,
        language: widget.language,
      );
      
      // Send image
      await ref.read(chatControllerProvider.notifier).sendImage(base64String, mimeType);
      
      _showSnackBar('Image sent successfully');
    } catch (e) {
      _showSnackBar('Error sending image: $e');
    }
  }

  Future<void> _onAudioRecorded(List<int> audioBytes) async {
    try {
      // Ensure connection
      await ref.read(chatControllerProvider.notifier).connect(
        sessionId: widget.sessionId,
        clientId: widget.clientId,
        language: widget.language,
      );
      
      // Send audio
      await ref.read(chatControllerProvider.notifier).sendAudio(audioBytes, 'audio/pcm;rate=16000;channels=1');
      
      _showSnackBar('Voice message sent successfully');
    } catch (e) {
      _showSnackBar('Error sending voice message: $e');
    }
  }

  String _getMimeType(String filePath) {
    final extension = filePath.split('.').last.toLowerCase();
    switch (extension) {
      case 'jpg':
      case 'jpeg':
        return 'image/jpeg';
      case 'png':
        return 'image/png';
      case 'gif':
        return 'image/gif';
      case 'webp':
        return 'image/webp';
      default:
        return 'image/jpeg';
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
}
