import 'package:flutter/material.dart';
import '../models/crop_cycle_models.dart';

class TaskCard extends StatelessWidget {
  final CropTask task;
  final VoidCallback? onTap;
  final VoidCallback? onMarkComplete;
  final VoidCallback? onMarkDelayed;
  final VoidCallback? onSkip;
  final VoidCallback? onAddPhotos;
  final VoidCallback? onRecordVoice;
  final VoidCallback? onAddNotes;

  const TaskCard({
    super.key,
    required this.task,
    this.onTap,
    this.onMarkComplete,
    this.onMarkDelayed,
    this.onSkip,
    this.onAddPhotos,
    this.onRecordVoice,
    this.onAddNotes,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isCompleted = task.status == 'completed';
    final isOverdue = _isOverdue();
    final priorityColor = _getPriorityColor(task.priority);
    final statusColor = _getStatusColor(task.status);

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      elevation: isCompleted ? 1 : 2,
      color: isCompleted ? Colors.grey.shade50 : null,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header with priority and status
              Row(
                children: [
                  // Priority indicator
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: priorityColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: priorityColor, width: 1),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          _getPriorityIcon(task.priority),
                          size: 16,
                          color: priorityColor,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          task.priority.toUpperCase(),
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: priorityColor,
                            fontWeight: FontWeight.bold,
                            fontSize: 10,
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  const Spacer(),
                  
                  // Status indicator
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: statusColor, width: 1),
                    ),
                    child: Text(
                      task.status.toUpperCase(),
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: statusColor,
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                      ),
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 12),
              
              // Task title and description
              Text(
                task.title,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  decoration: isCompleted ? TextDecoration.lineThrough : null,
                  color: isCompleted ? Colors.grey : null,
                ),
              ),
              
              if (task.description.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  task.description,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: isCompleted ? Colors.grey : null,
                  ),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              
              const SizedBox(height: 16),
              
              // Task details row
              Row(
                children: [
                  // Due date
                  Expanded(
                    child: _TaskDetailItem(
                      icon: Icons.calendar_today,
                      label: 'Due',
                      value: _formatDate(task.dueDate),
                      valueColor: isOverdue ? Colors.red : null,
                    ),
                  ),
                  
                  // Estimated time
                  Expanded(
                    child: _TaskDetailItem(
                      icon: Icons.access_time,
                      label: 'Estimated',
                      value: '${task.estimatedHours}h',
                    ),
                  ),
                  
                  // Notes count
                  Expanded(
                    child: _TaskDetailItem(
                      icon: Icons.note,
                      label: 'Notes',
                      value: task.notes?.isNotEmpty == true ? '1' : '0',
                    ),
                  ),
                ],
              ),
              
              // Overdue warning
              if (isOverdue && !isCompleted) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red.shade200),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.warning, color: Colors.red.shade700, size: 16),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'This task is overdue!',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: Colors.red.shade700,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              
              // Action buttons
              if (!isCompleted) ...[
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: onMarkComplete,
                        icon: const Icon(Icons.check, size: 16),
                        label: const Text('Complete'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 8),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: onMarkDelayed,
                        icon: const Icon(Icons.schedule, size: 16),
                        label: const Text('Delay'),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: onSkip,
                        icon: const Icon(Icons.skip_next, size: 16),
                        label: const Text('Skip'),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                        ),
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 12),
                
                // Secondary actions
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: onAddPhotos,
                        icon: const Icon(Icons.photo_camera, size: 16),
                        label: const Text('Photos'),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 6),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: onRecordVoice,
                        icon: const Icon(Icons.mic, size: 16),
                        label: const Text('Voice'),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 6),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: onAddNotes,
                        icon: const Icon(Icons.note_add, size: 16),
                        label: const Text('Notes'),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 6),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  bool _isOverdue() {
    final dueDate = task.dueDate;
    final now = DateTime.now();
    return dueDate.isBefore(now) && task.status != 'completed';
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final tomorrow = today.add(const Duration(days: 1));
    final taskDate = DateTime(date.year, date.month, date.day);
    
    if (taskDate == today) {
      return 'Today';
    } else if (taskDate == tomorrow) {
      return 'Tomorrow';
    } else if (taskDate.isBefore(today)) {
      final daysAgo = today.difference(taskDate).inDays;
      return '$daysAgo days ago';
    } else {
      final daysUntil = taskDate.difference(today).inDays;
      return 'In $daysUntil days';
    }
  }

  Color _getPriorityColor(String priority) {
    switch (priority.toLowerCase()) {
      case 'low':
        return Colors.green;
      case 'medium':
        return Colors.orange;
      case 'high':
        return Colors.red;
      case 'critical':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  IconData _getPriorityIcon(String priority) {
    switch (priority.toLowerCase()) {
      case 'low':
        return Icons.arrow_downward;
      case 'medium':
        return Icons.remove;
      case 'high':
        return Icons.arrow_upward;
      case 'critical':
        return Icons.priority_high;
      default:
        return Icons.circle;
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return Colors.blue;
      case 'in_progress':
        return Colors.orange;
      case 'completed':
        return Colors.green;
      case 'delayed':
        return Colors.red;
      case 'skipped':
        return Colors.grey;
      default:
        return Colors.grey;
    }
  }
}

class _TaskDetailItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color? valueColor;

  const _TaskDetailItem({
    required this.icon,
    required this.label,
    required this.value,
    this.valueColor,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Column(
      children: [
        Icon(icon, size: 16, color: Colors.grey),
        const SizedBox(height: 4),
        Text(
          label,
          style: theme.textTheme.bodySmall?.copyWith(
            color: Colors.grey,
            fontSize: 10,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: theme.textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.w500,
            color: valueColor ?? theme.textTheme.bodySmall?.color,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}
