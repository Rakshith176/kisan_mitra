import 'package:freezed_annotation/freezed_annotation.dart';

part 'crop_cycle_models.freezed.dart';
part 'crop_cycle_models.g.dart';

@freezed
class CropCycle with _$CropCycle {
  const factory CropCycle({
    required String id,
    required String clientId,
    required String cropId,
    required String variety,
    required DateTime startDate,
    required String season,
    required String pincode,
    required double lat,
    required double lon,
    required String irrigationType,
    required double areaAcres,
    required String language,
    required String status,
    required DateTime plannedHarvestDate,
    DateTime? actualHarvestDate,
    required DateTime createdAt,
    required DateTime updatedAt,
    Crop? crop,
    List<GrowthStage>? growthStages,
    List<CropTask>? tasks,
  }) = _CropCycle;

  factory CropCycle.fromJson(Map<String, dynamic> json) =>
      _$CropCycleFromJson(json);
}

@freezed
class Crop with _$Crop {
  const factory Crop({
    required String id,
    required String nameEn,
    required String nameHi,
    required String nameKn,
    required String category,
    required int growthDurationDays,
    required String season,
    required String region,
    required String description,
    required String careInstructions,
    required String pestManagement,
    required String diseaseManagement,
    required String harvestingTips,
    required String storageTips,
    required double minTemperature,
    required double maxTemperature,
    required double minRainfall,
    required double maxRainfall,
    required String soilType,
    required double soilPhMin,
    required double soilPhMax,
    required String waterRequirement,
    required String fertilizerRequirement,
    required String seedRate,
    required String spacing,
    required String depth,
    required String thinning,
    required String weeding,
    required String irrigation,
    required String harvesting,
    required String postHarvest,
    required String marketDemand,
    required double expectedYield,
    required String unit,
    required double minPrice,
    required double maxPrice,
    required String currency,
    required String imageUrl,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _Crop;

  factory Crop.fromJson(Map<String, dynamic> json) => _$CropFromJson(json);
}

@freezed
class GrowthStage with _$GrowthStage {
  const factory GrowthStage({
    required String id,
    required String cycleId,
    required String stageName,
    required DateTime expectedStartDate,
    DateTime? actualStartDate,
    required int expectedDurationDays,
    required double progressPercentage,
    String? notes,
    List<String>? photos,
    required DateTime createdAt,
  }) = _GrowthStage;

  factory GrowthStage.fromJson(Map<String, dynamic> json) =>
      _$GrowthStageFromJson(json);
}

@freezed
class CropTask with _$CropTask {
  const factory CropTask({
    required String id,
    required String cycleId,
    required String title,
    required String description,
    required String priority,
    required DateTime dueDate,
    required String status,
    required int estimatedHours,
    String? notes,
    List<String>? photos,
    String? voiceNote,
    DateTime? completedAt,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _CropTask;

  factory CropTask.fromJson(Map<String, dynamic> json) =>
      _$CropTaskFromJson(json);
}

@freezed
class CropObservation with _$CropObservation {
  const factory CropObservation({
    required String id,
    required String cycleId,
    required String observationType,
    required String description,
    required DateTime observedAt,
    List<String>? photos,
    String? voiceNote,
    String? notes,
    required DateTime createdAt,
  }) = _CropObservation;

  factory CropObservation.fromJson(Map<String, dynamic> json) =>
      _$CropObservationFromJson(json);
}

@freezed
class RiskAlert with _$RiskAlert {
  const factory RiskAlert({
    required String id,
    required String cycleId,
    required String riskType,
    required String severity,
    required String description,
    required String mitigationStrategy,
    required DateTime detectedAt,
    DateTime? acknowledgedAt,
    DateTime? resolvedAt,
    required DateTime createdAt,
  }) = _RiskAlert;

  factory RiskAlert.fromJson(Map<String, dynamic> json) =>
      _$RiskAlertFromJson(json);
}

@freezed
class CropPlan with _$CropPlan {
  const factory CropPlan({
    required String id,
    required String clientId,
    required String cropId,
    required String variety,
    required DateTime plannedStartDate,
    required String season,
    required String pincode,
    required double lat,
    required double lon,
    required String irrigationType,
    required double areaAcres,
    required String language,
    required String status,
    required DateTime plannedHarvestDate,
    required List<CropTask> tasks,
    required List<RiskAlert> risks,
    required Map<String, dynamic> recommendations,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _CropPlan;

  factory CropPlan.fromJson(Map<String, dynamic> json) =>
      _$CropPlanFromJson(json);
}

@freezed
class SmartChecklistRequest with _$SmartChecklistRequest {
  const factory SmartChecklistRequest({
    required String clientId,
    required String cropId,
    required String variety,
    required DateTime startDate,
    required String season,
    required String pincode,
    required double lat,
    required double lon,
    required String irrigationType,
    required double areaAcres,
    required String language,
    required int farmerExperienceYears,
    required String farmSizeCategory,
    required Map<String, dynamic> weatherConditions,
    required Map<String, dynamic> soilConditions,
    required Map<String, dynamic> marketConditions,
  }) = _SmartChecklistRequest;

  factory SmartChecklistRequest.fromJson(Map<String, dynamic> json) =>
      _$SmartChecklistRequestFromJson(json);
}

@freezed
class SmartChecklistResponse with _$SmartChecklistResponse {
  const factory SmartChecklistResponse({
    required List<CropTask> tasks,
    required Map<String, dynamic> recommendations,
    required String riskLevel,
    required List<String> riskFactors,
    required List<String> mitigationStrategies,
    required DateTime createdAt,
  }) = _SmartChecklistResponse;

  factory SmartChecklistResponse.fromJson(Map<String, dynamic> json) =>
      _$SmartChecklistResponseFromJson(json);
}

// Enums
enum Season { kharif, rabi, zaid, yearRound }
enum PlanStatus { planned, active, completed, failed }
enum ProgressStatus { notStarted, inProgress, completed, delayed }
enum TaskStatus { pending, inProgress, completed, delayed, skipped }
enum TaskPriority { low, medium, high, critical }
enum RiskSeverity { low, medium, high, critical }
enum RiskType { weather, pest, disease, market, soil, irrigation }
