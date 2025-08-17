import 'package:json_annotation/json_annotation.dart';

part 'feed.g.dart';

@JsonSerializable()
class LocalizedText {
  final String en;
  final String? hi;
  final String? kn;
  const LocalizedText({required this.en, this.hi, this.kn});
  factory LocalizedText.fromJson(Map<String, dynamic> json) => _$LocalizedTextFromJson(json);
  Map<String, dynamic> toJson() => _$LocalizedTextToJson(this);
}

String localized(LocalizedText t, String lang) =>
    lang == 'hi' && (t.hi ?? '').isNotEmpty ? t.hi! : lang == 'kn' && (t.kn ?? '').isNotEmpty ? t.kn! : t.en;

@JsonSerializable()
class WeatherDailyItem {
  final DateTime date;
  final double temp_min_c;
  final double temp_max_c;
  final double? precipitation_mm;
  final double? wind_kph;
  const WeatherDailyItem({
    required this.date,
    required this.temp_min_c,
    required this.temp_max_c,
    this.precipitation_mm,
    this.wind_kph,
  });
  factory WeatherDailyItem.fromJson(Map<String, dynamic> json) => _$WeatherDailyItemFromJson(json);
  Map<String, dynamic> toJson() => _$WeatherDailyItemToJson(this);
}

@JsonSerializable()
class WeatherCardData {
  final String card_type;
  final LocalizedText title;
  final List<LocalizedText> body_variants;
  final String? location_name;
  final double lat;
  final double lon;
  final List<WeatherDailyItem> forecast_days;
  final LocalizedText? analysis;
  final List<LocalizedText> recommendations;
  final List<Map<String, dynamic>> risk_tags;
  final DateTime? action_window_start;
  final DateTime? action_window_end;
  final DateTime? computed_at;
  final int? data_window_days;
  const WeatherCardData({
    required this.card_type,
    required this.title,
    required this.body_variants,
    this.location_name,
    required this.lat,
    required this.lon,
    required this.forecast_days,
    this.analysis,
    this.recommendations = const [],
    this.risk_tags = const [],
    this.action_window_start,
    this.action_window_end,
    this.computed_at,
    this.data_window_days,
  });
  factory WeatherCardData.fromJson(Map<String, dynamic> json) => _$WeatherCardDataFromJson(json);
  Map<String, dynamic> toJson() => _$WeatherCardDataToJson(this);
}

@JsonSerializable()
class MarketPriceItem {
  final String market_name;
  final String commodity;
  final String unit;
  final double price_min;
  final double price_max;
  final double? price_modal;
  final double? distance_km;
  final DateTime? date;
  const MarketPriceItem({
    required this.market_name,
    required this.commodity,
    required this.unit,
    required this.price_min,
    required this.price_max,
    this.price_modal,
    this.distance_km,
    this.date,
  });
  factory MarketPriceItem.fromJson(Map<String, dynamic> json) => _$MarketPriceItemFromJson(json);
  Map<String, dynamic> toJson() => _$MarketPriceItemToJson(this);
}

@JsonSerializable()
class MarketPricesCardData {
  final String card_type;
  final LocalizedText title;
  final List<LocalizedText> body_variants;
  final List<MarketPriceItem> items;
  final LocalizedText? analysis;
  final List<LocalizedText> recommendations;
  final DateTime? computed_at;
  final int? data_window_days;
  final DateTime? freshness_date;
  const MarketPricesCardData({
    required this.card_type,
    required this.title,
    required this.body_variants,
    required this.items,
    this.analysis,
    this.recommendations = const [],
    this.computed_at,
    this.data_window_days,
    this.freshness_date,
  });
  factory MarketPricesCardData.fromJson(Map<String, dynamic> json) => _$MarketPricesCardDataFromJson(json);
  Map<String, dynamic> toJson() => _$MarketPricesCardDataToJson(this);
}

@JsonSerializable()
class FeedCard {
  final String card_id;
  final DateTime created_at;
  final String language;
  final Map<String, dynamic> data; // will be parsed by card_type
  const FeedCard({required this.card_id, required this.created_at, required this.language, required this.data});
  factory FeedCard.fromJson(Map<String, dynamic> json) => _$FeedCardFromJson(json);
  Map<String, dynamic> toJson() => _$FeedCardToJson(this);
}

@JsonSerializable()
class FeedResponse {
  final String client_id;
  final String language;
  final List<FeedCard> cards;
  final String? cursor;
  final bool? has_more;
  const FeedResponse({required this.client_id, required this.language, required this.cards, this.cursor, this.has_more});
  factory FeedResponse.fromJson(Map<String, dynamic> json) => _$FeedResponseFromJson(json);
  Map<String, dynamic> toJson() => _$FeedResponseToJson(this);
}

// Crop tips card
@JsonSerializable()
class CropTipsCardData {
  final String card_type;
  final LocalizedText title;
  final List<LocalizedText> body_variants;
  final String crop_id;
  final LocalizedText crop_name;
  const CropTipsCardData({
    required this.card_type,
    required this.title,
    required this.body_variants,
    required this.crop_id,
    required this.crop_name,
  });
  factory CropTipsCardData.fromJson(Map<String, dynamic> json) => _$CropTipsCardDataFromJson(json);
  Map<String, dynamic> toJson() => _$CropTipsCardDataToJson(this);
}


