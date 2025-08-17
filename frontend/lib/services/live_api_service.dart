import 'dart:convert';
import 'dart:io';
import 'dart:developer' as developer;
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:record/record.dart';
import 'package:just_audio/just_audio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import '../src/api/endpoints.dart';


class LiveAPIService {
  WebSocketChannel? _channel;
  final AudioRecorder _audioRecorder = AudioRecorder();
  final AudioPlayer _audioPlayer = AudioPlayer();
  
  String? _sessionId;
  bool _isConnected = false;
  
  // Callbacks for UI updates
  Function(String)? onTextResponse;
  Function(String)? onAudioResponse;
  Function(String)? onError;
  Function(bool)? onConnectionStatusChanged;
  Function()? onTurnComplete;
  
  Future<void> connect(String sessionId, {String clientId = 'test_client', String language = 'en'}) async {
    try {
      _sessionId = sessionId;
      final uri = Uri.parse(ApiConfig.wsLiveAPI(sessionId, clientId, language));
      _channel = WebSocketChannel.connect(uri);
      
      _isConnected = true;
      onConnectionStatusChanged?.call(true);
      developer.log('Connected to Live API WebSocket: $uri', name: 'LiveAPIService');
      
      // Listen for responses
      _channel!.stream.listen(
        (data) => _handleResponse(data),
        onError: (error) {
          _isConnected = false;
          onConnectionStatusChanged?.call(false);
          onError?.call('WebSocket connection error: $error');
          developer.log('WebSocket error: $error', name: 'LiveAPIService');
        },
        onDone: () {
          _isConnected = false;
          onConnectionStatusChanged?.call(false);
          developer.log('WebSocket connection closed', name: 'LiveAPIService');
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
      
      developer.log('Received response: $type - ${response.toString()}', name: 'LiveAPIService');
      
      switch (type) {
        case 'live_response':
          // Backend wraps responses in 'live_response' with 'chunk' field
          final chunk = response['chunk'];
          if (chunk != null) {
            final chunkType = chunk['type'];
            final text = chunk['text'];
            final audio = chunk['audio'];
            final turnComplete = chunk['turn_complete'] ?? false;
            final metadata = chunk['metadata'];
            
            developer.log('Processing chunk: $chunkType - text: $text, audio: ${audio != null ? "present" : "null"}', name: 'LiveAPIService');
            
            if (text != null) {
              onTextResponse?.call(text);
            }
            
            if (audio != null) {
              onAudioResponse?.call(audio);
            }
            
            // Check if turn is complete
            if (turnComplete) {
              developer.log('Turn completed with metadata: $metadata', name: 'LiveAPIService');
              onTurnComplete?.call();
            }
          }
          break;
          
        case 'response':
          // Direct response (fallback)
          final text = response['text'];
          final audio = response['audio'];
          final turnComplete = response['turn_complete'] ?? false;
          final metadata = response['metadata'];
          
          if (text != null) {
            onTextResponse?.call(text);
          }
          
          if (audio != null) {
            onAudioResponse?.call(audio);
          }
          
          // Check if turn is complete
          if (turnComplete) {
            developer.log('Turn completed with metadata: $metadata', name: 'LiveAPIService');
            onTurnComplete?.call();
          }
          break;
          
        case 'tool_result':
          final text = response['text'];
          final metadata = response['metadata'];
          if (text != null) {
            onTextResponse?.call(text);
          }
          developer.log('Tool result received: $metadata', name: 'LiveAPIService');
          break;
          
        case 'error':
          final message = response['text'] ?? response['message'] ?? 'Unknown error';
          final fallback = response['fallback'] ?? false;
          onError?.call(message);
          developer.log('Error received (fallback: $fallback): $message', name: 'LiveAPIService');
          break;
          
        default:
          developer.log('Unknown response type: $type - Data: $response', name: 'LiveAPIService');
          break;
      }
    } catch (e) {
      onError?.call('Response parsing error: $e');
      developer.log('Response parsing error: $e', name: 'LiveAPIService');
    }
  }
  
  Future<void> sendTextMessage(String content, {String language = 'en'}) async {
    if (!_isConnected) {
      onError?.call('Not connected to Live API');
      return;
    }
    
    final message = {
      'type': 'text',
      'content': content,
      'language': language,
    };
    
    _channel?.sink.add(jsonEncode(message));
  }
  
  Future<void> sendAudioMessage({String language = 'en'}) async {
    if (!_isConnected) {
      onError?.call('Not connected to Live API');
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
          sampleRate: 16000,
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
          'type': 'audio',
          'content': base64Audio,
          'language': language,
          'format': 'audio/wav',
          'sample_rate': 16000,
        };
        
        _channel?.sink.add(jsonEncode(message));
        developer.log('Audio message sent successfully', name: 'LiveAPIService');
      }
      
    } catch (e) {
      onError?.call('Audio recording failed: $e');
      developer.log('Audio recording error: $e', name: 'LiveAPIService');
    }
  }
  
  Future<void> playAudioResponse(String base64Audio) async {
    try {
      if (kIsWeb) {
        // Audio playback not supported on web for now
        onError?.call('Audio playback not supported on web. Please use the mobile app for voice features.');
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
      onError?.call('Not connected to Live API');
      return;
    }
    
    try {
      if (kIsWeb) {
        onError?.call('Audio recording not supported on web');
        return;
      }
      
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
          sampleRate: 16000,
          bitRate: 256000,
        ),
        path: tempPath,
      );
      
      developer.log('Audio recording started', name: 'LiveAPIService');
      
    } catch (e) {
      onError?.call('Failed to start audio recording: $e');
      developer.log('Start recording error: $e', name: 'LiveAPIService');
    }
  }
  
  Future<String?> stopAudioRecording({String language = 'en'}) async {
    try {
      final path = await _audioRecorder.stop();
      developer.log('Audio recording stopped at: $path', name: 'LiveAPIService');
      
      if (path != null) {
        final tempFile = File(path);
        if (await tempFile.exists()) {
          final audioBytes = await tempFile.readAsBytes();
          final base64Audio = base64Encode(audioBytes);
          
          final message = {
            'type': 'audio',
            'content': base64Audio,
            'language': language,
            'format': 'audio/wav',
            'sample_rate': 16000,
          };
          
          _channel?.sink.add(jsonEncode(message));
          developer.log('Audio message sent successfully', name: 'LiveAPIService');
          return path;
        }
      }
      
      return null;
      
    } catch (e) {
      onError?.call('Failed to stop audio recording: $e');
      developer.log('Stop recording error: $e', name: 'LiveAPIService');
      return null;
    }
  }
  
  Future<void> requestTool(String toolName, Map<String, dynamic> parameters) async {
    if (!_isConnected) {
      onError?.call('Not connected to Live API');
      return;
    }
    
    final message = {
      'type': 'tool_request',
      'tool_name': toolName,
      'parameters': parameters,
    };
    
    _channel?.sink.add(jsonEncode(message));
    developer.log('Tool request sent: $toolName with params: $parameters', name: 'LiveAPIService');
  }
  
  Future<void> disconnect() async {
    _isConnected = false;
    await _channel?.sink.close();
    // AudioRecorder doesn't have dispose method, just close the channel
    await _audioPlayer.dispose();
    onConnectionStatusChanged?.call(false);
  }
  
  bool get isConnected => _isConnected;
}
