import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'markdown_message_widget.dart';

class AgriculturalAdviceWidget extends StatelessWidget {
  final String text;
  final bool isUser;

  const AgriculturalAdviceWidget({
    super.key,
    required this.text,
    required this.isUser,
  });

  @override
  Widget build(BuildContext context) {
    if (isUser) {
      // User messages don't need special formatting
      return MarkdownMessageWidget(
        text: text,
        isUser: true,
      );
    }

    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    // Enhanced styling for agricultural advice
    final adviceStyle = MarkdownStyleSheet(
      textScaleFactor: 1.0,
      h1: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: theme.primaryColor,
        height: 1.3,
      ),
      h2: TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.bold,
        color: theme.primaryColor,
        height: 1.3,
      ),
      h3: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.bold,
        color: theme.primaryColor,
        height: 1.3,
      ),
      p: TextStyle(
        fontSize: 16,
        height: 1.6,
        color: isDark ? Colors.white : Colors.black87,
      ),
      strong: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.bold,
        color: theme.primaryColor,
        height: 1.6,
      ),
      em: TextStyle(
        fontSize: 16,
        fontStyle: FontStyle.italic,
        color: isDark ? Colors.white70 : Colors.black54,
        height: 1.6,
      ),
      code: TextStyle(
        fontFamily: 'monospace',
        fontSize: 14,
        backgroundColor: theme.primaryColor.withValues(alpha: 0.1),
        color: theme.primaryColor,
      ),
      codeblockDecoration: BoxDecoration(
        color: theme.primaryColor.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: theme.primaryColor.withValues(alpha: 0.2),
        ),
      ),
      blockquote: TextStyle(
        fontSize: 16,
        fontStyle: FontStyle.italic,
        color: theme.primaryColor.withValues(alpha: 0.8),
        height: 1.6,
      ),
      blockquoteDecoration: BoxDecoration(
        border: Border(
          left: BorderSide(
            color: theme.primaryColor.withValues(alpha: 0.5),
            width: 4,
          ),
        ),
        color: theme.primaryColor.withValues(alpha: 0.05),
      ),
      listBullet: TextStyle(
        fontSize: 16,
        color: theme.primaryColor,
        height: 1.6,
      ),
      tableHead: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.bold,
        backgroundColor: theme.primaryColor.withValues(alpha: 0.1),
        color: theme.primaryColor,
      ),
      tableBody: TextStyle(
        fontSize: 16,
        height: 1.6,
        color: isDark ? Colors.white : Colors.black87,
      ),
      horizontalRuleDecoration: BoxDecoration(
        border: Border(
          top: BorderSide(
            color: theme.primaryColor.withValues(alpha: 0.3),
            width: 2,
          ),
        ),
      ),
    );

    return Container(
      decoration: BoxDecoration(
        color: theme.primaryColor.withValues(alpha: 0.02),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: theme.primaryColor.withValues(alpha: 0.1),
          width: 1,
        ),
      ),
      padding: const EdgeInsets.all(16),
      child: MarkdownBody(
        data: text,
        styleSheet: adviceStyle,
        shrinkWrap: true,
        softLineBreak: true,
        selectable: true,
        onTapLink: (text, url, title) {
          if (url != null) {
            debugPrint('Link tapped: $url');
          }
        },
      ),
    );
  }
}
