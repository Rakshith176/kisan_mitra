import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

class MarkdownMessageWidget extends StatelessWidget {
  final String text;
  final bool isUser;
  final TextStyle? textStyle;

  const MarkdownMessageWidget({
    super.key,
    required this.text,
    required this.isUser,
    this.textStyle,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    
    // Default text style
    final defaultStyle = textStyle ?? TextStyle(
      fontSize: 16,
      height: 1.5,
      color: isUser 
        ? Colors.white 
        : (isDark ? Colors.white : Colors.black87),
    );

    // Markdown style configuration
    final markdownStyle = MarkdownStyleSheet(
      textScaleFactor: 1.0,
      h1: defaultStyle.copyWith(
        fontSize: 22,
        fontWeight: FontWeight.bold,
        color: isUser ? Colors.white : theme.primaryColor,
      ),
      h2: defaultStyle.copyWith(
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: isUser ? Colors.white : theme.primaryColor,
      ),
      h3: defaultStyle.copyWith(
        fontSize: 18,
        fontWeight: FontWeight.bold,
        color: isUser ? Colors.white : theme.primaryColor,
      ),
      h4: defaultStyle.copyWith(
        fontSize: 16,
        fontWeight: FontWeight.bold,
        color: isUser ? Colors.white : theme.primaryColor,
      ),
      h5: defaultStyle.copyWith(
        fontSize: 14,
        fontWeight: FontWeight.bold,
        color: isUser ? Colors.white : theme.primaryColor,
      ),
      h6: defaultStyle.copyWith(
        fontSize: 12,
        fontWeight: FontWeight.bold,
        color: isUser ? Colors.white : theme.primaryColor,
      ),
      p: defaultStyle,
      strong: defaultStyle.copyWith(fontWeight: FontWeight.bold),
      em: defaultStyle.copyWith(fontStyle: FontStyle.italic),
      code: TextStyle(
        fontFamily: 'monospace',
        fontSize: 14,
        backgroundColor: isUser 
          ? Colors.white.withValues(alpha: 0.2)
          : Colors.grey.withValues(alpha: 0.1),
        color: isUser ? Colors.white : Colors.black87,
      ),
      codeblockDecoration: BoxDecoration(
        color: isUser 
          ? Colors.white.withValues(alpha: 0.1)
          : Colors.grey.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isUser 
            ? Colors.white.withValues(alpha: 0.3)
            : Colors.grey.withValues(alpha: 0.3),
        ),
      ),
      blockquote: defaultStyle.copyWith(
        fontStyle: FontStyle.italic,
        color: isUser 
          ? Colors.white.withValues(alpha: 0.8)
          : Colors.grey.shade600,
      ),
      blockquoteDecoration: BoxDecoration(
        border: Border(
          left: BorderSide(
            color: isUser 
              ? Colors.white.withValues(alpha: 0.5)
              : theme.primaryColor.withValues(alpha: 0.5),
            width: 4,
          ),
        ),
      ),
      listBullet: defaultStyle.copyWith(
        color: isUser ? Colors.white : theme.primaryColor,
      ),
      tableHead: defaultStyle.copyWith(
        fontWeight: FontWeight.bold,
        backgroundColor: isUser 
          ? Colors.white.withValues(alpha: 0.2)
          : theme.primaryColor.withValues(alpha: 0.1),
      ),
      tableBody: defaultStyle,
      horizontalRuleDecoration: BoxDecoration(
        border: Border(
          top: BorderSide(
            color: isUser 
              ? Colors.white.withValues(alpha: 0.3)
              : Colors.grey.withValues(alpha: 0.3),
            width: 1,
          ),
        ),
      ),
    );

    // Check if text contains markdown
    final hasMarkdown = _containsMarkdown(text);
    
    if (!hasMarkdown) {
      // Return plain text for non-markdown content
      return Text(
        text,
        style: defaultStyle,
        textAlign: isUser ? TextAlign.right : TextAlign.left,
      );
    }

    return MarkdownBody(
      data: text,
      styleSheet: markdownStyle,
      shrinkWrap: true,
      softLineBreak: true,
      selectable: true,
      onTapLink: (text, url, title) {
        // Handle link taps if needed
        if (url != null) {
          // You can add URL launcher here if needed
          debugPrint('Link tapped: $url');
        }
      },
    );
  }

  bool _containsMarkdown(String text) {
    // Simple check for common markdown patterns
    final markdownPatterns = [
      RegExp(r'^#{1,6}\s', multiLine: true), // Headers
      RegExp(r'\*\*.*\*\*'), // Bold
      RegExp(r'\*.*\*'), // Italic
      RegExp(r'`.*`'), // Inline code
      RegExp(r'^```', multiLine: true), // Code blocks
      RegExp(r'^>', multiLine: true), // Blockquotes
      RegExp(r'^[-*+]\s', multiLine: true), // Lists
      RegExp(r'^\d+\.\s', multiLine: true), // Numbered lists
      RegExp(r'\[.*\]\(.*\)'), // Links
      RegExp(r'^\|.*\|$', multiLine: true), // Tables
      RegExp(r'^---$', multiLine: true), // Horizontal rules
    ];

    return markdownPatterns.any((pattern) => pattern.hasMatch(text));
  }
}
