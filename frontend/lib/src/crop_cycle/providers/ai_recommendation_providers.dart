import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/ai_recommendation_models.dart';
import '../services/ai_recommendation_api_service.dart';

// Provider for the AI recommendation API service
final aiRecommendationApiServiceProvider = Provider<AIRecommendationApiService>((ref) {
  return AIRecommendationApiService();
});

// Provider for AI recommendation state
final aiRecommendationProvider = StateNotifierProvider<AIRecommendationNotifier, AIRecommendationState>((ref) {
  final apiService = ref.watch(aiRecommendationApiServiceProvider);
  return AIRecommendationNotifier(apiService);
});

// Provider family for client-specific AI recommendations
final clientAIRecommendationProvider = StateNotifierProvider.family<AIRecommendationNotifier, AIRecommendationState, String>((ref, clientId) {
  final apiService = ref.watch(aiRecommendationApiServiceProvider);
  return AIRecommendationNotifier(apiService);
});

// Provider for urgent recommendations
final urgentRecommendationsProvider = Provider.family<List<AIRecommendation>, String>((ref, clientId) {
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  return state.recommendations.where((rec) => rec.isUrgent).toList();
});

// Provider for critical recommendations
final criticalRecommendationsProvider = Provider.family<List<AIRecommendation>, String>((ref, clientId) {
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  return state.recommendations.where((rec) => rec.isCritical).toList();
});

// Provider for weather-based recommendations
final weatherRecommendationsProvider = Provider.family<List<AIRecommendation>, String>((ref, clientId) {
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  return state.recommendations.where((rec) => rec.typeEnum == RecommendationType.weatherAdaptation).toList();
});

// Provider for market-based recommendations
final marketRecommendationsProvider = Provider.family<List<AIRecommendation>, String>((ref, clientId) {
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  return state.recommendations.where((rec) => rec.typeEnum == RecommendationType.marketAction).toList();
});

// Provider for soil-based recommendations
final soilRecommendationsProvider = Provider.family<List<AIRecommendation>, String>((ref, clientId) {
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  return state.recommendations.where((rec) => rec.typeEnum == RecommendationType.soilImprovement).toList();
});

// Provider for crop protection recommendations
final cropProtectionRecommendationsProvider = Provider.family<List<AIRecommendation>, String>((ref, clientId) {
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  return state.recommendations.where((rec) => rec.typeEnum == RecommendationType.cropProtection).toList();
});

// Provider for irrigation recommendations
final irrigationRecommendationsProvider = Provider.family<List<AIRecommendation>, String>((ref, clientId) {
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  return state.recommendations.where((rec) => rec.typeEnum == RecommendationType.irrigation).toList();
});

// Provider for fertilization recommendations
final fertilizationRecommendationsProvider = Provider.family<List<AIRecommendation>, String>((ref, clientId) {
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  return state.recommendations.where((rec) => rec.typeEnum == RecommendationType.fertilization).toList();
});

// Provider for pest control recommendations
final pestControlRecommendationsProvider = Provider.family<List<AIRecommendation>, String>((ref, clientId) {
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  return state.recommendations.where((rec) => rec.typeEnum == RecommendationType.pestControl).toList();
});

// Provider for harvest timing recommendations
final harvestTimingRecommendationsProvider = Provider.family<List<AIRecommendation>, String>((ref, clientId) {
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  return state.recommendations.where((rec) => rec.typeEnum == RecommendationType.harvestTiming).toList();
});

// Provider for recommendations by priority
final recommendationsByPriorityProvider = Provider.family<List<AIRecommendation>, (String, String)>((ref, params) {
  final (clientId, priority) = params;
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  return state.recommendations.where((rec) => rec.priority.toLowerCase() == priority.toLowerCase()).toList();
});

// Provider for recommendations by type
final recommendationsByTypeProvider = Provider.family<List<AIRecommendation>, (String, String)>((ref, params) {
  final (clientId, type) = params;
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  return state.recommendations.where((rec) => rec.recommendationType.toLowerCase() == type.toLowerCase()).toList();
});

// Provider for expired recommendations
final expiredRecommendationsProvider = Provider.family<List<AIRecommendation>, String>((ref, clientId) {
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  return state.recommendations.where((rec) => rec.isExpired).toList();
});

// Provider for active (non-expired) recommendations
final activeRecommendationsProvider = Provider.family<List<AIRecommendation>, String>((ref, clientId) {
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  return state.recommendations.where((rec) => !rec.isExpired).toList();
});

// Provider for recommendations count by priority
final recommendationsCountByPriorityProvider = Provider.family<Map<String, int>, String>((ref, clientId) {
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  final counts = <String, int>{};
  
  for (final rec in state.recommendations) {
    final priority = rec.priority.toLowerCase();
    counts[priority] = (counts[priority] ?? 0) + 1;
  }
  
  return counts;
});

