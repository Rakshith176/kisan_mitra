import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:convert';
import '../services/chat_api_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});
  
  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ChatAPIService _chatAPI = ChatAPIService();
  final TextEditingController _textController = TextEditingController();
  final List<ChatMessage> _messages = [];
  bool _isRecording = false;
  Map<String, dynamic>? _experimentalBanner; // Store experimental banner data
  bool _bannerDismissed = false; // Track if banner is dismissed
  
  @override
  void initState() {
    super.initState();
    _setupChatAPI();
    _connectToChatAPI();
  }
  
  void _setupChatAPI() {
    _chatAPI.onTextResponse = (text) {
      if (mounted) {
        setState(() {
          // Check if this is a continuation of the last message (streaming effect)
          if (_messages.isNotEmpty && 
              !_messages.last.isUser && 
              _messages.last.timestamp.difference(DateTime.now()).inSeconds.abs() < 5) {
            // Append to last message for streaming effect
            _messages.last.text += text;
          } else {
            // Create new message
            _messages.add(ChatMessage(
              text: text,
              isUser: false,
              timestamp: DateTime.now(),
              isStreaming: true, // Mark as streaming
            ));
          }
        });
      }
    };
    
    _chatAPI.onAudioResponse = (audio) {
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            text: "🎵 Audio response received",
            isUser: false,
            timestamp: DateTime.now(),
            mediaType: 'audio',
          ));
        });
      }
      // Play the audio response
      _chatAPI.playAudioResponse(audio);
    };

    _chatAPI.onImageResponse = (imageBase64, mimeType) {
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            text: "🖼️ Image response received",
            isUser: false,
            timestamp: DateTime.now(),
            imageBase64: imageBase64,
            mediaType: 'image',
          ));
        });
      }
    };
    
    // Handle turn completion to stop streaming indicators
    _chatAPI.onTurnComplete = () {
      if (mounted) {
        setState(() {
          // Mark all streaming messages as complete
          for (var message in _messages) {
            if (message.isStreaming && !message.isUser) {
              message.isStreaming = false;
            }
          }
        });
      }
    };
    
    _chatAPI.onError = (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $error')),
        );
      }
    };
    
    _chatAPI.onConnectionStatusChanged = (connected) {
      if (mounted) {
        setState(() {});
      }
    };
    
    // Handle experimental banner from backend
    _chatAPI.onExperimentalBanner = (bannerData) {
      if (mounted) {
        setState(() {
          _experimentalBanner = bannerData;
        });
      }
    };
  }
  
  Future<void> _connectToChatAPI() async {
    final sessionId = DateTime.now().millisecondsSinceEpoch.toString();
    // TODO: Get actual client ID from user profile
    final clientId = 'test_client_${DateTime.now().millisecondsSinceEpoch}';
    final language = 'en'; // TODO: Get from user preferences
    await _chatAPI.connect(sessionId, clientId: clientId, language: language);
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Live Agricultural Assistant'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        actions: [
          Icon(
            _chatAPI.isConnected ? Icons.wifi : Icons.wifi_off,
            color: _chatAPI.isConnected ? Colors.green : Colors.red,
          ),
          SizedBox(width: 16),
        ],
      ),
      body: Column(
        children: [
          // Experimental Live API Banner for Hackathon Judges
          if (!_bannerDismissed) ...[
            Container(
              width: double.infinity,
              padding: EdgeInsets.symmetric(vertical: 12, horizontal: 16),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.orange.shade100, Colors.amber.shade100],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                border: Border(
                  bottom: BorderSide(color: Colors.orange.shade300, width: 1),
                ),
              ),
              child: Row(
                children: [
                  Container(
                    padding: EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.orange.shade200,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      Icons.science,
                      color: Colors.orange.shade800,
                      size: 24,
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _experimentalBanner?['title'] ?? '🧪 EXPERIMENTAL FEATURE',
                          style: TextStyle(
                            color: Colors.orange.shade800,
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                        SizedBox(height: 4),
                        Text(
                          _experimentalBanner?['message'] ?? 'Live multilingual audio responses are experimental. This demo showcases the potential for real-time voice conversations with AI agricultural assistance.',
                          style: TextStyle(
                            color: Colors.orange.shade700,
                            fontSize: 12,
                            height: 1.3,
                          ),
                        ),
                        SizedBox(height: 4),
                        Text(
                          _experimentalBanner?['details'] ?? 'For Hackathon Judges: This demonstrates our vision for accessible, voice-first agricultural advisory.',
                          style: TextStyle(
                            color: Colors.orange.shade600,
                            fontSize: 11,
                            fontStyle: FontStyle.italic,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: () {
                      setState(() {
                        _bannerDismissed = true;
                      });
                    },
                    icon: Icon(
                      Icons.close,
                      color: Colors.orange.shade600,
                      size: 20,
                    ),
                    padding: EdgeInsets.zero,
                    constraints: BoxConstraints(),
                  ),
                ],
              ),
            ),
          ],
          
          // Connection status banner
          Container(
            width: double.infinity,
            padding: EdgeInsets.symmetric(vertical: 8, horizontal: 16),
            color: _chatAPI.isConnected ? Colors.green.shade100 : Colors.red.shade100,
            child: Row(
              children: [
                Icon(
                  _chatAPI.isConnected ? Icons.check_circle : Icons.error,
                  color: _chatAPI.isConnected ? Colors.green : Colors.red,
                  size: 20,
                ),
                SizedBox(width: 8),
                Text(
                                      _chatAPI.isConnected ? 'Connected to Chat API' : 'Disconnected from Chat API',
                  style: TextStyle(
                                          color: _chatAPI.isConnected ? Colors.green.shade800 : Colors.red.shade800,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          
          // Audio status banner
          Container(
            width: double.infinity,
            padding: EdgeInsets.symmetric(vertical: 8, horizontal: 16),
            color: _isRecording ? Colors.red.shade100 : Colors.blue.shade100,
            child: Row(
              children: [
                Icon(
                  _isRecording ? Icons.mic : Icons.mic_none,
                  color: _isRecording ? Colors.red.shade800 : Colors.blue.shade800,
                  size: 20,
                ),
                SizedBox(width: 8),
                                  Text(
                    _isRecording 
                        ? 'Recording audio... Tap to stop' 
                        : 'Tap microphone to record voice message',
                    style: TextStyle(
                      color: _isRecording ? Colors.red.shade800 : Colors.blue.shade800,
                      fontWeight: FontWeight.w500,
                      fontSize: 12,
                    ),
                  ),
              ],
            ),
          ),
          
          // Chat messages
          Expanded(
            child: _messages.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.chat_bubble_outline,
                          size: 64,
                          color: Colors.grey.shade400,
                        ),
                        SizedBox(height: 16),
                        Text(
                          'Start a conversation with your\nagricultural assistant',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Colors.grey.shade600,
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: EdgeInsets.all(16),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      final message = _messages[index];
                      return ChatMessageWidget(message: message);
                    },
                  ),
          ),
          
          // Quick tool buttons
          Container(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Quick Actions',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey.shade700,
                  ),
                ),
                SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _buildToolButton(
                      '🌤️ Weather',
                      'get_weather_info',
                      {
                        'location': 'Karnataka',
                        'crop_type': 'rice'
                      },
                    ),
                    _buildToolButton(
                      '🏛️ PM KISAN',
                      'get_government_schemes',
                      {
                        'scheme_name': 'PM KISAN',
                        'query_type': 'eligibility'
                      },
                    ),
                    _buildToolButton(
                      '💰 Market Prices',
                      'get_market_prices',
                      {
                        'crop_name': 'rice'
                      },
                    ),
                    _buildToolButton(
                      '🌱 Crop Advice',
                      'get_crop_advice',
                      {
                        'crop_name': 'rice',
                        'growth_stage': 'vegetative'
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),
          
          // Input area
          Container(
            padding: EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.1),
                  blurRadius: 4,
                  offset: Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                // Text input
                Expanded(
                  child: TextField(
                    controller: _textController,
                    decoration: InputDecoration(
                      hintText: 'Ask about farming, weather, or government schemes...',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide(color: Colors.green.shade300),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide(color: Colors.green),
                      ),
                      contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    ),
                    onSubmitted: (_) => _sendTextMessage(),
                  ),
                ),
                
                SizedBox(width: 8),
                
                // Image upload button
                Container(
                  decoration: BoxDecoration(
                    color: Colors.orange,
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: IconButton(
                    onPressed: _showImagePickerDialog,
                    icon: Icon(Icons.image, color: Colors.white),
                    tooltip: 'Upload image',
                  ),
                ),
                
                SizedBox(width: 8),
                
                // Send button
                Container(
                  decoration: BoxDecoration(
                    color: Colors.green,
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: IconButton(
                    onPressed: _sendTextMessage,
                    icon: Icon(Icons.send, color: Colors.white),
                    tooltip: 'Send message',
                  ),
                ),
                
                SizedBox(width: 8),
                
                // Voice button
                Container(
                  decoration: BoxDecoration(
                    color: _isRecording ? Colors.red : Colors.blue,
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: _isRecording ? [
                      BoxShadow(
                        color: Colors.red.withValues(alpha: 0.3),
                        blurRadius: 8,
                        spreadRadius: 2,
                      )
                    ] : null,
                  ),
                  child: IconButton(
                    onPressed: _toggleRecording,
                    icon: _isRecording 
                        ? Icon(Icons.stop, color: Colors.white)
                        : Icon(Icons.mic, color: Colors.white),
                    tooltip: _isRecording ? 'Stop recording' : 'Start recording',
                  ),
                ),
                
                // Recording indicator
                if (_isRecording && !kIsWeb)
                  Container(
                    margin: EdgeInsets.only(left: 8),
                    padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.red.shade100,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.red.shade300),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: Colors.red,
                            shape: BoxShape.circle,
                          ),
                        ),
                        SizedBox(width: 4),
                        Text(
                          'Recording...',
                          style: TextStyle(
                            color: Colors.red.shade800,
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildToolButton(String label, String toolName, Map<String, dynamic> parameters) {
    return ElevatedButton(
      onPressed: () => _requestTool(toolName, parameters),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.green.shade50,
        foregroundColor: Colors.green.shade800,
        side: BorderSide(color: Colors.green.shade300),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
      child: Text(
        label,
        style: TextStyle(fontSize: 12),
      ),
    );
  }
  
  void _requestTool(String toolName, Map<String, dynamic> parameters) {
    // Show tool request in chat
    setState(() {
      _messages.add(ChatMessage(
        text: "🔧 Requesting: $toolName",
        isUser: true,
        timestamp: DateTime.now(),
      ));
    });
    
    // Send tool request to backend
    _chatAPI.requestTool(toolName, parameters);
  }
  
  void _sendTextMessage() {
    final text = _textController.text.trim();
    if (text.isNotEmpty) {
      setState(() {
        _messages.add(ChatMessage(
          text: text,
          isUser: true,
          timestamp: DateTime.now(),
        ));
      });
      
      _chatAPI.sendTextMessage(text);
      _textController.clear();
      
      // Scroll to bottom to show new message
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_messages.isNotEmpty) {
          // Scroll to bottom logic would go here if we had a ScrollController
        }
      });
    }
  }
  
  void _toggleRecording() async {
    if (_isRecording) {
      setState(() => _isRecording = false);
      final audioPath = await _chatAPI.stopAudioRecording();
      if (audioPath != null) {
        setState(() {
          _messages.add(ChatMessage(
            text: "🎤 Voice message sent",
            isUser: true,
            timestamp: DateTime.now(),
            mediaType: 'audio',
          ));
        });
      }
    } else {
      setState(() => _isRecording = true);
      await _chatAPI.startAudioRecording();
      
      // Show recording started message
      setState(() {
        _messages.add(ChatMessage(
          text: "🎤 Recording started... (tap again to stop)",
          isUser: true,
          timestamp: DateTime.now(),
        ));
      });
    }
  }

  void _pickImageFromGallery() async {
    try {
      await _chatAPI.sendImageMessage();
      setState(() {
        _messages.add(ChatMessage(
          text: "📷 Image sent from gallery",
          isUser: true,
          timestamp: DateTime.now(),
          mediaType: 'image',
        ));
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error sending image: $e')),
      );
    }
  }

  void _takePhotoWithCamera() async {
    try {
      await _chatAPI.sendCameraImage();
      setState(() {
        _messages.add(ChatMessage(
          text: "📸 Photo taken with camera",
          isUser: true,
          timestamp: DateTime.now(),
          mediaType: 'image',
        ));
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error taking photo: $e')),
      );
    }
  }

  void _showImagePickerDialog() {
    showModalBottomSheet(
      context: context,
      builder: (BuildContext context) {
        return Container(
          padding: EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: Icon(Icons.photo_library, color: Colors.green),
                title: Text('Choose from Gallery'),
                onTap: () {
                  Navigator.pop(context);
                  _pickImageFromGallery();
                },
              ),
              ListTile(
                leading: Icon(Icons.camera_alt, color: Colors.green),
                title: Text('Take Photo'),
                onTap: () {
                  Navigator.pop(context);
                  _takePhotoWithCamera();
                },
              ),
            ],
          ),
        );
      },
    );
  }
  

  
  @override
  void dispose() {
    _chatAPI.disconnect();
    _textController.dispose();
    super.dispose();
  }
}

class ChatMessage {
  String text; // Remove 'final' to make it mutable
  final bool isUser;
  final DateTime timestamp;
  bool isStreaming; // Track if message is still streaming
  final String? imagePath; // Path to image file
  final String? imageBase64; // Base64 encoded image data
  final String? mediaType; // Type of media (text, image, audio)
  
  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.isStreaming = false,
    this.imagePath,
    this.imageBase64,
    this.mediaType,
  });
}

