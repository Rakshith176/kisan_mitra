import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../state/chat_provider.dart';
import '../state/client_provider.dart';

class ChatListScreen extends ConsumerStatefulWidget {
  final String language;
  const ChatListScreen({super.key, required this.language});

  @override
  ConsumerState<ChatListScreen> createState() => _ChatListScreenState();
}

class _ChatListScreenState extends ConsumerState<ChatListScreen> {
  @override
  void initState() {
    super.initState();
    // Load conversations when screen initializes
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadConversations();
    });
  }

  Future<void> _loadConversations() async {
    final clientIdAsync = ref.read(clientIdProvider);
    clientIdAsync.whenData((clientId) {
      ref.read(chatControllerProvider.notifier).loadConversations(clientId);
    });
  }

  @override
  Widget build(BuildContext context) {
    final chat = ref.watch(chatControllerProvider);
    final clientIdAsync = ref.watch(clientIdProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(
          widget.language == 'hi' ? 'चैट' : 
          widget.language == 'kn' ? 'ಚಾಟ್' : 'Chat',
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
        ),
        backgroundColor: Theme.of(context).colorScheme.surface,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadConversations,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: clientIdAsync.when(
        data: (clientId) => Column(
          children: [
            // New Chat Button
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              child: ElevatedButton.icon(
                onPressed: () => _createNewChat(clientId),
                icon: const Icon(Icons.add, size: 20),
                label: Text(
                  widget.language == 'hi' ? 'नई चैट शुरू करें' : 
                  widget.language == 'kn' ? 'ಹೊಸ ಚಾಟ್ ಪ್ರಾರಂಭಿಸಿ' : 'Start New Chat',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Theme.of(context).colorScheme.primary,
                  foregroundColor: Theme.of(context).colorScheme.onPrimary,
                  padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
            
            // Conversations List
            Expanded(
              child: chat.loadingConversations
                ? const Center(child: CircularProgressIndicator())
                : chat.conversations.isEmpty
                  ? _buildEmptyState()
                  : _buildConversationsList(clientId),
            ),
          ],
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => const Center(child: Text('Client not initialized')),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.chat_bubble_outline,
            size: 64,
            color: Colors.grey.withValues(alpha: 0.5),
          ),
          const SizedBox(height: 16),
          Text(
            widget.language == 'hi' ? 'कोई चैट नहीं' : 
            widget.language == 'kn' ? 'ಚಾಟ್ ಇಲ್ಲ' : 'No chats yet',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w500,
              color: Colors.grey.withValues(alpha: 0.7),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            widget.language == 'hi' ? 'नई चैट शुरू करने के लिए ऊपर दिए गए बटन पर टैप करें' : 
            widget.language == 'kn' ? 'ಹೊಸ ಚಾಟ್ ಪ್ರಾರಂಭಿಸಲು ಮೇಲಿನ ಬಟನ್ ಟ್ಯಾಪ್ ಮಾಡಿ' : 'Tap the button above to start a new chat',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.withValues(alpha: 0.6),
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildConversationsList(String clientId) {
    final chat = ref.watch(chatControllerProvider);
    
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: chat.conversations.length,
      itemBuilder: (context, index) {
        final conversation = chat.conversations[index];
        final isSelected = chat.currentConversationId == conversation.id;
        
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          elevation: isSelected ? 2 : 1,
          color: isSelected 
            ? Theme.of(context).colorScheme.primaryContainer.withValues(alpha: 0.1)
            : Theme.of(context).colorScheme.surface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: isSelected 
              ? BorderSide(
                  color: Theme.of(context).colorScheme.primary,
                  width: 2,
                )
              : BorderSide.none,
          ),
          child: InkWell(
            onTap: () => _selectConversation(conversation.id, clientId),
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  // Conversation Icon
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.primaryContainer,
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: Icon(
                      Icons.chat_bubble,
                      color: Theme.of(context).colorScheme.onPrimaryContainer,
                      size: 24,
                    ),
                  ),
                  
                  const SizedBox(width: 16),
                  
                  // Conversation Details
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          conversation.title,
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Theme.of(context).colorScheme.onSurface,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        
                        if (conversation.lastMessagePreview != null) ...[
                          const SizedBox(height: 4),
                          Text(
                            conversation.lastMessagePreview!,
                            style: TextStyle(
                              fontSize: 14,
                              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                        
                        const SizedBox(height: 8),
                        
                        Row(
                          children: [
                            Icon(
                              Icons.message,
                              size: 14,
                              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5),
                            ),
                            const SizedBox(width: 4),
                            Text(
                              '${conversation.messageCount} messages',
                              style: TextStyle(
                                fontSize: 12,
                                color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5),
                              ),
                            ),
                            
                            const Spacer(),
                            
                            Text(
                              _formatDate(conversation.updatedAt),
                              style: TextStyle(
                                fontSize: 12,
                                color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  
                  // Arrow Icon
                  Icon(
                    Icons.chevron_right,
                    color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.3),
                    size: 20,
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);
    
    if (difference.inDays == 0) {
      return DateFormat('HH:mm').format(date);
    } else if (difference.inDays == 1) {
      return widget.language == 'hi' ? 'कल' : 
             widget.language == 'kn' ? 'ನಿನ್ನೆ' : 'Yesterday';
    } else if (difference.inDays < 7) {
      return DateFormat('EEE').format(date);
    } else {
      return DateFormat('MMM d').format(date);
    }
  }

  void _createNewChat(String clientId) {
    ref.read(chatControllerProvider.notifier).createNewChat();
  }

  void _selectConversation(String conversationId, String clientId) {
    ref.read(chatControllerProvider.notifier).selectConversation(conversationId);
  }
}
