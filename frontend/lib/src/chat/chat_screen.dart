import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../state/chat_provider.dart';
import '../state/client_provider.dart';
import 'widgets/media_input_widget.dart';
import 'widgets/markdown_message_widget.dart';
import 'widgets/agricultural_advice_widget.dart';

class ChatScreen extends ConsumerStatefulWidget {
  final String language;
  const ChatScreen({super.key, required this.language});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final _controller = TextEditingController();
  late final String _sessionId;

  @override
  void initState() {
    super.initState();
    _sessionId = const Uuid().v4();
  }

  @override
  Widget build(BuildContext context) {
    final chat = ref.watch(chatControllerProvider);
    final clientIdAsync = ref.watch(clientIdProvider);
    
    // Get current conversation info
    final currentConversation = chat.currentConversationId != null
        ? chat.conversations.firstWhere(
            (conv) => conv.id == chat.currentConversationId,
            orElse: () => Conversation(
              id: chat.currentConversationId!,
              title: 'New Chat',
              createdAt: DateTime.now(),
              updatedAt: DateTime.now(),
              messageCount: 0,
            ),
          )
        : null;
    
    return clientIdAsync.when(
      data: (clientId) => Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () {
              // Clear current conversation and return to list
              ref.read(chatControllerProvider.notifier).clearCurrentConversation();
            },
          ),
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                currentConversation?.title ?? 'New Chat',
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
              ),
              if (currentConversation != null) ...[
                const SizedBox(height: 2),
                Text(
                  '${currentConversation.messageCount} messages',
                  style: TextStyle(
                    fontSize: 12,
                    color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                  ),
                ),
              ],
            ],
          ),
          backgroundColor: Theme.of(context).colorScheme.surface,
          elevation: 0,
          actions: [
            if (chat.connected)
              IconButton(
                icon: const Icon(Icons.refresh),
                onPressed: () => _reconnect(clientId),
                tooltip: 'Reconnect',
              ),
          ],
        ),
        body: Column(
          children: [
            // Connection status indicator
            if (chat.connecting || !chat.connected)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
                color: chat.connecting 
                  ? Colors.orange.withValues(alpha: 0.2)
                  : Colors.red.withValues(alpha: 0.2),
                child: Row(
                  children: [
                    Icon(
                      chat.connecting ? Icons.sync : Icons.error,
                      size: 16,
                      color: chat.connecting ? Colors.orange : Colors.red,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        chat.connecting ? 'Connecting...' : 'Disconnected',
                        style: TextStyle(
                          color: chat.connecting ? Colors.orange : Colors.red,
                          fontSize: 12,
                        ),
                      ),
                    ),
                    if (!chat.connecting && !chat.connected)
                      TextButton(
                        onPressed: () => _reconnect(clientId),
                        child: const Text('Reconnect', style: TextStyle(fontSize: 12)),
                      ),
                  ],
                ),
              ),
            
            // Messages List
            Expanded(
              child: chat.loadingMessages
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: chat.messages.length + (chat.typingText.isNotEmpty ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index >= chat.messages.length) {
                        // typing indicator
                        return Align(
                          alignment: Alignment.centerLeft,
                          child: Container(
                            padding: const EdgeInsets.all(12),
                            margin: const EdgeInsets.only(bottom: 8),
                            decoration: BoxDecoration(
                              color: Theme.of(context).colorScheme.surfaceContainerHighest,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(chat.typingText, style: const TextStyle(fontSize: 16, height: 1.5)),
                          ),
                        );
                      }
                      final m = chat.messages[index];
                      final isUser = m.role == 'user';
                      return Align(
                        alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: m.role == 'user' 
                              ? Theme.of(context).primaryColor 
                              : Colors.grey.shade100,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: _buildMessageContent(m),
                        ),
                      );
                    },
                  ),
            ),
            
            // Input Area
            SafeArea(
              top: false,
              child: Padding(
                padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
                child: Column(
                  children: [
                    // Media input row
                    Row(
                      children: [
                        MediaInputWidget(
                          clientId: clientId,
                          sessionId: _sessionId,
                          language: widget.language,
                        ),
                        const Spacer(),
                      ],
                    ),
                    const SizedBox(height: 8),
                    // Text input row
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _controller,
                            minLines: 1,
                            maxLines: 5,
                            decoration: InputDecoration(
                              hintText: widget.language == 'hi' ? 'संदेश लिखें...' :
                                       widget.language == 'kn' ? 'ಸಂದೇಶ ಬರೆಯಿರಿ...' : 'Type a message…',
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                            ),
                            onSubmitted: (_) => _send(clientId),
                          ),
                        ),
                        const SizedBox(width: 8),
                        IconButton(
                          icon: const Icon(Icons.send),
                          onPressed: () => _send(clientId),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            )
          ],
        ),
      ),
      loading: () => const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      ),
      error: (_, __) => const Scaffold(
        body: Center(child: Text('Client not initialized')),
      ),
    );
  }

  Widget _buildMessageContent(ChatMessage message) {
    switch (message.type) {
      case 'text':
        // Use agricultural advice widget for AI responses, markdown widget for user messages
        if (message.role == 'assistant') {
          return AgriculturalAdviceWidget(
            text: message.text ?? '',
            isUser: false,
          );
        } else {
          return MarkdownMessageWidget(
            text: message.text ?? '',
            isUser: true,
          );
        }
      
      case 'image':
        if (message.imageBase64 != null) {
          try {
            final bytes = base64Decode(message.imageBase64!);
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.memory(
                    bytes,
                    width: 200,
                    height: 200,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(
                        width: 200,
                        height: 200,
                        color: Colors.grey.withValues(alpha: 0.3),
                        child: const Icon(Icons.broken_image, size: 48, color: Colors.grey),
                      );
                    },
                  ),
                ),
                if (message.text?.isNotEmpty == true) ...[
                  const SizedBox(height: 8),
                  if (message.role == 'assistant')
                    AgriculturalAdviceWidget(
                      text: message.text!,
                      isUser: false,
                    )
                  else
                    MarkdownMessageWidget(
                      text: message.text!,
                      isUser: true,
                    ),
                ],
              ],
            );
          } catch (e) {
            return const Text('Error displaying image', style: TextStyle(color: Colors.red));
          }
        }
        return const Text('Image message', style: TextStyle(fontStyle: FontStyle.italic));
      
      case 'audio':
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.mic, color: Colors.blue),
            const SizedBox(width: 8),
            const Text('Voice message', style: TextStyle(fontStyle: FontStyle.italic)),
          ],
        );
      
      default:
        if (message.role == 'assistant') {
          return AgriculturalAdviceWidget(
            text: message.text ?? 'Unknown message type',
            isUser: false,
          );
        } else {
          return MarkdownMessageWidget(
            text: message.text ?? 'Unknown message type',
            isUser: true,
          );
        }
    }
  }

  Future<void> _send(String clientId) async {
    if (_controller.text.trim().isEmpty) return;
    
    // Ensure connection with current conversation ID
    final chat = ref.read(chatControllerProvider);
    await ref.read(chatControllerProvider.notifier).connect(
          sessionId: _sessionId,
          clientId: clientId,
          language: widget.language,
          conversationId: chat.currentConversationId,
        );
    await ref.read(chatControllerProvider.notifier).sendText(_controller.text.trim());
    _controller.clear();
  }

  Future<void> _reconnect(String clientId) async {
    final chat = ref.read(chatControllerProvider);
    await ref.read(chatControllerProvider.notifier).connect(
          sessionId: _sessionId,
          clientId: clientId,
          language: widget.language,
          conversationId: chat.currentConversationId,
        );
  }
}


