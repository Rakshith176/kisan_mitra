import 'dart:async';
import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../api/endpoints.dart';

class ChatMessage {
  final String id;
  final String role; // 'user' | 'assistant'
  final String type; // 'text' | 'audio' | 'image'
  final String? text;
  final String? audioPath; // local file path if we choose to persist
  final String? imagePath; // local file path for images
  final String? imageBase64; // base64 encoded image data
  final DateTime createdAt;
  const ChatMessage({
    required this.id,
    required this.role,
    required this.type,
    this.text,
    this.audioPath,
    this.imagePath,
    this.imageBase64,
    required this.createdAt,
  });
}

class Conversation {
  final String id;
  final String title;
  final DateTime createdAt;
  final DateTime updatedAt;
  final int messageCount;
  final String? lastMessagePreview;
  
  const Conversation({
    required this.id,
    required this.title,
    required this.createdAt,
    required this.updatedAt,
    required this.messageCount,
    this.lastMessagePreview,
  });
  
  Conversation copyWith({
    String? id,
    String? title,
    DateTime? createdAt,
    DateTime? updatedAt,
    int? messageCount,
    String? lastMessagePreview,
  }) => Conversation(
    id: id ?? this.id,
    title: title ?? this.title,
    createdAt: createdAt ?? this.createdAt,
    updatedAt: updatedAt ?? this.updatedAt,
    messageCount: messageCount ?? this.messageCount,
    lastMessagePreview: lastMessagePreview ?? this.lastMessagePreview,
  );
}

class ChatState {
  final List<ChatMessage> messages;
  final List<Conversation> conversations;
  final String? currentConversationId;
  final bool connecting;
  final bool connected;
  final String typingText; // partial text from assistant
  final List<int> audioBuffer; // assembled PCM chunks (bytes)
  final bool loadingConversations;
  final bool loadingMessages;
  final String language; // current language for the session
  
  const ChatState({
    required this.messages,
    required this.conversations,
    this.currentConversationId,
    required this.connecting,
    required this.connected,
    required this.typingText,
    required this.audioBuffer,
    required this.loadingConversations,
    required this.loadingMessages,
    required this.language,
  });

  ChatState copyWith({
    List<ChatMessage>? messages,
    List<Conversation>? conversations,
    String? currentConversationId,
    bool? connecting,
    bool? connected,
    String? typingText,
    List<int>? audioBuffer,
    bool? loadingConversations,
    bool? loadingMessages,
    String? language,
  }) => ChatState(
        messages: messages ?? this.messages,
        conversations: conversations ?? this.conversations,
        currentConversationId: currentConversationId ?? this.currentConversationId,
        connecting: connecting ?? this.connecting,
        connected: connected ?? this.connected,
        typingText: typingText ?? this.typingText,
        audioBuffer: audioBuffer ?? this.audioBuffer,
        loadingConversations: loadingConversations ?? this.loadingConversations,
        loadingMessages: loadingMessages ?? this.loadingMessages,
        language: language ?? this.language,
      );

  factory ChatState.initial() => const ChatState(
        messages: [],
        conversations: [],
        currentConversationId: null,
        connecting: false,
        connected: false,
        typingText: '',
        audioBuffer: [],
        loadingConversations: false,
        loadingMessages: false,
        language: 'en',
      );
}

class ChatController extends StateNotifier<ChatState> {
  ChatController() : super(ChatState.initial());

  WebSocketChannel? _channel;
  StreamSubscription? _sub;
  // Stored for reconnection/backoff usage if needed in future iterations
  // Connection params are passed in and not retained for now to keep state minimal

  Future<void> connect({
    required String sessionId,
    required String clientId,
    required String language,
    String? conversationId,
  }) async {
    try {
      state = state.copyWith(connecting: true);
      // Use Live API endpoint for real-time audio support
      final url = ApiConfig.wsLiveAPI(sessionId, clientId, language);
      _channel = WebSocketChannel.connect(Uri.parse(url));
      _sub = _channel!.stream.listen(_onMessage, onDone: _onDone, onError: _onError);
      state = state.copyWith(
        connecting: false, 
        connected: true,
        currentConversationId: conversationId,
        language: language,
      );
    } catch (e) {
      state = state.copyWith(connecting: false, connected: false);
      rethrow;
    }
  }

  Future<void> createNewChat() async {
    final newConversationId = const Uuid().v4();
    final newConversation = Conversation(
      id: newConversationId,
      title: 'New Chat',
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
      messageCount: 0,
    );
    
    state = state.copyWith(
      conversations: [newConversation, ...state.conversations],
      currentConversationId: newConversationId,
      messages: [],
    );
  }

  void clearCurrentConversation() {
    state = state.copyWith(
      currentConversationId: null,
      messages: [],
    );
  }

