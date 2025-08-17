import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/crop_cycle_models.dart';
import '../providers/crop_cycle_providers.dart';
import '../widgets/task_card.dart';
import '../widgets/real_time_weather_widget.dart';
import '../widgets/real_time_market_widget.dart';
import 'add_task_screen.dart';
import 'task_detail_screen.dart';


class CropCycleDetailScreen extends ConsumerStatefulWidget {
  final String cycleId;
  final String clientId;

  const CropCycleDetailScreen({
    super.key,
    required this.cycleId,
    required this.clientId,
  });

  @override
  ConsumerState<CropCycleDetailScreen> createState() => _CropCycleDetailScreenState();
}

class _CropCycleDetailScreenState extends ConsumerState<CropCycleDetailScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;


  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);

    
    // Load crop cycle data
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(cropCycleProvider((widget.cycleId, widget.clientId)).notifier)
          .fetchCropCycle(widget.cycleId, widget.clientId);
      ref.read(tasksProvider((widget.cycleId, widget.clientId)).notifier)
          .fetchTasks(widget.cycleId, widget.clientId);
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cropCycleState = ref.watch(cropCycleProvider((widget.cycleId, widget.clientId)));
    final tasksState = ref.watch(tasksProvider((widget.cycleId, widget.clientId)));

    return Scaffold(
      appBar: AppBar(
        title: Text(cropCycleState.cycle?.crop?.nameEn ?? 'Crop Cycle'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            onPressed: () => _showOptionsMenu(context),
            icon: const Icon(Icons.more_vert),
          ),
        ],
      ),
      body: cropCycleState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : cropCycleState.error != null
              ? _buildErrorState(cropCycleState.error!)
              : cropCycleState.cycle == null
                  ? const Center(child: Text('Crop cycle not found'))
                  : _buildBody(cropCycleState.cycle!, tasksState),
    );
  }

  Widget _buildErrorState(String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, size: 64, color: Colors.red.shade300),
          const SizedBox(height: 16),
          Text(
            'Failed to load crop cycle',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Text(
            error,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Colors.grey.shade600,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () {
              ref.read(cropCycleProvider((widget.cycleId, widget.clientId)).notifier)
                  .fetchCropCycle(widget.cycleId, widget.clientId);
            },
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildBody(CropCycle cycle, TasksState tasksState) {
    return Column(
      children: [
        // Header with basic info
        _buildHeader(cycle),
        
        // Tab bar
        Container(
          color: Colors.grey.shade50,
          child: TabBar(
            controller: _tabController,
            labelColor: Colors.green,
            unselectedLabelColor: Colors.grey,
            indicatorColor: Colors.green,
            tabs: const [
              Tab(icon: Icon(Icons.dashboard), text: 'Overview'),
              Tab(icon: Icon(Icons.task), text: 'Tasks'),
              Tab(icon: Icon(Icons.remove_red_eye), text: 'Observations'),
              Tab(icon: Icon(Icons.warning), text: 'Risks'),
            ],
          ),
        ),
        
        // Tab content
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildOverviewTab(cycle),
              _buildTasksTab(cycle, tasksState),
              _buildObservationsTab(cycle),
              _buildRisksTab(cycle),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildHeader(CropCycle cycle) {
    final crop = cycle.crop;
    final progress = _calculateProgress(cycle);
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.shade200,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                cycle.status == 'active' ? Icons.grass : Icons.grass_outlined,
                color: cycle.status == 'active' ? Colors.green : Colors.grey,
                size: 32,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${crop?.nameEn ?? 'Unknown Crop'} - ${cycle.variety}',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      '${cycle.season} Season | ${cycle.areaAcres} acres',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: _getStatusColor(cycle.status).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: _getStatusColor(cycle.status)),
                ),
                child: Text(
                  cycle.status.toUpperCase(),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: _getStatusColor(cycle.status),
                    fontWeight: FontWeight.bold,
                  ),
                ),
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
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  Text(
                    '${(progress * 100).round()}%',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
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
                  cycle.status == 'completed' ? Colors.green : Colors.blue,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildOverviewTab(CropCycle cycle) {
    final crop = cycle.crop;
    
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Key Information
        _buildInfoCard(
          title: '📊 Key Information',
          children: [
            _buildInfoRow('Start Date', _formatDate(cycle.startDate)),
            _buildInfoRow('Planned Harvest', _formatDate(cycle.plannedHarvestDate)),
            if (cycle.actualHarvestDate != null)
              _buildInfoRow('Actual Harvest', _formatDate(cycle.actualHarvestDate!)),
            _buildInfoRow('Location', 'Pincode: ${cycle.pincode}'),
            _buildInfoRow('Coordinates', '${cycle.lat.toStringAsFixed(4)}, ${cycle.lon.toStringAsFixed(4)}'),
            _buildInfoRow('Irrigation', cycle.irrigationType),
            _buildInfoRow('Language', cycle.language),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // Crop Details
        if (crop != null) _buildInfoCard(
          title: '🌱 Crop Details',
          children: [
            _buildInfoRow('Category', crop.category),
            _buildInfoRow('Growth Duration', '${crop.growthDurationDays} days'),
            _buildInfoRow('Region', crop.region),
            _buildInfoRow('Expected Yield', '${crop.expectedYield} ${crop.unit}'),
            _buildInfoRow('Market Demand', crop.marketDemand),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // Care Instructions
        if (crop != null) _buildInfoCard(
          title: '📋 Care Instructions',
          children: [
            _buildInfoRow('Water Requirement', crop.waterRequirement),
            _buildInfoRow('Fertilizer', crop.fertilizerRequirement),
            _buildInfoRow('Seed Rate', crop.seedRate),
            _buildInfoRow('Spacing', crop.spacing),
            _buildInfoRow('Depth', crop.depth),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // Real-Time Data Integration
        _buildRealTimeDataSection(cycle),
        
        const SizedBox(height: 16),
        
        // Quick Actions
        _buildQuickActionsCard(),
      ],
    );
  }

  Widget _buildTasksTab(CropCycle cycle, TasksState tasksState) {
    return Column(
      children: [
        // Header with add task button
        Container(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Text(
                'Tasks (${tasksState.tasks.length})',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              ElevatedButton.icon(
                onPressed: () => _addNewTask(),
                icon: const Icon(Icons.add),
                label: const Text('Add Task'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),
        
        // Tasks list
        Expanded(
          child: tasksState.isLoading
              ? const Center(child: CircularProgressIndicator())
              : tasksState.tasks.isEmpty
                  ? _buildEmptyTasksState()
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: tasksState.tasks.length,
                      itemBuilder: (context, index) {
                        final task = tasksState.tasks[index];
                        return TaskCard(
                          task: task,
                          onTap: () => _viewTaskDetails(task),
                          onMarkComplete: () => _markTaskComplete(task),
                          onMarkDelayed: () => _markTaskDelayed(task),
                          onSkip: () => _skipTask(task),
                          onAddPhotos: () => _addPhotosToTask(task),
                          onRecordVoice: () => _recordVoiceForTask(task),
                          onAddNotes: () => _addNotesToTask(task),
                        );
                      },
                    ),
        ),
      ],
    );
  }

  Widget _buildObservationsTab(CropCycle cycle) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.remove_red_eye, size: 64, color: Colors.grey.shade400),
          const SizedBox(height: 16),
          Text(
            'No observations yet',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Add observations to track your crop\'s progress',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Colors.grey.shade500,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: () => _addNewObservation(),
            icon: const Icon(Icons.add),
            label: const Text('Add Observation'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue,
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRisksTab(CropCycle cycle) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.warning, size: 64, color: Colors.grey.shade400),
          const SizedBox(height: 16),
          Text(
            'No risk alerts',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Risk assessment will appear here when detected',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Colors.grey.shade500,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildInfoCard({required String title, required List<Widget> children}) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: Colors.green.shade700,
              ),
            ),
            const SizedBox(height: 16),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w500,
                color: Colors.grey.shade700,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRealTimeDataSection(CropCycle cycle) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '📊 Real-Time Data Integration',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        
        // Weather and Market data in a row
        Row(
          children: [
            Expanded(
              child: RealTimeWeatherWidget(
                latitude: cycle.lat,
                longitude: cycle.lon,
                clientId: widget.clientId,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: RealTimeMarketWidget(
                clientId: widget.clientId,
                selectedCrop: cycle.crop?.nameEn ?? 'wheat',
                state: 'Karnataka', // Should come from farmer profile
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQuickActionsCard() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '🚀 Quick Actions',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: Colors.green.shade700,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _addNewTask(),
                    icon: const Icon(Icons.task),
                    label: const Text('Add Task'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _addNewObservation(),
                    icon: const Icon(Icons.remove_red_eye),
                    label: const Text('Add Observation'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _exportData(),
                    icon: const Icon(Icons.download),
                    label: const Text('Export Data'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _generateSmartChecklist(),
                    icon: const Icon(Icons.checklist),
                    label: const Text('Smart Checklist'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyTasksState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.task, size: 64, color: Colors.grey.shade400),
          const SizedBox(height: 16),
          Text(
            'No tasks yet',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Create your first task to get started',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Colors.grey.shade500,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: () => _addNewTask(),
            icon: const Icon(Icons.add),
            label: const Text('Create First Task'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  // Helper methods
  double _calculateProgress(CropCycle cycle) {
    if (cycle.growthStages == null || cycle.growthStages!.isEmpty) {
      final totalDays = cycle.crop?.growthDurationDays ?? 120;
      final daysSincePlanting = DateTime.now().difference(cycle.startDate).inDays;
      return (daysSincePlanting / totalDays).clamp(0.0, 1.0);
    }
    
    final completedStages = cycle.growthStages!
        .where((stage) => stage.actualStartDate != null)
        .length;
    final totalStages = cycle.growthStages!.length;
    
    return totalStages > 0 ? completedStages / totalStages : 0.0;
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
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

  // Action methods
  void _showOptionsMenu(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.edit),
              title: const Text('Edit Crop Cycle'),
              onTap: () {
                Navigator.pop(context);
                _editCropCycle();
              },
            ),
            ListTile(
              leading: const Icon(Icons.delete),
              title: const Text('Delete Crop Cycle'),
              onTap: () {
                Navigator.pop(context);
                _deleteCropCycle();
              },
            ),
            ListTile(
              leading: const Icon(Icons.share),
              title: const Text('Share'),
              onTap: () {
                Navigator.pop(context);
                _shareCropCycle();
              },
            ),
          ],
        ),
      ),
    );
  }

  void _addNewTask() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => AddTaskScreen(
          cycleId: widget.cycleId,
          clientId: widget.clientId,
        ),
      ),
    );
  }

  void _addNewObservation() {
    // TODO: Navigate to add observation screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Add Observation - Coming Soon!')),
    );
  }

  void _viewTaskDetails(CropTask task) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => TaskDetailScreen(
          task: task,
          cycleId: widget.cycleId,
          clientId: widget.clientId,
        ),
      ),
    );
  }

  void _markTaskComplete(CropTask task) {
    // TODO: Implement mark complete
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Mark Complete - Coming Soon!')),
    );
  }

  void _markTaskDelayed(CropTask task) {
    // TODO: Implement mark delayed
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Mark Delayed - Coming Soon!')),
    );
  }

  void _skipTask(CropTask task) {
    // TODO: Implement skip task
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Skip Task - Coming Soon!')),
    );
  }

  void _addPhotosToTask(CropTask task) {
    // TODO: Implement add photos
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Add Photos - Coming Soon!')),
    );
  }

  void _recordVoiceForTask(CropTask task) {
    // TODO: Implement voice recording
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Voice Recording - Coming Soon!')),
    );
  }

  void _addNotesToTask(CropTask task) {
    // TODO: Implement add notes
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Add Notes - Coming Soon!')),
    );
  }

  void _editCropCycle() {
    // TODO: Navigate to edit screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Edit Crop Cycle - Coming Soon!')),
    );
  }

  void _deleteCropCycle() {
    // TODO: Implement delete
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Delete Crop Cycle - Coming Soon!')),
    );
  }

  void _shareCropCycle() {
    // TODO: Implement share
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Share - Coming Soon!')),
    );
  }

  void _exportData() {
    // TODO: Implement export
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Export Data - Coming Soon!')),
    );
  }

  void _generateSmartChecklist() {
    // TODO: Implement smart checklist
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Smart Checklist - Coming Soon!')),
    );
  }
}
