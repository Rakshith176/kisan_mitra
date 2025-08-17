import 'package:flutter/material.dart';
import 'formatters.dart';

class SeverityChip extends StatelessWidget {
  final String severity; // high|med|low
  const SeverityChip({super.key, required this.severity});
  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    String label;
    switch (severity) {
      case 'high':
        bg = Colors.red.shade50; fg = Colors.red.shade700; label = 'High';
        break;
      case 'med':
        bg = Colors.orange.shade50; fg = Colors.orange.shade700; label = 'Medium';
        break;
      default:
        bg = Colors.green.shade50; fg = Colors.green.shade700; label = 'Low';
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(16)),
      child: Text(label, style: TextStyle(color: fg, fontWeight: FontWeight.w600)),
    );
  }
}

class DateRangeChip extends StatelessWidget {
  final DateTime? start;
  final DateTime? end;
  const DateRangeChip({super.key, this.start, this.end});
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(color: Theme.of(context).colorScheme.surfaceVariant, borderRadius: BorderRadius.circular(16)),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        const Icon(Icons.schedule, size: 16), const SizedBox(width: 6),
        Text(formatDateRange(start, end)),
      ]),
    );
  }
}

class FreshnessChip extends StatelessWidget {
  final DateTime? date;
  const FreshnessChip({super.key, this.date});
  @override
  Widget build(BuildContext context) {
    final label = date == null ? '—' : (DateTime.now().difference(date!).inDays == 0 ? 'Today' : formatDateShort(date!));
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(color: Colors.blue.shade50, borderRadius: BorderRadius.circular(16)),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        const Icon(Icons.event_available, size: 16, color: Colors.blue), const SizedBox(width: 6),
        Text(label, style: const TextStyle(color: Colors.blue)),
      ]),
    );
  }
}


