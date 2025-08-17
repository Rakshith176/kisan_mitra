import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import '../services/live_api_service.dart';

class LiveChatScreen extends StatefulWidget {
  @override
  _LiveChatScreenState createState() => _LiveChatScreenState();
}

class _LiveChatScreenState extends State<LiveChatScreen> {
  final LiveAPIService _liveAPI = LiveAPIService();
  final TextEditingController _textController = TextEditingController();
  final List<ChatMessage> _messages = [];
  bool _isRecording = false;
  
  @override
  void initState() {
    super.initState();
    _setupLiveAPI();
    _connectToLiveAPI();
  }
  
  void _setupLiveAPI() {
    _liveAPI.onTextResponse = (text) {
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
    
    _liveAPI.onAudioResponse = (audio) {
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            text: "🎵 Audio response received",
            isUser: false,
            timestamp: DateTime.now(),
          ));
        });
      }
      // Play the audio response
      _liveAPI.playAudioResponse(audio);
    };
    
    // Handle turn completion to stop streaming indicators
    _liveAPI.onTurnComplete = () {
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
    
    _liveAPI.onError = (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $error')),
        );
      }
    };
    
    _liveAPI.onConnectionStatusChanged = (connected) {
      if (mounted) {
        setState(() {});
      }
    };
  }
  
  Future<void> _connectToLiveAPI() async {
    final sessionId = DateTime.now().millisecondsSinceEpoch.toString();
    // TODO: Get actual client ID from user profile
    final clientId = 'test_client_${DateTime.now().millisecondsSinceEpoch}';
    final language = 'en'; // TODO: Get from user preferences
    await _liveAPI.connect(sessionId, clientId: clientId, language: language);
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
            _liveAPI.isConnected ? Icons.wifi : Icons.wifi_off,
            color: _liveAPI.isConnected ? Colors.green : Colors.red,
          ),
          SizedBox(width: 16),
        ],
      ),
      body: Column(
        children: [
          // Connection status banner
          Container(
            width: double.infinity,
            padding: EdgeInsets.symmetric(vertical: 8, horizontal: 16),
            color: _liveAPI.isConnected ? Colors.green.shade100 : Colors.red.shade100,
            child: Row(
              children: [
                Icon(
                  _liveAPI.isConnected ? Icons.check_circle : Icons.error,
                  color: _liveAPI.isConnected ? Colors.green : Colors.red,
                  size: 20,
                ),
                SizedBox(width: 8),
                Text(
                  _liveAPI.isConnected ? 'Connected to Live API' : 'Disconnected from Live API',
                  style: TextStyle(
                    color: _liveAPI.isConnected ? Colors.green.shade800 : Colors.red.shade800,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          
          // Web platform notice
          if (kIsWeb)
            Container(
              width: double.infinity,
              padding: EdgeInsets.symmetric(vertical: 8, horizontal: 16),
              color: Colors.orange.shade100,
              child: Row(
                children: [
                  Icon(
                    Icons.info_outline,
                    color: Colors.orange.shade800,
                    size: 20,
                  ),
                  SizedBox(width: 8),
                  Text(
                    'Web version: Voice features not available. Use text chat and tools.',
                    style: TextStyle(
                      color: Colors.orange.shade800,
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
                  color: Colors.black.withOpacity(0.1),
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
                    color: _isRecording ? Colors.red : (kIsWeb ? Colors.grey : Colors.blue),
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: _isRecording ? [
                      BoxShadow(
                        color: Colors.red.withOpacity(0.3),
                        blurRadius: 8,
                        spreadRadius: 2,
                      )
                    ] : null,
                  ),
                  child: IconButton(
                    onPressed: kIsWeb ? null : _toggleRecording,
                    icon: _isRecording 
                        ? Icon(Icons.stop, color: Colors.white)
                        : Icon(Icons.mic, color: Colors.white),
                    tooltip: kIsWeb 
                        ? 'Voice recording not available on web' 
                        : (_isRecording ? 'Stop recording' : 'Start recording'),
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
    _liveAPI.requestTool(toolName, parameters);
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
      
      _liveAPI.sendTextMessage(text);
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
      final audioPath = await _liveAPI.stopAudioRecording();
      if (audioPath != null) {
        setState(() {
          _messages.add(ChatMessage(
            text: "🎤 Voice message sent",
            isUser: true,
            timestamp: DateTime.now(),
          ));
        });
      }
    } else {
      setState(() => _isRecording = true);
      await _liveAPI.startAudioRecording();
      
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
  
  @override
  void dispose() {
    _liveAPI.disconnect();
    _textController.dispose();
    super.dispose();
  }
}

class ChatMessage {
  String text; // Remove 'final' to make it mutable
  final bool isUser;
  final DateTime timestamp;
  bool isStreaming; // Track if message is still streaming
  
  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.isStreaming = false,
  });
}

class ChatMessageWidget extends StatelessWidget {
  final ChatMessage message;
  
  ChatMessageWidget({required this.message});
  
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
