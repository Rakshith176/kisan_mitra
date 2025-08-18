import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/crop_cycle_models.dart';
import '../providers/crop_cycle_providers.dart';
import '../services/crop_cycle_api_service.dart';

class AddTaskScreen extends ConsumerStatefulWidget {
  final String cycleId;
  final String clientId;

  const AddTaskScreen({
    super.key,
    required this.cycleId,
    required this.clientId,
  });

  @override
  ConsumerState<AddTaskScreen> createState() => _AddTaskScreenState();
}

class _AddTaskScreenState extends ConsumerState<AddTaskScreen> {
  final _formKey = GlobalKey<FormState>();
  final _scrollController = ScrollController();
  
  // Form fields
  String _title = '';
  String _description = '';
  String _selectedTaskType = 'planting';
  DateTime _dueDate = DateTime.now().add(const Duration(days: 1));
  String _selectedPriority = 'medium';
  int _estimatedHours = 2;
  String _selectedStatus = 'pending';
  String _notes = '';
  
  // State
  bool _isLoading = false;
  String? _error;

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
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

  Future<void> _createTask() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      setState(() => _isLoading = true);
      
      final apiService = ref.read(cropCycleApiServiceProvider);
      final taskData = {
        'cycleId': widget.cycleId,
        'clientId': widget.clientId,
        'title': _title,
        'description': _description,
        'taskType': _selectedTaskType,
        'dueDate': _dueDate.toIso8601String(),
        'priority': _selectedPriority,
        'estimatedHours': _estimatedHours,
        'status': _selectedStatus,
        'notes': _notes,
      };

      await apiService.createTask(widget.cycleId, taskData);
      
      // Refresh the tasks list
      ref.read(tasksProvider((widget.cycleId, widget.clientId)).notifier)
          .fetchTasks(widget.cycleId, widget.clientId);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Task created successfully!')),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to create task: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Add New Task'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: Form(
        key: _formKey,
        child: Column(
          children: [
            Expanded(
              child: _buildForm(),
            ),
            _buildBottomActions(),
          ],
        ),
      ),
    );
  }

  Widget _buildForm() {
    return ListView(
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
    );
  }

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
        hintText: 'e.g., Apply fertilizer, Water plants',
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
        hintText: 'Detailed description of the task',
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
        hintText: 'e.g., 2',
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
        hintText: 'Additional notes or instructions',
      ),
      maxLines: 3,
      onChanged: (value) => _notes = value,
    );
  }

  Widget _buildBottomActions() {
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
              onPressed: () => Navigator.of(context).pop(),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Text('Cancel'),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: ElevatedButton(
              onPressed: _isLoading ? null : _createTask,
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
                  : const Text('Create Task'),
            ),
          ),
        ],
      ),
    );
  }
}
