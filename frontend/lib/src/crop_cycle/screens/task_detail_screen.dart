import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/crop_cycle_models.dart';
import '../providers/crop_cycle_providers.dart';
import '../services/crop_cycle_api_service.dart';

class TaskDetailScreen extends ConsumerStatefulWidget {
  final CropTask task;
  final String cycleId;
  final String clientId;

  const TaskDetailScreen({
    super.key,
    required this.task,
    required this.cycleId,
    required this.clientId,
  });

  @override
  ConsumerState<TaskDetailScreen> createState() => _TaskDetailScreenState();
}

class _TaskDetailScreenState extends ConsumerState<TaskDetailScreen> {
  final _formKey = GlobalKey<FormState>();
  final _scrollController = ScrollController();
  
  // Form fields (for editing)
  late String _title;
  late String _description;
  late String _selectedTaskType;
  late DateTime _dueDate;
  late String _selectedPriority;
  late int _estimatedHours;
  late String _selectedStatus;
  late String _notes;
  
  // State
  bool _isEditing = false;
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _initializeFormFields();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _initializeFormFields() {
    _title = widget.task.title;
    _description = widget.task.description;
    _selectedTaskType = 'other'; // Default since CropTask doesn't have taskType
    _dueDate = widget.task.dueDate;
    _selectedPriority = widget.task.priority;
    _estimatedHours = widget.task.estimatedHours;
    _selectedStatus = widget.task.status;
    _notes = widget.task.notes ?? '';
  }

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _dueDate,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );
    if (picked != null && picked != _dueDate) {
      setState(() {
        _dueDate = picked;
      });
    }
  }

  Future<void> _updateTask() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      setState(() => _isLoading = true);
      
      final apiService = ref.read(cropCycleApiServiceProvider);
      final taskData = {
        'title': _title,
        'description': _description,
        'taskType': _selectedTaskType,
        'dueDate': _dueDate.toIso8601String(),
        'priority': _selectedPriority,
        'estimatedHours': _estimatedHours,
        'status': _selectedStatus,
        'notes': _notes,
      };

      await apiService.updateTask(widget.cycleId, widget.task.id, taskData);
      
      // Refresh the tasks list
      ref.read(tasksProvider((widget.cycleId, widget.clientId)).notifier)
          .fetchTasks(widget.cycleId, widget.clientId);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Task updated successfully!')),
        );
        setState(() {
          _isEditing = false;
        });
      }
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to update task: $e')),
        );
      }
    }
  }

  Future<void> _deleteTask() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Task'),
        content: const Text('Are you sure you want to delete this task? This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    try {
      setState(() => _isLoading = true);
      
      final apiService = ref.read(cropCycleApiServiceProvider);
      await apiService.deleteTask(widget.cycleId, widget.task.id);
      
      // Refresh the tasks list
      ref.read(tasksProvider((widget.cycleId, widget.clientId)).notifier)
          .fetchTasks(widget.cycleId, widget.clientId);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Task deleted successfully!')),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to delete task: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? 'Edit Task' : 'Task Details'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        actions: [
          if (!_isEditing) ...[
            IconButton(
              onPressed: () => setState(() => _isEditing = true),
              icon: const Icon(Icons.edit),
            ),
            IconButton(
              onPressed: _deleteTask,
              icon: const Icon(Icons.delete),
            ),
          ],
        ],
      ),
      body: _isEditing ? _buildEditForm() : _buildDetailView(),
    );
  }

  Widget _buildDetailView() {
    return ListView(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      children: [
        // Task Header
        _buildTaskHeader(),
        
        const SizedBox(height: 24),
        
        // Basic Information
        _buildInfoCard(
          title: '📋 Basic Information',
          children: [
            _buildInfoRow('Title', widget.task.title),
            if (widget.task.description.isNotEmpty)
              _buildInfoRow('Description', widget.task.description),
            _buildInfoRow('Type', _formatTaskType(_selectedTaskType)),
            _buildInfoRow('Status', _formatStatus(widget.task.status)),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // Scheduling
        _buildInfoCard(
          title: '📅 Scheduling',
          children: [
            _buildInfoRow('Due Date', _formatDate(widget.task.dueDate)),
            _buildInfoRow('Priority', _formatPriority(widget.task.priority)),
            _buildInfoRow('Estimated Hours', '${widget.task.estimatedHours} hours'),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // Additional Details
        if (widget.task.notes?.isNotEmpty == true) _buildInfoCard(
          title: '📝 Notes',
          children: [
            _buildInfoRow('Notes', widget.task.notes!),
          ],
        ),
        
        const SizedBox(height: 24),
        
        // Quick Actions
        _buildQuickActionsCard(),
      ],
    );
  }

  Widget _buildEditForm() {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          Expanded(
            child: ListView(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              children: [
                // Basic Information
                _buildSectionHeader('📋 Basic Information'),
                _buildTitleField(),
                _buildDescriptionField(),
                _buildTaskTypeField(),
                
                const SizedBox(height: 24),
                
                // Scheduling
                _buildSectionHeader('📅 Scheduling'),
                _buildDueDateField(),
                _buildPriorityField(),
                _buildEstimatedHoursField(),
                
                const SizedBox(height: 24),
                
                // Additional Details
                _buildSectionHeader('📝 Additional Details'),
                _buildStatusField(),
                _buildNotesField(),
                
                const SizedBox(height: 100), // Bottom padding
              ],
            ),
          ),
          _buildEditActions(),
        ],
      ),
    );
  }

  Widget _buildTaskHeader() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  _getTaskTypeIcon(_selectedTaskType),
                  color: _getPriorityColor(widget.task.priority),
                  size: 32,
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.task.title,
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                                             Text(
                         _formatTaskType(_selectedTaskType),
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
                    color: _getStatusColor(widget.task.status).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: _getStatusColor(widget.task.status)),
                  ),
                  child: Text(
                    _formatStatus(widget.task.status).toUpperCase(),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: _getStatusColor(widget.task.status),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Priority indicator
            Row(
              children: [
                Icon(
                  Icons.priority_high,
                  color: _getPriorityColor(widget.task.priority),
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'Priority: ${_formatPriority(widget.task.priority)}',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w500,
                    color: _getPriorityColor(widget.task.priority),
                  ),
                ),
              ],
            ),
          ],
        ),
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
                    onPressed: () => _markTaskComplete(),
                    icon: const Icon(Icons.check),
                    label: const Text('Mark Complete'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _markTaskDelayed(),
                    icon: const Icon(Icons.schedule),
                    label: const Text('Mark Delayed'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _addPhotosToTask(),
                    icon: const Icon(Icons.photo_camera),
                    label: const Text('Add Photos'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _recordVoiceForTask(),
                    icon: const Icon(Icons.mic),
                    label: const Text('Record Voice'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // Edit form widgets
  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleLarge?.copyWith(
          fontWeight: FontWeight.bold,
          color: Colors.green.shade700,
        ),
      ),
    );
  }

  Widget _buildTitleField() {
    return TextFormField(
      initialValue: _title,
      decoration: const InputDecoration(
        labelText: 'Task Title *',
        border: OutlineInputBorder(),
        prefixIcon: Icon(Icons.task),
      ),
      onChanged: (value) => _title = value,
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Please enter task title';
        }
        return null;
      },
    );
  }

  Widget _buildDescriptionField() {
    return TextFormField(
      initialValue: _description,
      decoration: const InputDecoration(
        labelText: 'Description',
        border: OutlineInputBorder(),
        prefixIcon: Icon(Icons.description),
      ),
      maxLines: 3,
      onChanged: (value) => _description = value,
    );
  }

  Widget _buildTaskTypeField() {
    return DropdownButtonFormField<String>(
      value: _selectedTaskType,
      decoration: const InputDecoration(
        labelText: 'Task Type *',
        border: OutlineInputBorder(),
        prefixIcon: Icon(Icons.category),
      ),
      items: const [
        DropdownMenuItem(value: 'planting', child: Text('Planting')),
        DropdownMenuItem(value: 'watering', child: Text('Watering')),
        DropdownMenuItem(value: 'fertilizing', child: Text('Fertilizing')),
        DropdownMenuItem(value: 'pest_control', child: Text('Pest Control')),
        DropdownMenuItem(value: 'harvesting', child: Text('Harvesting')),
        DropdownMenuItem(value: 'soil_preparation', child: Text('Soil Preparation')),
        DropdownMenuItem(value: 'maintenance', child: Text('Maintenance')),
        DropdownMenuItem(value: 'monitoring', child: Text('Monitoring')),
        DropdownMenuItem(value: 'other', child: Text('Other')),
      ],
      onChanged: (value) {
        setState(() {
          _selectedTaskType = value!;
        });
      },
    );
  }

  Widget _buildDueDateField() {
    return InkWell(
      onTap: () => _selectDate(context),
      child: InputDecorator(
        decoration: const InputDecoration(
          labelText: 'Due Date *',
          border: OutlineInputBorder(),
          prefixIcon: Icon(Icons.calendar_today),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '${_dueDate.day}/${_dueDate.month}/${_dueDate.year}',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const Icon(Icons.arrow_drop_down),
          ],
        ),
      ),
    );
  }

  Widget _buildPriorityField() {
    return DropdownButtonFormField<String>(
      value: _selectedPriority,
      decoration: const InputDecoration(
        labelText: 'Priority *',
        border: OutlineInputBorder(),
        prefixIcon: Icon(Icons.priority_high),
      ),
      items: const [
        DropdownMenuItem(value: 'low', child: Text('Low')),
        DropdownMenuItem(value: 'medium', child: Text('Medium')),
        DropdownMenuItem(value: 'high', child: Text('High')),
        DropdownMenuItem(value: 'urgent', child: Text('Urgent')),
      ],
      onChanged: (value) {
        setState(() {
          _selectedPriority = value!;
        });
      },
    );
  }

  Widget _buildEstimatedHoursField() {
    return TextFormField(
      initialValue: _estimatedHours.toString(),
      decoration: const InputDecoration(
        labelText: 'Estimated Hours *',
        border: OutlineInputBorder(),
        prefixIcon: Icon(Icons.access_time),
      ),
      keyboardType: TextInputType.number,
      onChanged: (value) {
        final hours = int.tryParse(value);
        if (hours != null && hours > 0) {
          _estimatedHours = hours;
        }
      },
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Please enter estimated hours';
        }
        final hours = int.tryParse(value);
        if (hours == null || hours <= 0) {
          return 'Please enter a valid number of hours';
        }
        return null;
      },
    );
  }

  Widget _buildStatusField() {
    return DropdownButtonFormField<String>(
      value: _selectedStatus,
      decoration: const InputDecoration(
        labelText: 'Status *',
        border: OutlineInputBorder(),
        prefixIcon: Icon(Icons.info),
      ),
      items: const [
        DropdownMenuItem(value: 'pending', child: Text('Pending')),
        DropdownMenuItem(value: 'in_progress', child: Text('In Progress')),
        DropdownMenuItem(value: 'completed', child: Text('Completed')),
        DropdownMenuItem(value: 'delayed', child: Text('Delayed')),
        DropdownMenuItem(value: 'cancelled', child: Text('Cancelled')),
      ],
      onChanged: (value) {
        setState(() {
          _selectedStatus = value!;
        });
      },
    );
  }

  Widget _buildNotesField() {
    return TextFormField(
      initialValue: _notes,
      decoration: const InputDecoration(
        labelText: 'Notes',
        border: OutlineInputBorder(),
        prefixIcon: Icon(Icons.note),
      ),
      maxLines: 3,
      onChanged: (value) => _notes = value,
    );
  }

  Widget _buildEditActions() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.shade300,
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: OutlinedButton(
              onPressed: () {
                setState(() {
                  _isEditing = false;
                  _initializeFormFields();
                });
              },
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Text('Cancel'),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: ElevatedButton(
              onPressed: _isLoading ? null : _updateTask,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                  : const Text('Update Task'),
            ),
          ),
        ],
      ),
    );
  }

  // Helper methods
  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }

  String _formatTaskType(String taskType) {
    switch (taskType) {
      case 'planting':
        return 'Planting';
      case 'watering':
        return 'Watering';
      case 'fertilizing':
        return 'Fertilizing';
      case 'pest_control':
        return 'Pest Control';
      case 'harvesting':
        return 'Harvesting';
      case 'soil_preparation':
        return 'Soil Preparation';
      case 'maintenance':
        return 'Maintenance';
      case 'monitoring':
        return 'Monitoring';
      case 'other':
        return 'Other';
      default:
        return taskType;
    }
  }

  String _formatStatus(String status) {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'in_progress':
        return 'In Progress';
      case 'completed':
        return 'Completed';
      case 'delayed':
        return 'Delayed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  String _formatPriority(String priority) {
    switch (priority) {
      case 'low':
        return 'Low';
      case 'medium':
        return 'Medium';
      case 'high':
        return 'High';
      case 'urgent':
        return 'Urgent';
      default:
        return priority;
    }
  }

  IconData _getTaskTypeIcon(String taskType) {
    switch (taskType) {
      case 'planting':
        return Icons.grass;
      case 'watering':
        return Icons.water_drop;
      case 'fertilizing':
        return Icons.eco;
      case 'pest_control':
        return Icons.bug_report;
      case 'harvesting':
        return Icons.agriculture;
      case 'soil_preparation':
        return Icons.landscape;
      case 'maintenance':
        return Icons.build;
      case 'monitoring':
        return Icons.visibility;
      default:
        return Icons.task;
    }
  }

  Color _getPriorityColor(String priority) {
    switch (priority) {
      case 'low':
        return Colors.green;
      case 'medium':
        return Colors.orange;
      case 'high':
        return Colors.red;
      case 'urgent':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'pending':
        return Colors.blue;
      case 'in_progress':
        return Colors.orange;
      case 'completed':
        return Colors.green;
      case 'delayed':
        return Colors.red;
      case 'cancelled':
        return Colors.grey;
      default:
        return Colors.grey;
    }
  }

  // Action methods
  void _markTaskComplete() {
    // TODO: Implement mark complete
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Mark Complete - Coming Soon!')),
    );
  }

  void _markTaskDelayed() {
    // TODO: Implement mark delayed
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Mark Delayed - Coming Soon!')),
    );
  }

  void _addPhotosToTask() {
    // TODO: Implement add photos
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Add Photos - Coming Soon!')),
    );
  }

  void _recordVoiceForTask() {
    // TODO: Implement voice recording
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Voice Recording - Coming Soon!')),
    );
  }
}
