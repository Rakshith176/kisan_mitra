import 'dart:convert';
import 'dart:io';
import 'dart:developer' as developer;
import 'dart:typed_data';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:record/record.dart';
import 'package:just_audio/just_audio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:image_picker/image_picker.dart';
import '../src/api/endpoints.dart';
import 'web_recorder.dart';


class ChatAPIService {
  WebSocketChannel? _channel;
  final AudioRecorder _audioRecorder = AudioRecorder();
  final AudioPlayer _audioPlayer = AudioPlayer();
  
  String? _sessionId;
  bool _isConnected = false;
  WebRecorder? _webRecorder; // Used only on web
  
  // Callbacks for UI updates
  Function(String)? onTextResponse;
  Function(String)? onAudioResponse;
  Function(String, String)? onImageResponse; // imageBase64, mimeType
  Function(String)? onError;
  Function(bool)? onConnectionStatusChanged;
  Function()? onTurnComplete;
  Function(Map<String, dynamic>)? onExperimentalBanner; // New callback for experimental banner
  
  Future<void> connect(String sessionId, {String clientId = 'test_client', String language = 'en'}) async {
    try {
      _sessionId = sessionId;
      final uri = Uri.parse(ApiConfig.wsChat(sessionId, clientId, language));
      _channel = WebSocketChannel.connect(uri);
      
      _isConnected = true;
      onConnectionStatusChanged?.call(true);
      developer.log('Connected to Chat WebSocket: $uri', name: 'ChatAPIService');
      
      // Listen for responses
      _channel!.stream.listen(
        (data) => _handleResponse(data),
        onError: (error) {
          _isConnected = false;
          onConnectionStatusChanged?.call(false);
          onError?.call('WebSocket connection error: $error');
          developer.log('WebSocket error: $error', name: 'ChatAPIService');
        },
        onDone: () {
          _isConnected = false;
          onConnectionStatusChanged?.call(false);
          developer.log('WebSocket connection closed', name: 'ChatAPIService');
        },
      );
      
    } catch (e) {
      _isConnected = false;
      onConnectionStatusChanged?.call(false);
      onError?.call('Connection failed: $e');
    }
  }
  
  void _handleResponse(dynamic data) {
    try {
      final response = jsonDecode(data);
      final type = response['type'];
      
      developer.log('Received response: $type - ${response.toString()}', name: 'ChatAPIService');
      
      switch (type) {
        case 'experimental_banner':
          final title = response['title'] ?? 'Experimental Feature';
          final message = response['message'] ?? '';
          final details = response['details'] ?? '';
          final status = response['status'] ?? 'demo';
          
          onExperimentalBanner?.call({
            'title': title,
            'message': message,
            'details': details,
            'status': status,
          });
          developer.log('Experimental banner received: $title', name: 'ChatAPIService');
          break;
          
        case 'live_response':
          // Backend wraps responses in 'live_response' with 'chunk' field
          final chunk = response['chunk'];
          if (chunk != null) {
            final chunkType = chunk['type'];
            final text = chunk['text'];
            final audio = chunk['audio'];
            final turnComplete = chunk['turn_complete'] ?? false;
            final metadata = chunk['metadata'];
            
            developer.log('Processing chunk: $chunkType - text: $text, audio: ${audio != null ? "present" : "null"}', name: 'ChatAPIService');
            
            if (text != null) {
              onTextResponse?.call(text);
            }
            
            if (audio != null) {
              onAudioResponse?.call(audio);
            }
            
            // Check if turn is complete
            if (turnComplete) {
              developer.log('Turn completed with metadata: $metadata', name: 'ChatAPIService');
              onTurnComplete?.call();
            }
          }
          break;
          
        case 'response':
          // Main chat endpoint response
          final data = response['data'];
          if (data != null) {
            final text = data['text'];
            final audio = data['audio'];
            final image = data['image'];
            final metadata = data['metadata'];
            
            if (text != null) {
              onTextResponse?.call(text);
            }
            
            if (audio != null) {
              onAudioResponse?.call(audio);
            }

            if (image != null) {
              final mimeType = data['mime_type'] ?? 'image/jpeg';
              onImageResponse?.call(image, mimeType);
            }
          
            // Chat responses are always complete
            developer.log('Chat response completed with metadata: $metadata', name: 'ChatAPIService');
            onTurnComplete?.call();
          }
          break;
          
        case 'tool_result':
          final toolText = response['text'] ?? response['result'] ?? 'Tool executed successfully';
          final toolMetadata = response['metadata'];
          if (toolText != null) {
            onTextResponse?.call(toolText);
          }
          developer.log('Tool result received: $toolMetadata', name: 'ChatAPIService');
          break;
          
        case 'error':
          final errorMessage = response['text'] ?? response['message'] ?? 'Unknown error';
          final fallback = response['fallback'] ?? false;
          onError?.call(errorMessage);
          developer.log('Error received (fallback: $fallback): $errorMessage', name: 'ChatAPIService');
          break;
          
        default:
          developer.log('Unknown response type: $type - Data: $response', name: 'ChatAPIService');
          break;
      }
    } catch (e) {
      onError?.call('Response parsing error: $e');
      developer.log('Response parsing error: $e', name: 'ChatAPIService');
    }
  }
  