// Provider for recommendations count by type
final recommendationsCountByTypeProvider = Provider.family<Map<String, int>, String>((ref, clientId) {
  final state = ref.watch(clientAIRecommendationProvider(clientId));
  final counts = <String, int>{};
  
  for (final rec in state.recommendations) {
    final type = rec.recommendationType.toLowerCase();
    counts[type] = (counts[type] ?? 0) + 1;
  }
  
  return counts;
});

// State notifier for managing AI recommendations
class AIRecommendationNotifier extends StateNotifier<AIRecommendationState> {
  final AIRecommendationApiService _apiService;

  AIRecommendationNotifier(this._apiService) : super(const AIRecommendationState());

  /// Generate new AI recommendations
  Future<void> generateRecommendations(
    String clientId, {
    bool includeWeather = true,
    bool includeMarket = true,
    bool includeSoil = true,
  }) async {
    try {
      state = state.copyWith(isLoading: true, error: null);
      
      final recommendations = await _apiService.generateRecommendations(
        clientId,
        includeWeather: includeWeather,
        includeMarket: includeMarket,
        includeSoil: includeSoil,
      );
      
      state = state.copyWith(
        recommendations: recommendations,
        isLoading: false,
        lastUpdated: DateTime.now(),
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Fetch cached recommendations
  Future<void> fetchCachedRecommendations(
    String clientId, {
    int maxRecommendations = 10,
  }) async {
    try {
      state = state.copyWith(isLoading: true, error: null);
      
      final recommendations = await _apiService.getCachedRecommendations(
        clientId,
        maxRecommendations: maxRecommendations,
      );
      
      state = state.copyWith(
        recommendations: recommendations,
        isLoading: false,
        lastUpdated: DateTime.now(),
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Refresh recommendations (force new generation)
  Future<void> refreshRecommendations(
    String clientId, {
    bool includeWeather = true,
    bool includeMarket = true,
    bool includeSoil = true,
  }) async {
    try {
      state = state.copyWith(isRefreshing: true, error: null);
      
      final recommendations = await _apiService.refreshRecommendations(
        clientId,
        includeWeather: includeWeather,
        includeMarket: includeMarket,
        includeSoil: includeSoil,
      );
      
      state = state.copyWith(
        recommendations: recommendations,
        isRefreshing: false,
        lastUpdated: DateTime.now(),
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isRefreshing: false,
        error: e.toString(),
      );
    }
  }

  /// Get recommendations by priority
  Future<List<AIRecommendation>> getRecommendationsByPriority(
    String clientId,
    String priority, {
    int maxRecommendations = 10,
  }) async {
    try {
      return await _apiService.getRecommendationsByPriority(
        clientId,
        priority,
        maxRecommendations: maxRecommendations,
      );
    } catch (e) {
      state = state.copyWith(error: e.toString());
      return [];
    }
  }

  /// Get urgent recommendations
  Future<List<AIRecommendation>> getUrgentRecommendations(
    String clientId, {
    int maxRecommendations = 10,
  }) async {
    try {
      return await _apiService.getUrgentRecommendations(
        clientId,
        maxRecommendations: maxRecommendations,
      );
    } catch (e) {
      state = state.copyWith(error: e.toString());
      return [];
    }
  }

  /// Get recommendations by type
  Future<List<AIRecommendation>> getRecommendationsByType(
    String clientId,
    String type, {
    int maxRecommendations = 10,
  }) async {
    try {
      return await _apiService.getRecommendationsByType(
        clientId,
        type,
        maxRecommendations: maxRecommendations,
      );
    } catch (e) {
      state = state.copyWith(error: e.toString());
      return [];
    }
  }

  /// Clear error state
  void clearError() {
    state = state.copyWith(error: null);
  }

  /// Clear all recommendations
  void clearRecommendations() {
    state = state.copyWith(
      recommendations: [],
      lastUpdated: DateTime.now(),
    );
  }

  /// Remove expired recommendations
  void removeExpiredRecommendations() {
    final activeRecommendations = state.recommendations.where((rec) => !rec.isExpired).toList();
    state = state.copyWith(
      recommendations: activeRecommendations,
      lastUpdated: DateTime.now(),
    );
  }

  /// Get recommendations summary
  Map<String, dynamic> getRecommendationsSummary() {
    final total = state.recommendations.length;
    final urgent = state.recommendations.where((rec) => rec.isUrgent).length;
    final critical = state.recommendations.where((rec) => rec.isCritical).length;
    final expired = state.recommendations.where((rec) => rec.isExpired).length;
    
    return {
      'total': total,
      'urgent': urgent,
      'critical': critical,
      'expired': expired,
      'active': total - expired,
      'lastUpdated': state.lastUpdated,
    };
  }
}
