import 'package:flutter/material.dart';
import '../models/crop_cycle_models.dart';

class CropCycleCard extends StatelessWidget {
  final CropCycle cycle;
  final VoidCallback? onTap;
  final VoidCallback? onViewDetails;
  final VoidCallback? onMarkComplete;
  final VoidCallback? onAddNote;

  const CropCycleCard({
    super.key,
    required this.cycle,
    this.onTap,
    this.onViewDetails,
    this.onMarkComplete,
    this.onAddNote,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isActive = cycle.status == 'active';
    final isCompleted = cycle.status == 'completed';
    
    // Calculate progress
    final progress = _calculateProgress();
    final daysSincePlanting = _calculateDaysSincePlanting();
    final daysToHarvest = _calculateDaysToHarvest();
    
    // Get crop name in current language (default to English)
    final cropName = cycle.crop?.nameEn ?? 'Unknown Crop';
    
    // Get risk level (this would come from backend risk assessment)
    final riskLevel = _getRiskLevel();
    
    // Get today's tasks count
    final todayTasksCount = _getTodayTasksCount();

    return Card(
      margin: const EdgeInsets.all(12),
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header with crop name, season, and status
              Row(
                children: [
                  Icon(
                    isActive ? Icons.grass : Icons.grass_outlined,
                    color: isActive ? Colors.green : Colors.grey,
                    size: 24,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '$cropName - ${cycle.season} Season',
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          cycle.status.toUpperCase(),
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: _getStatusColor(cycle.status),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 12),
              
              // Location and area info
              Row(
                children: [
                  const Icon(Icons.location_on, size: 16, color: Colors.grey),
                  const SizedBox(width: 4),
                  Text(
                    'Pincode: ${cycle.pincode} | Area: ${cycle.areaAcres} acres',
                    style: theme.textTheme.bodySmall?.copyWith(color: Colors.grey),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              // Progress bar
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Progress',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      Text(
                        '${(progress * 100).round()}%',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.green,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  LinearProgressIndicator(
                    value: progress,
                    backgroundColor: Colors.grey.shade200,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      isCompleted ? Colors.green : Colors.blue,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              // Current stage and timing info
              Row(
                children: [
                  Expanded(
                    child: _InfoItem(
                      icon: Icons.grass,
                      label: 'Current Stage',
                      value: _getCurrentStage(),
                    ),
                  ),
                  Expanded(
                    child: _InfoItem(
                      icon: Icons.calendar_today,
                      label: 'Days Since Planting',
                      value: '$daysSincePlanting',
                    ),
                  ),
                  Expanded(
                    child: _InfoItem(
                      icon: Icons.agriculture,
                      label: 'Days to Harvest',
                      value: '$daysToHarvest',
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              // Risk level and today's tasks
              Row(
                children: [
                  Expanded(
                    child: _InfoItem(
                      icon: Icons.warning,
                      label: 'Risk Level',
                      value: riskLevel,
                      valueColor: _getRiskColor(riskLevel),
                    ),
                  ),
                  Expanded(
                    child: _InfoItem(
                      icon: Icons.task,
                      label: "Today's Tasks",
                      value: '$todayTasksCount pending',
                      valueColor: todayTasksCount > 0 ? Colors.orange : Colors.green,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              // Action buttons
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: onViewDetails,
                      icon: const Icon(Icons.visibility, size: 16),
                      label: const Text('View Details'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  if (isActive) ...[
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: onMarkComplete,
                        icon: const Icon(Icons.check, size: 16),
                        label: const Text('Mark Complete'),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                  ],
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: onAddNote,
                      icon: const Icon(Icons.note_add, size: 16),
                      label: const Text('Add Note'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  double _calculateProgress() {
    if (cycle.growthStages == null || cycle.growthStages!.isEmpty) {
      // Fallback: calculate based on time
      final totalDays = cycle.crop?.growthDurationDays ?? 120;
      final daysSincePlanting = DateTime.now().difference(cycle.startDate).inDays;
      return (daysSincePlanting / totalDays).clamp(0.0, 1.0);
    }
    
    // Calculate based on completed growth stages
    final completedStages = cycle.growthStages!
        .where((stage) => stage.actualStartDate != null)
        .length;
    final totalStages = cycle.growthStages!.length;
    
    return totalStages > 0 ? completedStages / totalStages : 0.0;
  }

  int _calculateDaysSincePlanting() {
    return DateTime.now().difference(cycle.startDate).inDays;
  }

  int _calculateDaysToHarvest() {
    final harvestDate = cycle.actualHarvestDate ?? cycle.plannedHarvestDate;
    return harvestDate.difference(DateTime.now()).inDays;
  }

  String _getCurrentStage() {
    if (cycle.growthStages == null || cycle.growthStages!.isEmpty) {
      return 'Planning';
    }
    
    // Find the current stage based on progress
    final currentStage = cycle.growthStages!
        .where((stage) => stage.actualStartDate == null)
        .firstOrNull;
    
    return currentStage?.stageName ?? 'Unknown';
  }

  String _getRiskLevel() {
    // This would come from backend risk assessment
    // For now, return a placeholder
    return 'Medium';
  }

  Color _getRiskColor(String riskLevel) {
    switch (riskLevel.toLowerCase()) {
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

  int _getTodayTasksCount() {
    if (cycle.tasks == null) return 0;
    
    final today = DateTime.now();
    final startOfDay = DateTime(today.year, today.month, today.day);
    final endOfDay = startOfDay.add(const Duration(days: 1));
    
    return cycle.tasks!.where((task) {
      final dueDate = task.dueDate;
      return dueDate.isAfter(startOfDay) && 
             dueDate.isBefore(endOfDay) && 
             task.status != 'completed';
    }).length;
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'planned':
        return Colors.blue;
      case 'active':
        return Colors.green;
      case 'completed':
        return Colors.green.shade700;
      case 'failed':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}

class _InfoItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color? valueColor;

  const _InfoItem({
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