class ChatMessageWidget extends StatelessWidget {
  final ChatMessage message;
  
  const ChatMessageWidget({super.key, required this.message});
  
  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.only(
        bottom: 16,
        left: message.isUser ? 64 : 0,
        right: message.isUser ? 0 : 64,
      ),
      child: Row(
        mainAxisAlignment: message.isUser 
            ? MainAxisAlignment.end 
            : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!message.isUser) ...[
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.green,
              child: Icon(Icons.agriculture, color: Colors.white, size: 16),
            ),
            SizedBox(width: 8),
          ],
          
          Flexible(
            child: Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: message.isUser 
                    ? Colors.green.shade100 
                    : Colors.grey.shade100,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: message.isUser 
                      ? Colors.green.shade300 
                      : Colors.grey.shade300,
                ),
              ),
                                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Display image if present
                      if (message.mediaType == 'image' && message.imageBase64 != null)
                        Container(
                          margin: EdgeInsets.only(bottom: 8),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: Image.memory(
                              base64Decode(message.imageBase64!),
                              width: 200,
                              height: 200,
                              fit: BoxFit.cover,
                            ),
                          ),
                        ),
                      
                      // Display text
                      if (message.text.isNotEmpty)
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                message.text,
                                style: TextStyle(
                                  color: message.isUser 
                                      ? Colors.green.shade800 
                                      : Colors.grey.shade800,
                                  fontSize: 14,
                                ),
                              ),
                            ),
                            if (message.isStreaming && !message.isUser)
                              Container(
                                margin: EdgeInsets.only(left: 8),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Container(
                                      width: 4,
                                      height: 4,
                                      decoration: BoxDecoration(
                                        color: Colors.green,
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                    SizedBox(width: 2),
                                    Container(
                                      width: 4,
                                      height: 4,
                                      decoration: BoxDecoration(
                                        color: Colors.green,
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                    SizedBox(width: 2),
                                    Container(
                                      width: 4,
                                      height: 4,
                                      decoration: BoxDecoration(
                                        color: Colors.green,
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                          ],
                        ),
                      SizedBox(height: 4),
                      Text(
                        _formatTime(message.timestamp),
                        style: TextStyle(
                          color: Colors.grey.shade500,
                          fontSize: 10,
                        ),
                      ),
                    ],
                  ),
            ),
          ),
          
          if (message.isUser) ...[
            SizedBox(width: 8),
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.blue,
              child: Icon(Icons.person, color: Colors.white, size: 16),
            ),
          ],
        ],
      ),
    );
  }
  
  String _formatTime(DateTime timestamp) {
    return '${timestamp.hour.toString().padLeft(2, '0')}:${timestamp.minute.toString().padLeft(2, '0')}';
  }
}
