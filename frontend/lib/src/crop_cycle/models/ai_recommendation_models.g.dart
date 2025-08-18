// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ai_recommendation_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$AIRecommendationImpl _$$AIRecommendationImplFromJson(
        Map<String, dynamic> json) =>
    _$AIRecommendationImpl(
      recommendationId: json['recommendationId'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      recommendationType: json['recommendationType'] as String,
      priority: json['priority'] as String,
      actionItems: (json['actionItems'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      reasoning: json['reasoning'] as String,
      expectedImpact: json['expectedImpact'] as String,
      urgencyHours: (json['urgencyHours'] as num).toInt(),
      dataSources: json['dataSources'] as Map<String, dynamic>,
      createdAt: json['createdAt'] as String,
      expiresAt: json['expiresAt'] as String?,
    );

Map<String, dynamic> _$$AIRecommendationImplToJson(
        _$AIRecommendationImpl instance) =>
    <String, dynamic>{
      'recommendationId': instance.recommendationId,
      'title': instance.title,
      'description': instance.description,
      'recommendationType': instance.recommendationType,
      'priority': instance.priority,
      'actionItems': instance.actionItems,
      'reasoning': instance.reasoning,
      'expectedImpact': instance.expectedImpact,
      'urgencyHours': instance.urgencyHours,
      'dataSources': instance.dataSources,
      'createdAt': instance.createdAt,
      'expiresAt': instance.expiresAt,
    };

_$AIRecommendationRequestImpl _$$AIRecommendationRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$AIRecommendationRequestImpl(
      includeWeather: json['includeWeather'] as bool? ?? true,
      includeMarket: json['includeMarket'] as bool? ?? true,
      includeSoil: json['includeSoil'] as bool? ?? true,
    );

Map<String, dynamic> _$$AIRecommendationRequestImplToJson(
        _$AIRecommendationRequestImpl instance) =>
    <String, dynamic>{
      'includeWeather': instance.includeWeather,
      'includeMarket': instance.includeMarket,
      'includeSoil': instance.includeSoil,
    };

_$AIRecommendationStateImpl _$$AIRecommendationStateImplFromJson(
        Map<String, dynamic> json) =>
    _$AIRecommendationStateImpl(
      recommendations: (json['recommendations'] as List<dynamic>?)
              ?.map((e) => AIRecommendation.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      isLoading: json['isLoading'] as bool? ?? false,
      isRefreshing: json['isRefreshing'] as bool? ?? false,
      error: json['error'] as String?,
      lastUpdated: json['lastUpdated'] == null
          ? null
          : DateTime.parse(json['lastUpdated'] as String),
    );

Map<String, dynamic> _$$AIRecommendationStateImplToJson(
        _$AIRecommendationStateImpl instance) =>
    <String, dynamic>{
      'recommendations': instance.recommendations,
      'isLoading': instance.isLoading,
      'isRefreshing': instance.isRefreshing,
      'error': instance.error,
      'lastUpdated': instance.lastUpdated?.toIso8601String(),
    };
