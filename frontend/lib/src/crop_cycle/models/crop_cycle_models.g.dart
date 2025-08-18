// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'crop_cycle_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$CropCycleImpl _$$CropCycleImplFromJson(Map<String, dynamic> json) =>
    _$CropCycleImpl(
      id: json['id'] as String,
      clientId: json['clientId'] as String,
      cropId: json['cropId'] as String,
      variety: json['variety'] as String,
      startDate: DateTime.parse(json['startDate'] as String),
      season: json['season'] as String,
      pincode: json['pincode'] as String,
      lat: (json['lat'] as num).toDouble(),
      lon: (json['lon'] as num).toDouble(),
      irrigationType: json['irrigationType'] as String,
      areaAcres: (json['areaAcres'] as num).toDouble(),
      language: json['language'] as String,
      status: json['status'] as String,
      plannedHarvestDate: DateTime.parse(json['plannedHarvestDate'] as String),
      actualHarvestDate: json['actualHarvestDate'] == null
          ? null
          : DateTime.parse(json['actualHarvestDate'] as String),
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      crop: json['crop'] == null
          ? null
          : Crop.fromJson(json['crop'] as Map<String, dynamic>),
      growthStages: (json['growthStages'] as List<dynamic>?)
          ?.map((e) => GrowthStage.fromJson(e as Map<String, dynamic>))
          .toList(),
      tasks: (json['tasks'] as List<dynamic>?)
          ?.map((e) => CropTask.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$$CropCycleImplToJson(_$CropCycleImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'clientId': instance.clientId,
      'cropId': instance.cropId,
      'variety': instance.variety,
      'startDate': instance.startDate.toIso8601String(),
      'season': instance.season,
      'pincode': instance.pincode,
      'lat': instance.lat,
      'lon': instance.lon,
      'irrigationType': instance.irrigationType,
      'areaAcres': instance.areaAcres,
      'language': instance.language,
      'status': instance.status,
      'plannedHarvestDate': instance.plannedHarvestDate.toIso8601String(),
      'actualHarvestDate': instance.actualHarvestDate?.toIso8601String(),
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
      'crop': instance.crop,
      'growthStages': instance.growthStages,
      'tasks': instance.tasks,
    };

_$CropImpl _$$CropImplFromJson(Map<String, dynamic> json) => _$CropImpl(
      id: json['id'] as String,
      nameEn: json['nameEn'] as String,
      nameHi: json['nameHi'] as String,
      nameKn: json['nameKn'] as String,
      category: json['category'] as String,
      growthDurationDays: (json['growthDurationDays'] as num).toInt(),
      season: json['season'] as String,
      region: json['region'] as String,
      description: json['description'] as String,
      careInstructions: json['careInstructions'] as String,
      pestManagement: json['pestManagement'] as String,
      diseaseManagement: json['diseaseManagement'] as String,
      harvestingTips: json['harvestingTips'] as String,
      storageTips: json['storageTips'] as String,
      minTemperature: (json['minTemperature'] as num).toDouble(),
      maxTemperature: (json['maxTemperature'] as num).toDouble(),
      minRainfall: (json['minRainfall'] as num).toDouble(),
      maxRainfall: (json['maxRainfall'] as num).toDouble(),
      soilType: json['soilType'] as String,
      soilPhMin: (json['soilPhMin'] as num).toDouble(),
      soilPhMax: (json['soilPhMax'] as num).toDouble(),
      waterRequirement: json['waterRequirement'] as String,
      fertilizerRequirement: json['fertilizerRequirement'] as String,
      seedRate: json['seedRate'] as String,
      spacing: json['spacing'] as String,
      depth: json['depth'] as String,
      thinning: json['thinning'] as String,
      weeding: json['weeding'] as String,
      irrigation: json['irrigation'] as String,
      harvesting: json['harvesting'] as String,
      postHarvest: json['postHarvest'] as String,
      marketDemand: json['marketDemand'] as String,
      expectedYield: (json['expectedYield'] as num).toDouble(),
      unit: json['unit'] as String,
      minPrice: (json['minPrice'] as num).toDouble(),
      maxPrice: (json['maxPrice'] as num).toDouble(),
      currency: json['currency'] as String,
      imageUrl: json['imageUrl'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$$CropImplToJson(_$CropImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nameEn': instance.nameEn,
      'nameHi': instance.nameHi,
      'nameKn': instance.nameKn,
      'category': instance.category,
      'growthDurationDays': instance.growthDurationDays,
      'season': instance.season,
      'region': instance.region,
      'description': instance.description,
      'careInstructions': instance.careInstructions,
      'pestManagement': instance.pestManagement,
      'diseaseManagement': instance.diseaseManagement,
      'harvestingTips': instance.harvestingTips,
      'storageTips': instance.storageTips,
      'minTemperature': instance.minTemperature,
      'maxTemperature': instance.maxTemperature,
      'minRainfall': instance.minRainfall,
      'maxRainfall': instance.maxRainfall,
      'soilType': instance.soilType,
      'soilPhMin': instance.soilPhMin,
      'soilPhMax': instance.soilPhMax,
      'waterRequirement': instance.waterRequirement,
      'fertilizerRequirement': instance.fertilizerRequirement,
      'seedRate': instance.seedRate,
      'spacing': instance.spacing,
      'depth': instance.depth,
      'thinning': instance.thinning,
      'weeding': instance.weeding,
      'irrigation': instance.irrigation,
      'harvesting': instance.harvesting,
      'postHarvest': instance.postHarvest,
      'marketDemand': instance.marketDemand,
      'expectedYield': instance.expectedYield,
      'unit': instance.unit,
      'minPrice': instance.minPrice,
      'maxPrice': instance.maxPrice,
      'currency': instance.currency,
      'imageUrl': instance.imageUrl,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
    };

_$GrowthStageImpl _$$GrowthStageImplFromJson(Map<String, dynamic> json) =>
    _$GrowthStageImpl(
      id: json['id'] as String,
      cycleId: json['cycleId'] as String,
      stageName: json['stageName'] as String,
      expectedStartDate: DateTime.parse(json['expectedStartDate'] as String),
      actualStartDate: json['actualStartDate'] == null
          ? null
          : DateTime.parse(json['actualStartDate'] as String),
      expectedDurationDays: (json['expectedDurationDays'] as num).toInt(),
      progressPercentage: (json['progressPercentage'] as num).toDouble(),
      notes: json['notes'] as String?,
      photos:
          (json['photos'] as List<dynamic>?)?.map((e) => e as String).toList(),
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$$GrowthStageImplToJson(_$GrowthStageImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'cycleId': instance.cycleId,
      'stageName': instance.stageName,
      'expectedStartDate': instance.expectedStartDate.toIso8601String(),
      'actualStartDate': instance.actualStartDate?.toIso8601String(),
      'expectedDurationDays': instance.expectedDurationDays,
      'progressPercentage': instance.progressPercentage,
      'notes': instance.notes,
      'photos': instance.photos,
      'createdAt': instance.createdAt.toIso8601String(),
    };

_$CropTaskImpl _$$CropTaskImplFromJson(Map<String, dynamic> json) =>
    _$CropTaskImpl(
      id: json['id'] as String,
      cycleId: json['cycleId'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      priority: json['priority'] as String,
      dueDate: DateTime.parse(json['dueDate'] as String),
      status: json['status'] as String,
      estimatedHours: (json['estimatedHours'] as num).toInt(),
      notes: json['notes'] as String?,
      photos:
          (json['photos'] as List<dynamic>?)?.map((e) => e as String).toList(),
      voiceNote: json['voiceNote'] as String?,
      completedAt: json['completedAt'] == null
          ? null
          : DateTime.parse(json['completedAt'] as String),
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$$CropTaskImplToJson(_$CropTaskImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'cycleId': instance.cycleId,
      'title': instance.title,
      'description': instance.description,
      'priority': instance.priority,
      'dueDate': instance.dueDate.toIso8601String(),
      'status': instance.status,
      'estimatedHours': instance.estimatedHours,
      'notes': instance.notes,
      'photos': instance.photos,
      'voiceNote': instance.voiceNote,
      'completedAt': instance.completedAt?.toIso8601String(),
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
    };

_$CropObservationImpl _$$CropObservationImplFromJson(
        Map<String, dynamic> json) =>
    _$CropObservationImpl(
      id: json['id'] as String,
      cycleId: json['cycleId'] as String,
      observationType: json['observationType'] as String,
      description: json['description'] as String,
      observedAt: DateTime.parse(json['observedAt'] as String),
      photos:
          (json['photos'] as List<dynamic>?)?.map((e) => e as String).toList(),
      voiceNote: json['voiceNote'] as String?,
      notes: json['notes'] as String?,
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$$CropObservationImplToJson(
        _$CropObservationImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'cycleId': instance.cycleId,
      'observationType': instance.observationType,
      'description': instance.description,
      'observedAt': instance.observedAt.toIso8601String(),
      'photos': instance.photos,
      'voiceNote': instance.voiceNote,
      'notes': instance.notes,
      'createdAt': instance.createdAt.toIso8601String(),
    };

_$RiskAlertImpl _$$RiskAlertImplFromJson(Map<String, dynamic> json) =>
    _$RiskAlertImpl(
      id: json['id'] as String,
      cycleId: json['cycleId'] as String,
      riskType: json['riskType'] as String,
      severity: json['severity'] as String,
      description: json['description'] as String,
      mitigationStrategy: json['mitigationStrategy'] as String,
      detectedAt: DateTime.parse(json['detectedAt'] as String),
      acknowledgedAt: json['acknowledgedAt'] == null
          ? null
          : DateTime.parse(json['acknowledgedAt'] as String),
      resolvedAt: json['resolvedAt'] == null
          ? null
          : DateTime.parse(json['resolvedAt'] as String),
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$$RiskAlertImplToJson(_$RiskAlertImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'cycleId': instance.cycleId,
      'riskType': instance.riskType,
      'severity': instance.severity,
      'description': instance.description,
      'mitigationStrategy': instance.mitigationStrategy,
      'detectedAt': instance.detectedAt.toIso8601String(),
      'acknowledgedAt': instance.acknowledgedAt?.toIso8601String(),
      'resolvedAt': instance.resolvedAt?.toIso8601String(),
      'createdAt': instance.createdAt.toIso8601String(),
    };

_$CropPlanImpl _$$CropPlanImplFromJson(Map<String, dynamic> json) =>
    _$CropPlanImpl(
      id: json['id'] as String,
      clientId: json['clientId'] as String,
      cropId: json['cropId'] as String,
      variety: json['variety'] as String,
      plannedStartDate: DateTime.parse(json['plannedStartDate'] as String),
      season: json['season'] as String,
      pincode: json['pincode'] as String,
      lat: (json['lat'] as num).toDouble(),
      lon: (json['lon'] as num).toDouble(),
      irrigationType: json['irrigationType'] as String,
      areaAcres: (json['areaAcres'] as num).toDouble(),
      language: json['language'] as String,
      status: json['status'] as String,
      plannedHarvestDate: DateTime.parse(json['plannedHarvestDate'] as String),
      tasks: (json['tasks'] as List<dynamic>)
          .map((e) => CropTask.fromJson(e as Map<String, dynamic>))
          .toList(),
      risks: (json['risks'] as List<dynamic>)
          .map((e) => RiskAlert.fromJson(e as Map<String, dynamic>))
          .toList(),
      recommendations: json['recommendations'] as Map<String, dynamic>,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$$CropPlanImplToJson(_$CropPlanImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'clientId': instance.clientId,
      'cropId': instance.cropId,
      'variety': instance.variety,
      'plannedStartDate': instance.plannedStartDate.toIso8601String(),
      'season': instance.season,
      'pincode': instance.pincode,
      'lat': instance.lat,
      'lon': instance.lon,
      'irrigationType': instance.irrigationType,
      'areaAcres': instance.areaAcres,
      'language': instance.language,
      'status': instance.status,
      'plannedHarvestDate': instance.plannedHarvestDate.toIso8601String(),
      'tasks': instance.tasks,
      'risks': instance.risks,
      'recommendations': instance.recommendations,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
    };

_$SmartChecklistRequestImpl _$$SmartChecklistRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$SmartChecklistRequestImpl(
      clientId: json['clientId'] as String,
      cropId: json['cropId'] as String,
      variety: json['variety'] as String,
      startDate: DateTime.parse(json['startDate'] as String),
      season: json['season'] as String,
      pincode: json['pincode'] as String,
      lat: (json['lat'] as num).toDouble(),
      lon: (json['lon'] as num).toDouble(),
      irrigationType: json['irrigationType'] as String,
      areaAcres: (json['areaAcres'] as num).toDouble(),
      language: json['language'] as String,
      farmerExperienceYears: (json['farmerExperienceYears'] as num).toInt(),
      farmSizeCategory: json['farmSizeCategory'] as String,
      weatherConditions: json['weatherConditions'] as Map<String, dynamic>,
      soilConditions: json['soilConditions'] as Map<String, dynamic>,
      marketConditions: json['marketConditions'] as Map<String, dynamic>,
    );

Map<String, dynamic> _$$SmartChecklistRequestImplToJson(
        _$SmartChecklistRequestImpl instance) =>
    <String, dynamic>{
      'clientId': instance.clientId,
      'cropId': instance.cropId,
      'variety': instance.variety,
      'startDate': instance.startDate.toIso8601String(),
      'season': instance.season,
      'pincode': instance.pincode,
      'lat': instance.lat,
      'lon': instance.lon,
      'irrigationType': instance.irrigationType,
      'areaAcres': instance.areaAcres,
      'language': instance.language,
      'farmerExperienceYears': instance.farmerExperienceYears,
      'farmSizeCategory': instance.farmSizeCategory,
      'weatherConditions': instance.weatherConditions,
      'soilConditions': instance.soilConditions,
      'marketConditions': instance.marketConditions,
    };

_$SmartChecklistResponseImpl _$$SmartChecklistResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$SmartChecklistResponseImpl(
      tasks: (json['tasks'] as List<dynamic>)
          .map((e) => CropTask.fromJson(e as Map<String, dynamic>))
          .toList(),
      recommendations: json['recommendations'] as Map<String, dynamic>,
      riskLevel: json['riskLevel'] as String,
      riskFactors: (json['riskFactors'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      mitigationStrategies: (json['mitigationStrategies'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$$SmartChecklistResponseImplToJson(
        _$SmartChecklistResponseImpl instance) =>
    <String, dynamic>{
      'tasks': instance.tasks,
      'recommendations': instance.recommendations,
      'riskLevel': instance.riskLevel,
      'riskFactors': instance.riskFactors,
      'mitigationStrategies': instance.mitigationStrategies,
      'createdAt': instance.createdAt.toIso8601String(),
    };