  Future<void> sendTextMessage(String content, {String language = 'en'}) async {
    if (!_isConnected) {
      onError?.call('Not connected to Chat API');
      return;
    }
    
    final message = {
      'type': 'request',
      'data': {
        'media_type': 'text',
        'content': content,
        'mime_type': null,
        'metadata': {
          'language': language,
        }
      },
      'message_id': DateTime.now().millisecondsSinceEpoch.toString(),
    };
    
    _channel?.sink.add(jsonEncode(message));
  }
  
  Future<void> sendAudioMessage({String language = 'en'}) async {
    if (!_isConnected) {
      onError?.call('Not connected to Chat API');
      return;
    }
    
    try {
      // Check if we're on web (audio recording not supported)
      if (kIsWeb) {
        onError?.call('Audio recording not supported on web. Please use the mobile app for voice features.');
        return;
      }
      
      // Check if we're on a platform that supports audio recording
      if (!await _audioRecorder.hasPermission()) {
        onError?.call('Audio recording not supported on this platform');
        return;
      }
      
      // Check microphone permission
      final status = await Permission.microphone.request();
      if (status != PermissionStatus.granted) {
        onError?.call('Microphone permission denied');
        return;
      }
      
      // Start recording
      final tempDir = await getTemporaryDirectory();
      final tempPath = '${tempDir.path}/temp_audio.wav';
      
      await _audioRecorder.start(
        const RecordConfig(
          encoder: AudioEncoder.wav,
          sampleRate: 16000, // Updated to match Live API requirements
          bitRate: 256000,
        ),
        path: tempPath,
      );
      
      // Record for 5 seconds (adjust as needed)
      await Future.delayed(Duration(seconds: 5));
      
      // Stop recording
      await _audioRecorder.stop();
      
      // Check if file exists and convert to base64
      final tempFile = File(tempPath);
      if (await tempFile.exists()) {
        final audioBytes = await tempFile.readAsBytes();
        final base64Audio = base64Encode(audioBytes);
        
        final message = {
          'type': 'request',
          'data': {
            'media_type': 'audio',
            'content': base64Audio,
            'mime_type': 'audio/pcm;rate=16000',
            'metadata': {
              'language': language,
              'sample_rate': 16000,
            }
          },
          'message_id': DateTime.now().millisecondsSinceEpoch.toString(),
        };
        
        _channel?.sink.add(jsonEncode(message));
        developer.log('Audio message sent successfully', name: 'ChatAPIService');
      }
      
    } catch (e) {
      onError?.call('Audio recording failed: $e');
      developer.log('Audio recording error: $e', name: 'ChatAPIService');
    }
  }
  
