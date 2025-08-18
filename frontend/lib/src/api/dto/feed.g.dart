// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'feed.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

LocalizedText _$LocalizedTextFromJson(Map<String, dynamic> json) =>
    LocalizedText(
      en: json['en'] as String,
      hi: json['hi'] as String?,
      kn: json['kn'] as String?,
    );

Map<String, dynamic> _$LocalizedTextToJson(LocalizedText instance) =>
    <String, dynamic>{
      'en': instance.en,
      'hi': instance.hi,
      'kn': instance.kn,
    };

WeatherDailyItem _$WeatherDailyItemFromJson(Map<String, dynamic> json) =>
    WeatherDailyItem(
      date: DateTime.parse(json['date'] as String),
      temp_min_c: (json['temp_min_c'] as num).toDouble(),
      temp_max_c: (json['temp_max_c'] as num).toDouble(),
      precipitation_mm: (json['precipitation_mm'] as num?)?.toDouble(),
      wind_kph: (json['wind_kph'] as num?)?.toDouble(),
    );

Map<String, dynamic> _$WeatherDailyItemToJson(WeatherDailyItem instance) =>
    <String, dynamic>{
      'date': instance.date.toIso8601String(),
      'temp_min_c': instance.temp_min_c,
      'temp_max_c': instance.temp_max_c,
      'precipitation_mm': instance.precipitation_mm,
      'wind_kph': instance.wind_kph,
    };

