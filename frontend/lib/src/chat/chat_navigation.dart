import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../state/chat_provider.dart';
import 'chat_list_screen.dart';
import 'chat_screen.dart';

class ChatNavigation extends ConsumerWidget {
  final String language;
  
  const ChatNavigation({super.key, required this.language});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final chat = ref.watch(chatControllerProvider);
    
    // If there's a current conversation, show the chat screen
    if (chat.currentConversationId != null) {
      return ChatScreen(language: language);
    }
    
    // Otherwise, show the chat list
    return ChatListScreen(language: language);
  }
}