  Future<void> playAudioResponse(String base64Audio) async {
    try {
      if (kIsWeb) {
        // Web audio playback not implemented yet
        onError?.call('Audio playback not supported on web yet. Please use the mobile app for voice features.');
        return;
      }
      
      // On mobile, save to file and play
      final audioBytes = base64Decode(base64Audio);
      final tempDir = await getTemporaryDirectory();
      final tempFile = File('${tempDir.path}/response_audio.wav');
      await tempFile.writeAsBytes(audioBytes);
      
      await _audioPlayer.setFilePath(tempFile.path);
      await _audioPlayer.play();
      
    } catch (e) {
      onError?.call('Audio playback failed: $e');
    }
  }
  
  Future<void> startAudioRecording() async {
    if (!_isConnected) {
      onError?.call('Not connected to Chat API');
      return;
    }
    
    try {
      if (kIsWeb) {
        // Initialize and start web recorder
        _webRecorder ??= createWebRecorder();
        await _webRecorder!.start();
        developer.log('Web audio recording started', name: 'ChatAPIService');
        return;
      }
      
      // Mobile audio recording
      if (!await _audioRecorder.hasPermission()) {
        onError?.call('Audio recording not supported on this platform');
        return;
      }
      
      final status = await Permission.microphone.request();
      if (status != PermissionStatus.granted) {
        onError?.call('Microphone permission denied');
        return;
      }
      
      final tempDir = await getTemporaryDirectory();
      final tempPath = '${tempDir.path}/temp_audio.wav';
      
      await _audioRecorder.start(
        const RecordConfig(
          encoder: AudioEncoder.wav,
          sampleRate: 16000, // Updated to match Live API requirements
          bitRate: 256000,
        ),
        path: tempPath,
      );
      
      developer.log('Mobile audio recording started', name: 'ChatAPIService');
      
    } catch (e) {
      onError?.call('Failed to start audio recording: $e');
      developer.log('Start recording error: $e', name: 'ChatAPIService');
    }
  }
  
  Future<String?> stopAudioRecording({String language = 'en'}) async {
    try {
      if (kIsWeb) {
        // Stop web recorder and send audio
        _webRecorder ??= createWebRecorder();
        final base64Audio = await _webRecorder!.stop();
        if (base64Audio == null) {
          onError?.call('Failed to capture audio from microphone');
          return null;
        }
        final message = {
          'type': 'request',
          'data': {
            'media_type': 'audio',
            'content': base64Audio,
            'mime_type': 'audio/webm;codecs=opus',
            'metadata': {
              'language': language,
              'sample_rate': 16000,
            }
          },
          'message_id': DateTime.now().millisecondsSinceEpoch.toString(),
        };
        _channel?.sink.add(jsonEncode(message));
        developer.log('Web audio message sent successfully', name: 'ChatAPIService');
        return 'web_audio';
      }
      
      // Mobile audio recording
      final path = await _audioRecorder.stop();
      developer.log('Audio recording stopped at: $path', name: 'LiveAPIService');
      
      if (path != null) {
        final tempFile = File(path);
        if (await tempFile.exists()) {
          final audioBytes = await tempFile.readAsBytes();
          final base64Audio = base64Encode(audioBytes);
          
          final audioMessage = {
            'type': 'request',
            'data': {
              'media_type': 'audio',
              'content': base64Audio,
              'mime_type': 'audio/pcm;rate=16000',
              'metadata': {
                'language': language,
                'sample_rate': 16000,
              }
            },
            'message_id': DateTime.now().millisecondsSinceEpoch.toString(),
          };
          
          _channel?.sink.add(jsonEncode(audioMessage));
          developer.log('Mobile audio message sent successfully', name: 'ChatAPIService');
          return path;
        }
      }
      
      return null;
      
    } catch (e) {
      onError?.call('Failed to stop audio recording: $e');
      developer.log('Stop recording error: $e', name: 'ChatAPIService');
      return null;
    }
  }
  