  Future<void> loadConversations(String clientId) async {
    state = state.copyWith(loadingConversations: true);
    
    try {
      // TODO: Implement API call to load conversations
      // For now, we'll use mock data
      await Future.delayed(const Duration(milliseconds: 500));
      
      final mockConversations = [
        Conversation(
          id: 'conv1',
          title: 'Crop Disease Help',
          createdAt: DateTime.now().subtract(const Duration(days: 2)),
          updatedAt: DateTime.now().subtract(const Duration(hours: 3)),
          messageCount: 8,
          lastMessagePreview: 'Thank you for the help!',
        ),
        Conversation(
          id: 'conv2',
          title: 'Weather Advice',
          createdAt: DateTime.now().subtract(const Duration(days: 5)),
          updatedAt: DateTime.now().subtract(const Duration(days: 1)),
          messageCount: 12,
          lastMessagePreview: 'When should I plant?',
        ),
      ];
      
      state = state.copyWith(
        conversations: mockConversations,
        loadingConversations: false,
      );
    } catch (e) {
      state = state.copyWith(loadingConversations: false);
      // TODO: Handle error
    }
  }

  Future<void> loadMessages(String conversationId) async {
    state = state.copyWith(loadingMessages: true);
    
    try {
      // TODO: Implement API call to load messages for conversation
      // For now, we'll use mock data
      await Future.delayed(const Duration(milliseconds: 300));
      
      final mockMessages = [
        ChatMessage(
          id: 'msg1',
          role: 'user',
          type: 'text',
          text: 'Hello, I need help with my rice crop',
          createdAt: DateTime.now().subtract(const Duration(hours: 2)),
        ),
        ChatMessage(
          id: 'msg2',
          role: 'assistant',
          type: 'text',
          text: 'Hello! I\'d be happy to help with your rice crop. What specific issue are you facing?',
          createdAt: DateTime.now().subtract(const Duration(hours: 2)),
        ),
        ChatMessage(
          id: 'msg3',
          role: 'user',
          type: 'text',
          text: 'The leaves are turning yellow',
          createdAt: DateTime.now().subtract(const Duration(hours: 1)),
        ),
        ChatMessage(
          id: 'msg4',
          role: 'assistant',
          type: 'text',
          text: 'Yellow leaves in rice can indicate several issues. Let me help you diagnose this step by step.',
          createdAt: DateTime.now().subtract(const Duration(hours: 1)),
        ),
      ];
      
      state = state.copyWith(
        messages: mockMessages,
        currentConversationId: conversationId,
        loadingMessages: false,
      );
    } catch (e) {
      state = state.copyWith(loadingMessages: false);
      // TODO: Handle error
    }
  }

  Future<void> selectConversation(String conversationId) async {
    if (state.currentConversationId == conversationId) return;
    
    await loadMessages(conversationId);
  }

  void _onMessage(dynamic data) {
    try {
      final msg = jsonDecode(data as String) as Map<String, dynamic>;
      
      // Handle Live API message types
      final messageType = msg['type'] as String?;
      
      if (messageType == 'live_response') {
        // Live API response with chunks
        final chunk = msg['chunk'] as Map<String, dynamic>?;
        if (chunk != null) {
          final text = chunk['text'] as String?;
          final audio = chunk['audio'] as String?;
          final turnComplete = chunk['turn_complete'] as bool? ?? false;
          
          // Handle text response
          if (text != null && text.isNotEmpty) {
            final id = const Uuid().v4();
            final m = ChatMessage(
              id: id, 
              role: 'assistant', 
              type: 'text', 
              text: text, 
              createdAt: DateTime.now()
            );
            state = state.copyWith(
              messages: [...state.messages, m],
              typingText: '',
            );
            
            // Update conversation preview
            _updateConversationPreview(text);
          }
          
          // Handle audio response
          if (audio != null && audio.isNotEmpty) {
            final bytes = base64Decode(audio);
            final combined = [...state.audioBuffer, ...bytes];
            state = state.copyWith(audioBuffer: combined);
          }
          
          // Check if turn is complete
          if (turnComplete) {
            // Turn completed, no more chunks expected
            state = state.copyWith(typingText: '');
          }
        }
        return;
      }
      
      if (messageType == 'response') {
        // Direct response (fallback)
        final text = msg['text'] as String?;
        final audio = msg['audio'] as String?;
        
        if (text != null && text.isNotEmpty) {
          final id = const Uuid().v4();
          final m = ChatMessage(
            id: id, 
            role: 'assistant', 
            type: 'text', 
            text: text, 
            createdAt: DateTime.now()
          );
          state = state.copyWith(
            messages: [...state.messages, m],
            typingText: '',
          );
          
          // Update conversation preview
          _updateConversationPreview(text);
        }
        
        if (audio != null && audio.isNotEmpty) {
          final bytes = base64Decode(audio);
          final combined = [...state.audioBuffer, ...bytes];
          state = state.copyWith(audioBuffer: combined);
        }
        return;
      }
      
      if (messageType == 'error') {
        final errorMessage = msg['message'] as String? ?? msg['text'] as String? ?? 'Unknown error occurred';
        // Add error message to chat
        final id = const Uuid().v4();
        final m = ChatMessage(
          id: id, 
          role: 'assistant', 
          type: 'text', 
          text: 'Error: $errorMessage', 
          createdAt: DateTime.now()
        );
        state = state.copyWith(
          messages: [...state.messages, m],
          typingText: '',
        );
        return;
      }
      
      if (messageType == 'connected') {
        // Welcome message - no action needed
        return;
      }
      
    } catch (e) {
      // Log parse errors but don't crash
      // TODO: Replace with proper logging when logger is available
    }
  }

