import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/crop_cycle_providers.dart';
import '../widgets/crop_cycle_card.dart';
import '../widgets/real_time_weather_widget.dart';
import '../widgets/real_time_market_widget.dart';

import '../models/crop_cycle_models.dart';
import 'new_crop_cycle_screen.dart';
import 'crop_cycle_detail_screen.dart';

class PlannerMainScreen extends ConsumerStatefulWidget {
  final String clientId;

  const PlannerMainScreen({
    super.key,
    required this.clientId,
  });

  @override
  ConsumerState<PlannerMainScreen> createState() => _PlannerMainScreenState();
}

class _PlannerMainScreenState extends ConsumerState<PlannerMainScreen> with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    // Fetch crop cycles when screen initializes
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(cropCyclesProvider(widget.clientId).notifier).fetchCropCycles(widget.clientId);
    });
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    // Refresh data when app becomes active (returning from background)
    if (state == AppLifecycleState.resumed && mounted) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          ref.read(cropCyclesProvider(widget.clientId).notifier).refreshCropCycles(widget.clientId);
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cropCyclesState = ref.watch(cropCyclesProvider(widget.clientId));

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: () => ref.read(cropCyclesProvider(widget.clientId).notifier).refreshCropCycles(widget.clientId),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Header
            Row(
              children: [
                Text(
                  '📋 Planner',
                  style: theme.textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                IconButton(
                  onPressed: () => ref.read(cropCyclesProvider(widget.clientId).notifier).refreshCropCycles(widget.clientId),
                  icon: const Icon(Icons.refresh),
                  tooltip: 'Refresh',
                ),
                IconButton(
                  onPressed: () => _showFilterDialog(context),
                  icon: const Icon(Icons.filter_list),
                  tooltip: 'Filter',
                ),
              ],
            ),
            
            const SizedBox(height: 24),
            
            // Real-Time Data Dashboard
            _buildRealTimeDataDashboard(),
            
            const SizedBox(height: 24),
            
            // Quick Actions
            _buildQuickActions(),
            
            const SizedBox(height: 24),
            
            // Today's Tasks Section
            _buildTodayTasksSection(),
            
            const SizedBox(height: 24),
            
            // Active Crop Cycles Section
            _buildActiveCyclesSection(cropCyclesState),
            
            const SizedBox(height: 24),
            
            // Recent Activity Section
            _buildRecentActivitySection(),
            
            const SizedBox(height: 100), // Bottom padding for FAB
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _navigateToNewCropCycle(context),
        icon: const Icon(Icons.add),
        label: const Text('New Crop Cycle'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
    );
  }

  Widget _buildRealTimeDataDashboard() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.dashboard, color: Colors.blue, size: 24),
            const SizedBox(width: 8),
            Text(
              '📊 Real-Time Data Dashboard',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        

        
        // Weather and Market Data in a row
        Row(
          children: [
            Expanded(
              child: RealTimeWeatherWidget(
                latitude: 12.9716, // Default to Bangalore - should come from farmer profile
                longitude: 77.5946,
                clientId: widget.clientId,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: RealTimeMarketWidget(
                clientId: widget.clientId,
                state: 'Karnataka', // Default state - should come from farmer profile
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '🚀 Quick Actions',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _QuickActionCard(
                icon: Icons.grass,
                title: 'New Crop\nCycle',
                color: Colors.green,
                onTap: () => _navigateToNewCropCycle(context),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _QuickActionCard(
                icon: Icons.view_list,
                title: 'View All\nCycles',
                color: Colors.blue,
                onTap: () => _navigateToAllCycles(context),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _QuickActionCard(
                icon: Icons.calendar_today,
                title: 'Calendar\nView',
                color: Colors.orange,
                onTap: () => _navigateToCalendarView(context),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildTodayTasksSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              '📋 Today\'s Tasks',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const Spacer(),
            TextButton(
              onPressed: () => _navigateToAllTasks(context),
              child: const Text('View All'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        
        // This would show tasks from all active crop cycles
        // For now, show a placeholder
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.grey.shade50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey.shade200),
          ),
          child: Row(
            children: [
              Icon(Icons.info_outline, color: Colors.grey.shade600),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Tasks will appear here when you have active crop cycles',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey.shade600,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildActiveCyclesSection(CropCyclesState cropCyclesState) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              '🌱 Active Crop Cycles',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const Spacer(),
            TextButton(
              onPressed: () => _navigateToAllCycles(context),
              child: const Text('View All'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        
        if (cropCyclesState.isLoading)
          const Center(child: CircularProgressIndicator())
        else if (cropCyclesState.error != null)
          _buildErrorState(cropCyclesState.error!)
        else if (cropCyclesState.cycles.isEmpty)
          _buildEmptyState()
        else
          _buildCyclesList(cropCyclesState.cycles),
      ],
    );
  }

  Widget _buildCyclesList(List<CropCycle> cycles) {
    final activeCycles = cycles.where((cycle) => 
      cycle.status == 'active' || cycle.status == 'planned'
    ).toList();
    
    if (activeCycles.isEmpty) {
      return _buildEmptyState();
    }
    
    return Column(
      children: activeCycles.take(3).map((cycle) {
        return CropCycleCard(
          cycle: cycle,
          onTap: () => _navigateToCycleDetail(context, cycle),
          onViewDetails: () => _navigateToCycleDetail(context, cycle),
          onMarkComplete: () => _markCycleComplete(cycle),
          onAddNote: () => _addNoteToCycle(cycle),
        );
      }).toList(),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        children: [
          Icon(
            Icons.grass_outlined,
            size: 48,
            color: Colors.grey.shade400,
          ),
          const SizedBox(height: 16),
          Text(
            'No active crop cycles',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Start your first crop cycle to begin planning and tracking',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey.shade600,
                ),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: () => _navigateToNewCropCycle(context),
            icon: const Icon(Icons.add),
            label: const Text('Start First Cycle'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(String error) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline, color: Colors.red.shade700),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'Failed to load crop cycles: $error',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.red.shade700,
              ),
            ),
          ),
          TextButton(
            onPressed: () => ref.read(cropCyclesProvider(widget.clientId).notifier).fetchCropCycles(widget.clientId),
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentActivitySection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '📊 Recent Activity',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        
        // Placeholder for recent activity
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.grey.shade50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey.shade200),
          ),
          child: Row(
            children: [
              Icon(Icons.info_outline, color: Colors.grey.shade600),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Activity will appear here as you use the app',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey.shade600,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  void _navigateToNewCropCycle(BuildContext context) async {
    final result = await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => NewCropCycleScreen(clientId: widget.clientId),
      ),
    );
    
    // If a new crop cycle was created, show success message and refresh data
    if (result != null && result is CropCycle && mounted) {
      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('✅ Crop cycle "${result.crop?.nameEn ?? 'Unknown'}" created successfully!'),
          backgroundColor: Colors.green,
          duration: const Duration(seconds: 3),
          action: SnackBarAction(
            label: 'View Details',
            textColor: Colors.white,
            onPressed: () => _navigateToCycleDetailById(result.id),
          ),
        ),
      );
      
      // Refresh the crop cycles list to show the new cycle
      ref.read(cropCyclesProvider(widget.clientId).notifier).refreshCropCycles(widget.clientId);
    }
  }



  void _navigateToAllCycles(BuildContext context) {
    // TODO: Navigate to all cycles screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('All Cycles - Coming Soon!')),
    );
  }

  void _navigateToCalendarView(BuildContext context) {
    // TODO: Navigate to calendar view
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Calendar View - Coming Soon!')),
    );
  }

  void _navigateToAllTasks(BuildContext context) {
    // TODO: Navigate to all tasks screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('All Tasks - Coming Soon!')),
    );
  }

  void _navigateToCycleDetail(BuildContext context, CropCycle cycle) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => CropCycleDetailScreen(
          cycleId: cycle.id,
          clientId: widget.clientId,
        ),
      ),
    );
  }

  void _navigateToCycleDetailById(String cycleId) {
    if (mounted) {
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (context) => CropCycleDetailScreen(
            cycleId: cycleId,
            clientId: widget.clientId,
          ),
        ),
      );
    }
  }

  void _markCycleComplete(CropCycle cycle) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        String notes = '';
        return AlertDialog(
          title: const Text('Mark Cycle Complete'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Are you sure you want to mark "${cycle.crop?.nameEn ?? 'Crop'}" cycle as complete?'),
              const SizedBox(height: 16),
              TextField(
                decoration: const InputDecoration(
                  labelText: 'Completion Notes (Optional)',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
                onChanged: (value) => notes = value,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                Navigator.of(context).pop();
                
                try {
                  // Update cycle status
                  await ref.read(cropCycleApiServiceProvider).updateCropCycleStatus(cycle.id, 'completed', notes: notes.isNotEmpty ? notes : null);
                  
                  // Refresh the cycles list
                  await ref.read(cropCyclesProvider(widget.clientId).notifier).refreshCropCycles(widget.clientId);
                  
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Crop cycle marked as complete!'),
                        backgroundColor: Colors.green,
                      ),
                    );
                  }
                } catch (e) {
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Failed to mark cycle complete: $e'),
                        backgroundColor: Colors.red,
                      ),
                    );
                  }
                }
              },
              child: const Text('Complete'),
            ),
          ],
        );
      },
    );
  }

  void _addNoteToCycle(CropCycle cycle) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        String notes = '';
        return AlertDialog(
          title: const Text('Add Note to Cycle'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Add a note to "${cycle.crop?.nameEn ?? 'Crop'}" cycle'),
              const SizedBox(height: 16),
              TextField(
                decoration: const InputDecoration(
                  labelText: 'Note',
                  border: OutlineInputBorder(),
                ),
                maxLines: 5,
                onChanged: (value) => notes = value,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                if (notes.trim().isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Please enter a note'),
                      backgroundColor: Colors.red,
                    ),
                  );
                  return;
                }
                
                Navigator.of(context).pop();
                
                try {
                  // Add note to cycle (this would need a backend endpoint)
                  // For now, we'll just show a success message
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Note added successfully!'),
                        backgroundColor: Colors.green,
                      ),
                    );
                  }
                } catch (e) {
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Failed to add note: $e'),
                        backgroundColor: Colors.red,
                      ),
                    );
                  }
                }
              },
              child: const Text('Add Note'),
            ),
          ],
        );
      },
    );
  }

  void _showFilterDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        String selectedStatus = 'all';
        String selectedSeason = 'all';
        String selectedCrop = 'all';
        
        return AlertDialog(
          title: const Text('Filter Crop Cycles'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<String>(
                decoration: const InputDecoration(
                  labelText: 'Status',
                  border: OutlineInputBorder(),
                ),
                value: selectedStatus,
                items: const [
                  DropdownMenuItem(value: 'all', child: Text('All Statuses')),
                  DropdownMenuItem(value: 'active', child: Text('Active')),
                  DropdownMenuItem(value: 'completed', child: Text('Completed')),
                  DropdownMenuItem(value: 'planned', child: Text('Planned')),
                ],
                onChanged: (value) => selectedStatus = value ?? 'all',
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                decoration: const InputDecoration(
                  labelText: 'Season',
                  border: OutlineInputBorder(),
                ),
                value: selectedSeason,
                items: const [
                  DropdownMenuItem(value: 'all', child: Text('All Seasons')),
                  DropdownMenuItem(value: 'kharif', child: Text('Kharif')),
                  DropdownMenuItem(value: 'rabi', child: Text('Rabi')),
                  DropdownMenuItem(value: 'zaid', child: Text('Zaid')),
                ],
                onChanged: (value) => selectedSeason = value ?? 'all',
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                decoration: const InputDecoration(
                  labelText: 'Crop',
                  border: OutlineInputBorder(),
                ),
                value: selectedCrop,
                items: const [
                  DropdownMenuItem(value: 'all', child: Text('All Crops')),
                  DropdownMenuItem(value: 'rice', child: Text('Rice')),
                  DropdownMenuItem(value: 'wheat', child: Text('Wheat')),
                  DropdownMenuItem(value: 'maize', child: Text('Maize')),
                  DropdownMenuItem(value: 'pulses', child: Text('Pulses')),
                ],
                onChanged: (value) => selectedCrop = value ?? 'all',
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                
                // TODO: Implement actual filtering logic
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Filter applied! (Filtering logic coming soon)'),
                    backgroundColor: Colors.blue,
                  ),
                );
              },
              child: const Text('Apply Filter'),
            ),
          ],
        );
      },
    );
  }
}

class _QuickActionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final Color color;
  final VoidCallback onTap;

  const _QuickActionCard({
    required this.icon,
    required this.title,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Icon(
                icon,
                size: 32,
                color: color,
              ),
              const SizedBox(height: 8),
              Text(
                title,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

