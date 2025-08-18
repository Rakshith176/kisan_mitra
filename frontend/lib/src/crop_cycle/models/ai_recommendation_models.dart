import 'package:freezed_annotation/freezed_annotation.dart';

part 'ai_recommendation_models.freezed.dart';
part 'ai_recommendation_models.g.dart';

@freezed
class AIRecommendation with _$AIRecommendation {
  const factory AIRecommendation({
    required String recommendationId,
    required String title,
    required String description,
    required String recommendationType,
    required String priority,
    required List<String> actionItems,
    required String reasoning,
    required String expectedImpact,
    required int urgencyHours,
    required Map<String, dynamic> dataSources,
    required String createdAt,
    String? expiresAt,
  }) = _AIRecommendation;

  factory AIRecommendation.fromJson(Map<String, dynamic> json) =>
      _$AIRecommendationFromJson(json);
}

@freezed
class AIRecommendationRequest with _$AIRecommendationRequest {
  const factory AIRecommendationRequest({
    @Default(true) bool includeWeather,
    @Default(true) bool includeMarket,
    @Default(true) bool includeSoil,
  }) = _AIRecommendationRequest;

  factory AIRecommendationRequest.fromJson(Map<String, dynamic> json) =>
      _$AIRecommendationRequestFromJson(json);
}

@freezed
class AIRecommendationState with _$AIRecommendationState {
  const factory AIRecommendationState({
    @Default([]) List<AIRecommendation> recommendations,
    @Default(false) bool isLoading,
    @Default(false) bool isRefreshing,
    String? error,
    DateTime? lastUpdated,
  }) = _AIRecommendationState;

  factory AIRecommendationState.fromJson(Map<String, dynamic> json) =>
      _$AIRecommendationStateFromJson(json);
}

// Priority levels for UI styling
enum RecommendationPriority {
  critical,
  high,
  medium,
  low;

  String get displayName {
    switch (this) {
      case RecommendationPriority.critical:
        return 'Critical';
      case RecommendationPriority.high:
        return 'High';
      case RecommendationPriority.medium:
        return 'Medium';
      case RecommendationPriority.low:
        return 'Low';
    }
  }

  String get color {
    switch (this) {
      case RecommendationPriority.critical:
        return '#FF4444'; // Red
      case RecommendationPriority.high:
        return '#FF8800'; // Orange
      case RecommendationPriority.medium:
        return '#FFBB33'; // Yellow
      case RecommendationPriority.low:
        return '#00C851'; // Green
    }
  }

  String get icon {
    switch (this) {
      case RecommendationPriority.critical:
        return '🚨';
      case RecommendationPriority.high:
        return '⚠️';
      case RecommendationPriority.medium:
        return '📋';
      case RecommendationPriority.low:
        return 'ℹ️';
    }
  }
}

// Recommendation types for categorization
enum RecommendationType {
  irrigation,
  fertilization,
  pestControl,
  harvestTiming,
  marketAction,
  weatherAdaptation,
  soilImprovement,
  cropProtection;

  String get displayName {
    switch (this) {
      case RecommendationType.irrigation:
        return 'Irrigation';
      case RecommendationType.fertilization:
        return 'Fertilization';
      case RecommendationType.pestControl:
        return 'Pest Control';
      case RecommendationType.harvestTiming:
        return 'Harvest Timing';
      case RecommendationType.marketAction:
        return 'Market Action';
      case RecommendationType.weatherAdaptation:
        return 'Weather Adaptation';
      case RecommendationType.soilImprovement:
        return 'Soil Improvement';
      case RecommendationType.cropProtection:
        return 'Crop Protection';
    }
  }

  String get icon {
    switch (this) {
      case RecommendationType.irrigation:
        return '💧';
      case RecommendationType.fertilization:
        return '🌱';
      case RecommendationType.pestControl:
        return '🐛';
      case RecommendationType.harvestTiming:
        return '🌾';
      case RecommendationType.marketAction:
        return '💰';
      case RecommendationType.weatherAdaptation:
        return '🌤️';
      case RecommendationType.soilImprovement:
        return '🌍';
      case RecommendationType.cropProtection:
        return '🛡️';
    }
  }
}

// Extension methods for easy conversion
extension AIRecommendationExtensions on AIRecommendation {
  RecommendationPriority get priorityEnum {
    switch (priority.toLowerCase()) {
      case 'critical':
        return RecommendationPriority.critical;
      case 'high':
        return RecommendationPriority.high;
      case 'medium':
        return RecommendationPriority.medium;
      case 'low':
        return RecommendationPriority.low;
      default:
        return RecommendationPriority.medium;
    }
  }

  RecommendationType get typeEnum {
    switch (recommendationType.toLowerCase()) {
      case 'irrigation':
        return RecommendationType.irrigation;
      case 'fertilization':
        return RecommendationType.fertilization;
      case 'pest_control':
        return RecommendationType.pestControl;
      case 'harvest_timing':
        return RecommendationType.harvestTiming;
      case 'market_action':
        return RecommendationType.marketAction;
      case 'weather_adaptation':
        return RecommendationType.weatherAdaptation;
      case 'soil_improvement':
        return RecommendationType.soilImprovement;
      case 'crop_protection':
        return RecommendationType.cropProtection;
      default:
        return RecommendationType.cropProtection;
    }
  }

  bool get isUrgent => urgencyHours <= 24;
  bool get isCritical => priorityEnum == RecommendationPriority.critical;
  bool get isExpired {
    if (expiresAt == null) return false;
    final expiryDate = DateTime.tryParse(expiresAt!);
    if (expiryDate == null) return false;
    return DateTime.now().isAfter(expiryDate);
  }

  String get urgencyText {
    if (urgencyHours == 0) return 'Immediate';
    if (urgencyHours <= 2) return 'Within 2 hours';
    if (urgencyHours <= 24) return 'Within 24 hours';
    if (urgencyHours <= 72) return 'Within 3 days';
    if (urgencyHours <= 168) return 'Within 1 week';
    return 'Planning';
  }
}