WeatherCardData _$WeatherCardDataFromJson(Map<String, dynamic> json) =>
    WeatherCardData(
      card_type: json['card_type'] as String,
      title: LocalizedText.fromJson(json['title'] as Map<String, dynamic>),
      body_variants: (json['body_variants'] as List<dynamic>)
          .map((e) => LocalizedText.fromJson(e as Map<String, dynamic>))
          .toList(),
      location_name: json['location_name'] as String?,
      lat: (json['lat'] as num).toDouble(),
      lon: (json['lon'] as num).toDouble(),
      forecast_days: (json['forecast_days'] as List<dynamic>)
          .map((e) => WeatherDailyItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      analysis: json['analysis'] == null
          ? null
          : LocalizedText.fromJson(json['analysis'] as Map<String, dynamic>),
      recommendations: (json['recommendations'] as List<dynamic>?)
              ?.map((e) => LocalizedText.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      risk_tags: (json['risk_tags'] as List<dynamic>?)
              ?.map((e) => e as Map<String, dynamic>)
              .toList() ??
          const [],
      action_window_start: json['action_window_start'] == null
          ? null
          : DateTime.parse(json['action_window_start'] as String),
      action_window_end: json['action_window_end'] == null
          ? null
          : DateTime.parse(json['action_window_end'] as String),
      computed_at: json['computed_at'] == null
          ? null
          : DateTime.parse(json['computed_at'] as String),
      data_window_days: (json['data_window_days'] as num?)?.toInt(),
    );

Map<String, dynamic> _$WeatherCardDataToJson(WeatherCardData instance) =>
    <String, dynamic>{
      'card_type': instance.card_type,
      'title': instance.title,
      'body_variants': instance.body_variants,
      'location_name': instance.location_name,
      'lat': instance.lat,
      'lon': instance.lon,
      'forecast_days': instance.forecast_days,
      'analysis': instance.analysis,
      'recommendations': instance.recommendations,
      'risk_tags': instance.risk_tags,
      'action_window_start': instance.action_window_start?.toIso8601String(),
      'action_window_end': instance.action_window_end?.toIso8601String(),
      'computed_at': instance.computed_at?.toIso8601String(),
      'data_window_days': instance.data_window_days,
    };

MarketPriceItem _$MarketPriceItemFromJson(Map<String, dynamic> json) =>
    MarketPriceItem(
      market_name: json['market_name'] as String,
      commodity: json['commodity'] as String,
      unit: json['unit'] as String,
      price_min: (json['price_min'] as num).toDouble(),
      price_max: (json['price_max'] as num).toDouble(),
      price_modal: (json['price_modal'] as num?)?.toDouble(),
      distance_km: (json['distance_km'] as num?)?.toDouble(),
      date:
          json['date'] == null ? null : DateTime.parse(json['date'] as String),
    );

Map<String, dynamic> _$MarketPriceItemToJson(MarketPriceItem instance) =>
    <String, dynamic>{
      'market_name': instance.market_name,
      'commodity': instance.commodity,
      'unit': instance.unit,
      'price_min': instance.price_min,
      'price_max': instance.price_max,
      'price_modal': instance.price_modal,
      'distance_km': instance.distance_km,
      'date': instance.date?.toIso8601String(),
    };

MarketPricesCardData _$MarketPricesCardDataFromJson(
        Map<String, dynamic> json) =>
    MarketPricesCardData(
      card_type: json['card_type'] as String,
      title: LocalizedText.fromJson(json['title'] as Map<String, dynamic>),
      body_variants: (json['body_variants'] as List<dynamic>)
          .map((e) => LocalizedText.fromJson(e as Map<String, dynamic>))
          .toList(),
      items: (json['items'] as List<dynamic>)
          .map((e) => MarketPriceItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      analysis: json['analysis'] == null
          ? null
          : LocalizedText.fromJson(json['analysis'] as Map<String, dynamic>),
      recommendations: (json['recommendations'] as List<dynamic>?)
              ?.map((e) => LocalizedText.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      computed_at: json['computed_at'] == null
          ? null
          : DateTime.parse(json['computed_at'] as String),
      data_window_days: (json['data_window_days'] as num?)?.toInt(),
      freshness_date: json['freshness_date'] == null
          ? null
          : DateTime.parse(json['freshness_date'] as String),
    );

Map<String, dynamic> _$MarketPricesCardDataToJson(
        MarketPricesCardData instance) =>
    <String, dynamic>{
      'card_type': instance.card_type,
      'title': instance.title,
      'body_variants': instance.body_variants,
      'items': instance.items,
      'analysis': instance.analysis,
      'recommendations': instance.recommendations,
      'computed_at': instance.computed_at?.toIso8601String(),
      'data_window_days': instance.data_window_days,
      'freshness_date': instance.freshness_date?.toIso8601String(),
    };

FeedCard _$FeedCardFromJson(Map<String, dynamic> json) => FeedCard(
      card_id: json['card_id'] as String,
      created_at: DateTime.parse(json['created_at'] as String),
      language: json['language'] as String,
      data: json['data'] as Map<String, dynamic>,
    );

Map<String, dynamic> _$FeedCardToJson(FeedCard instance) => <String, dynamic>{
      'card_id': instance.card_id,
      'created_at': instance.created_at.toIso8601String(),
      'language': instance.language,
      'data': instance.data,
    };

FeedResponse _$FeedResponseFromJson(Map<String, dynamic> json) => FeedResponse(
      client_id: json['client_id'] as String,
      language: json['language'] as String,
      cards: (json['cards'] as List<dynamic>)
          .map((e) => FeedCard.fromJson(e as Map<String, dynamic>))
          .toList(),
      cursor: json['cursor'] as String?,
      has_more: json['has_more'] as bool?,
    );

Map<String, dynamic> _$FeedResponseToJson(FeedResponse instance) =>
    <String, dynamic>{
      'client_id': instance.client_id,
      'language': instance.language,
      'cards': instance.cards,
      'cursor': instance.cursor,
      'has_more': instance.has_more,
    };

CropTipsCardData _$CropTipsCardDataFromJson(Map<String, dynamic> json) =>
    CropTipsCardData(
      card_type: json['card_type'] as String,
      title: LocalizedText.fromJson(json['title'] as Map<String, dynamic>),
      body_variants: (json['body_variants'] as List<dynamic>)
          .map((e) => LocalizedText.fromJson(e as Map<String, dynamic>))
          .toList(),
      crop_id: json['crop_id'] as String,
      crop_name:
          LocalizedText.fromJson(json['crop_name'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$CropTipsCardDataToJson(CropTipsCardData instance) =>
    <String, dynamic>{
      'card_type': instance.card_type,
      'title': instance.title,
      'body_variants': instance.body_variants,
      'crop_id': instance.crop_id,
      'crop_name': instance.crop_name,
    };