  Future<void> requestTool(String toolName, Map<String, dynamic> parameters) async {
    if (!_isConnected) {
      onError?.call('Not connected to Chat API');
      return;
    }
    
    final message = {
      'type': 'tool_request',
      'tool_name': toolName,
      'parameters': parameters,
    };
    
    _channel?.sink.add(jsonEncode(message));
    developer.log('Tool request sent: $toolName with params: $parameters', name: 'ChatAPIService');
  }
  
  Future<void> disconnect() async {
    _isConnected = false;
    await _channel?.sink.close();
    // AudioRecorder doesn't have dispose method, just close the channel
    await _audioPlayer.dispose();
    onConnectionStatusChanged?.call(false);
  }
  
  bool get isConnected => _isConnected;
  
  Future<bool> get isAudioSupported async {
    if (kIsWeb) {
      // Assume supported; browser will prompt for permission
      return true;
    } else {
      return await _audioRecorder.hasPermission();
    }
  }

  Future<void> sendImageMessage({String language = 'en'}) async {
    if (!_isConnected) {
      onError?.call('Not connected to Chat API');
      return;
    }

    try {
      final ImagePicker picker = ImagePicker();
      final XFile? image = await picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (image == null) {
        return; // User cancelled
      }

      // Read image as bytes
      final Uint8List imageBytes = await image.readAsBytes();
      final String base64Image = base64Encode(imageBytes);
      
      // Determine MIME type based on file extension
      String mimeType = 'image/jpeg'; // default
      final String extension = image.path.split('.').last.toLowerCase();
      switch (extension) {
        case 'png':
          mimeType = 'image/png';
          break;
        case 'gif':
          mimeType = 'image/gif';
          break;
        case 'webp':
          mimeType = 'image/webp';
          break;
        case 'jpg':
        case 'jpeg':
        default:
          mimeType = 'image/jpeg';
          break;
      }

      final message = {
        'type': 'request',
        'data': {
          'media_type': 'image',
          'content': base64Image,
          'mime_type': mimeType,
          'metadata': {
            'language': language,
            'filename': image.name,
            'size': imageBytes.length,
          }
        },
        'message_id': DateTime.now().millisecondsSinceEpoch.toString(),
      };

      _channel?.sink.add(jsonEncode(message));
      developer.log('Image message sent successfully', name: 'ChatAPIService');
      
    } catch (e) {
      onError?.call('Failed to send image: $e');
      developer.log('Image send error: $e', name: 'ChatAPIService');
    }
  }

  Future<void> sendCameraImage({String language = 'en'}) async {
    if (!_isConnected) {
      onError?.call('Not connected to Chat API');
      return;
    }

    try {
      final ImagePicker picker = ImagePicker();
      final XFile? image = await picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (image == null) {
        return; // User cancelled
      }

      // Read image as bytes
      final Uint8List imageBytes = await image.readAsBytes();
      final String base64Image = base64Encode(imageBytes);
      
      // Determine MIME type based on file extension
      String mimeType = 'image/jpeg'; // default
      final String extension = image.path.split('.').last.toLowerCase();
      switch (extension) {
        case 'png':
          mimeType = 'image/png';
          break;
        case 'gif':
          mimeType = 'image/gif';
          break;
        case 'webp':
          mimeType = 'image/webp';
          break;
        case 'jpg':
        case 'jpeg':
        default:
          mimeType = 'image/jpeg';
          break;
      }

      final message = {
        'type': 'request',
        'data': {
          'media_type': 'image',
          'content': base64Image,
          'mime_type': mimeType,
          'metadata': {
            'language': language,
            'filename': image.name,
            'size': imageBytes.length,
            'source': 'camera',
          }
        },
        'message_id': DateTime.now().millisecondsSinceEpoch.toString(),
      };

      _channel?.sink.add(jsonEncode(message));
      developer.log('Camera image message sent successfully', name: 'ChatAPIService');
      
    } catch (e) {
      onError?.call('Failed to send camera image: $e');
      developer.log('Camera image send error: $e', name: 'ChatAPIService');
    }
  }
}
