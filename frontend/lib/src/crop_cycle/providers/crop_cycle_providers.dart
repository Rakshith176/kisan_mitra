import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/crop_cycle_models.dart';
import '../services/crop_cycle_api_service.dart';

// API Service Provider
final cropCycleApiServiceProvider = Provider<CropCycleApiService>((ref) {
  return CropCycleApiService();
});

// Crop Cycles State
class CropCyclesState {
  final List<CropCycle> cycles;
  final bool isLoading;
  final String? error;
  final bool isStale;

  const CropCyclesState({
    this.cycles = const [],
    this.isLoading = false,
    this.error,
    this.isStale = false,
  });

  CropCyclesState copyWith({
    List<CropCycle>? cycles,
    bool? isLoading,
    String? error,
    bool? isStale,
  }) {
    return CropCyclesState(
      cycles: cycles ?? this.cycles,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      isStale: isStale ?? this.isStale,
    );
  }
}

// Crop Cycles Notifier
class CropCyclesNotifier extends StateNotifier<CropCyclesState> {
  final CropCycleApiService _apiService;

  CropCyclesNotifier(this._apiService) : super(const CropCyclesState());

  Future<void> fetchCropCycles(String clientId) async {
    try {
      state = state.copyWith(isLoading: true, error: null);
      final cycles = await _apiService.getCropCycles(clientId);
      state = state.copyWith(
        cycles: cycles,
        isLoading: false,
        isStale: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> refreshCropCycles(String clientId) async {
    await fetchCropCycles(clientId);
  }

  void markAsStale() {
    state = state.copyWith(isStale: true);
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

// Crop Cycles Provider
final cropCyclesProvider = StateNotifierProvider.family<CropCyclesNotifier, CropCyclesState, String>((ref, clientId) {
  final apiService = ref.watch(cropCycleApiServiceProvider);
  return CropCyclesNotifier(apiService);
});

// Individual Crop Cycle State
class CropCycleState {
  final CropCycle? cycle;
  final bool isLoading;
  final String? error;

  const CropCycleState({
    this.cycle,
    this.isLoading = false,
    this.error,
  });

  CropCycleState copyWith({
    CropCycle? cycle,
    bool? isLoading,
    String? error,
  }) {
    return CropCycleState(
      cycle: cycle ?? this.cycle,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

// Individual Crop Cycle Notifier
class CropCycleNotifier extends StateNotifier<CropCycleState> {
  final CropCycleApiService _apiService;

  CropCycleNotifier(this._apiService) : super(const CropCycleState());

  Future<void> fetchCropCycle(String cycleId, String clientId) async {
    try {
      state = state.copyWith(isLoading: true, error: null);
      final cycle = await _apiService.getCropCycle(cycleId, clientId);
      state = state.copyWith(
        cycle: cycle,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> updateCropCycle(String cycleId, Map<String, dynamic> data) async {
    try {
      state = state.copyWith(isLoading: true, error: null);
      final updatedCycle = await _apiService.updateCropCycle(cycleId, data);
      state = state.copyWith(
        cycle: updatedCycle,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

// Individual Crop Cycle Provider
final cropCycleProvider = StateNotifierProvider.family<CropCycleNotifier, CropCycleState, (String, String)>((ref, params) {
  final (cycleId, clientId) = params;
  final apiService = ref.watch(cropCycleApiServiceProvider);
  return CropCycleNotifier(apiService);
});

// Tasks State
class TasksState {
  final List<CropTask> tasks;
  final bool isLoading;
  final String? error;

  const TasksState({
    this.tasks = const [],
    this.isLoading = false,
    this.error,
  });

  TasksState copyWith({
    List<CropTask>? tasks,
    bool? isLoading,
    String? error,
  }) {
    return TasksState(
      tasks: tasks ?? this.tasks,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

// Tasks Notifier
class TasksNotifier extends StateNotifier<TasksState> {
  final CropCycleApiService _apiService;

  TasksNotifier(this._apiService) : super(const TasksState());

  Future<void> fetchTasks(String cycleId, String clientId) async {
    try {
      state = state.copyWith(isLoading: true, error: null);
      final tasks = await _apiService.getTasks(cycleId, clientId);
      state = state.copyWith(
        tasks: tasks,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> updateTaskStatus(String cycleId, String taskId, String status, String clientId, {String? notes, DateTime? completedAt}) async {
    try {
      final updatedTask = await _apiService.updateTaskStatus(cycleId, taskId, status, clientId, notes: notes, completedAt: completedAt);
      
      // Update the task in the state
      final updatedTasks = state.tasks.map((task) {
        if (task.id == taskId) {
          return updatedTask;
        }
        return task;
      }).toList();
      
      state = state.copyWith(tasks: updatedTasks);
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }

  Future<void> addObservation(String cycleId, Map<String, dynamic> observationData) async {
    try {
      await _apiService.addObservation(cycleId, observationData);
      // Refresh tasks to get updated data
      await fetchTasks(cycleId, observationData['clientId'] ?? '');
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }

  Future<void> generateSmartChecklist(String cycleId, String clientId) async {
    try {
      state = state.copyWith(isLoading: true, error: null);
      final newTasks = await _apiService.generateSmartChecklist(cycleId, clientId);
      
      // Merge new tasks with existing ones, avoiding duplicates
      final existingTaskIds = state.tasks.map((task) => task.id).toSet();
      final uniqueNewTasks = newTasks.where((task) => !existingTaskIds.contains(task.id)).toList();
      
      final allTasks = [...state.tasks, ...uniqueNewTasks];
      state = state.copyWith(
        tasks: allTasks,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }

  Future<void> createTask(String cycleId, Map<String, dynamic> taskData) async {
    try {
      state = state.copyWith(isLoading: true, error: null);
      final newTask = await _apiService.createTask(cycleId, taskData);
      state = state.copyWith(
        tasks: [...state.tasks, newTask],
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> updateTask(String cycleId, String taskId, Map<String, dynamic> taskData) async {
    try {
      state = state.copyWith(isLoading: true, error: null);
      final updatedTask = await _apiService.updateTask(cycleId, taskId, taskData);
      final updatedTasks = state.tasks.map((task) {
        return task.id == taskId ? updatedTask : task;
      }).toList();
      state = state.copyWith(
        tasks: updatedTasks,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> deleteTask(String cycleId, String taskId) async {
    try {
      await _apiService.deleteTask(cycleId, taskId);
      final updatedTasks = state.tasks.where((task) => task.id != taskId).toList();
      state = state.copyWith(tasks: updatedTasks);
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }
}

// Tasks Provider
final tasksProvider = StateNotifierProvider.family<TasksNotifier, TasksState, (String, String)>((ref, params) {
  final (cycleId, clientId) = params;
  final apiService = ref.watch(cropCycleApiServiceProvider);
  return TasksNotifier(apiService);
});