  void _updateConversationPreview(String lastMessage) {
    if (state.currentConversationId == null) return;
    
    final updatedConversations = state.conversations.map((conv) {
      if (conv.id == state.currentConversationId) {
        // Generate a title based on the first message if this is a new chat
        String title = conv.title;
        if (conv.title == 'New Chat' && conv.messageCount == 0) {
          title = _generateConversationTitle(lastMessage);
        }
        
        return conv.copyWith(
          title: title,
          updatedAt: DateTime.now(),
          messageCount: conv.messageCount + 1,
          lastMessagePreview: lastMessage.length > 50 
            ? '${lastMessage.substring(0, 50)}...' 
            : lastMessage,
        );
      }
      return conv;
    }).toList();
    
    state = state.copyWith(conversations: updatedConversations);
  }

  String _generateConversationTitle(String message) {
    // Simple title generation based on message content
    final lowerMessage = message.toLowerCase();
    
    if (lowerMessage.contains('crop') || lowerMessage.contains('plant')) {
      return 'Crop Advice';
    } else if (lowerMessage.contains('disease') || lowerMessage.contains('pest')) {
      return 'Plant Health';
    } else if (lowerMessage.contains('weather') || lowerMessage.contains('rain')) {
      return 'Weather Help';
    } else if (lowerMessage.contains('market') || lowerMessage.contains('price')) {
      return 'Market Info';
    } else if (lowerMessage.contains('soil') || lowerMessage.contains('fertilizer')) {
      return 'Soil & Nutrition';
    } else if (lowerMessage.contains('irrigation') || lowerMessage.contains('water')) {
      return 'Water Management';
    } else {
      return 'Farming Help';
    }
  }

  void _onDone() {
    state = state.copyWith(connected: false);
  }

  void _onError(Object e) {
    state = state.copyWith(connected: false);
    // Add error message to chat
    final id = const Uuid().v4();
    final m = ChatMessage(
      id: id, 
      role: 'assistant', 
      type: 'text', 
      text: 'Connection error: $e', 
      createdAt: DateTime.now()
    );
    state = state.copyWith(
      messages: [...state.messages, m],
      typingText: '',
    );
  }

  Future<void> sendText(String text) async {
    if (_channel == null) return;
    
    // Use the Live API WebSocket message format that matches the backend
    final payload = jsonEncode({
      'type': 'text',
      'content': text,
      'language': state.language,
    });
    
    _channel!.sink.add(payload);
    
    // Add user message to local state
    final id = const Uuid().v4();
    final m = ChatMessage(
      id: id, 
      role: 'user', 
      type: 'text', 
      text: text, 
      createdAt: DateTime.now()
    );
    state = state.copyWith(messages: [...state.messages, m]);
    
    // Update conversation preview
    _updateConversationPreview(text);
  }

  Future<void> sendImage(String imageBase64, String mimeType) async {
    if (_channel == null) return;
    
    // Use the new WebSocket message format that matches the backend
    final payload = jsonEncode({
      'type': 'request',
      'data': {
        'media_type': 'image',
        'content': imageBase64,
        'mime_type': mimeType
      },
      'message_id': const Uuid().v4(),
      'timestamp': DateTime.now().toIso8601String()
    });
    
    _channel!.sink.add(payload);
    
    // Add user message to local state
    final id = const Uuid().v4();
    final m = ChatMessage(
      id: id, 
      role: 'user', 
      type: 'image', 
      imageBase64: imageBase64, 
      createdAt: DateTime.now()
    );
    state = state.copyWith(messages: [...state.messages, m]);
    
    // Update conversation preview
    _updateConversationPreview('📷 Image sent');
  }

  Future<void> sendAudio(List<int> audioBytes, String mimeType) async {
    if (_channel == null) return;
    
    // Convert audio bytes to base64
    final audioBase64 = base64Encode(audioBytes);
    
    // Use the Live API WebSocket message format that matches the backend
    final payload = jsonEncode({
      'type': 'audio',
      'content': audioBase64,
      'language': state.language,
      'format': mimeType,
      'sample_rate': 24000, // Match the recording sample rate
    });
    
    _channel!.sink.add(payload);
    
    // Add user message to local state
    final id = const Uuid().v4();
    final m = ChatMessage(
      id: id, 
      role: 'user', 
      type: 'audio', 
      audioPath: null, // We don't store the path for now
      createdAt: DateTime.now()
    );
    state = state.copyWith(messages: [...state.messages, m]);
    
    // Update conversation preview
    _updateConversationPreview('🎤 Voice message sent');
  }

  @override
  void dispose() {
    _sub?.cancel();
    _channel?.sink.close();
    super.dispose();
  }
}

final chatControllerProvider = StateNotifierProvider<ChatController, ChatState>((ref) {
  return ChatController();
});


