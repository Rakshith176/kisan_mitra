import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../api/endpoints.dart';
import '../api/http_client.dart';

class MarketPrice {
  final String marketName;
  final String commodity;
  final double? modalPrice;
  final double? minPrice;
  final double? maxPrice;
  final String? unit;
  final DateTime? date;

  MarketPrice({
    required this.marketName,
    required this.commodity,
    this.modalPrice,
    this.minPrice,
    this.maxPrice,
    this.unit,
    this.date,
  });

  factory MarketPrice.fromJson(Map<String, dynamic> json) {
    return MarketPrice(
      marketName: json['market_name'] ?? '',
      commodity: json['commodity'] ?? '',
      modalPrice: json['modal_price']?.toDouble(),
      minPrice: json['min_price']?.toDouble(),
      maxPrice: json['max_price']?.toDouble(),
      unit: json['unit'],
      date: json['date'] != null ? DateTime.tryParse(json['date']) : null,
    );
  }
}

class MarketPricesResponse {
  final List<MarketPrice> prices;
  final String commodity;
  final String location;
  final int totalMarkets;
  final DateTime? lastUpdated;
  final String? message;

  MarketPricesResponse({
    required this.prices,
    required this.commodity,
    required this.location,
    required this.totalMarkets,
    this.lastUpdated,
    this.message,
  });

  factory MarketPricesResponse.fromJson(Map<String, dynamic> json) {
    return MarketPricesResponse(
      prices: (json['prices'] as List<dynamic>?)
          ?.map((p) => MarketPrice.fromJson(p as Map<String, dynamic>))
          .toList() ?? [],
      commodity: json['commodity'] ?? '',
      location: json['location'] ?? '',
      totalMarkets: json['total_markets'] ?? 0,
      lastUpdated: json['last_updated'] != null 
          ? DateTime.tryParse(json['last_updated']) 
          : null,
      message: json['message'],
    );
  }
}

class MarketPricesService {
  final Dio _dio;
  
  MarketPricesService({Dio? dio}) : _dio = dio ?? ApiClient.standard().dio;

  /// Fetch market prices for a specific crop
  Future<MarketPricesResponse> getMarketPrices({
    required String crop,
    String? location,
    String? clientId,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'crop': crop.toLowerCase(),
      };
      
      if (location != null) {
        queryParams['location'] = location;
      }
      
      if (clientId != null) {
        queryParams['client_id'] = clientId;
      }

      final response = await _dio.get(
        ApiConfig.marketPrices,
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      return MarketPricesResponse.fromJson(data);
    } catch (e) {
      // Return empty response with error message
      return MarketPricesResponse(
        prices: [],
        commodity: crop,
        location: location ?? 'Unknown',
        totalMarkets: 0,
        message: 'Failed to fetch market data: ${e.toString()}',
      );
    }
  }

  /// Cache market prices data
  Future<void> cacheMarketPrices(String crop, MarketPricesResponse data) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cacheKey = 'market_prices_${crop.toLowerCase()}';
      await prefs.setString(cacheKey, jsonEncode(data));
      await prefs.setString('${cacheKey}_ts', DateTime.now().toIso8601String());
    } catch (e) {
      // Silently fail caching
    }
  }

  /// Get cached market prices data
  Future<MarketPricesResponse?> getCachedMarketPrices(String crop) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cacheKey = 'market_prices_${crop.toLowerCase()}';
      final jsonStr = prefs.getString(cacheKey);
      final tsStr = prefs.getString('${cacheKey}_ts');
      
      if (jsonStr == null) return null;
      
      final ts = tsStr != null ? DateTime.tryParse(tsStr) : null;
      final isStale = ts == null || DateTime.now().difference(ts) > const Duration(hours: 6);
      
      if (isStale) return null; // Return null if data is stale
      
      final data = jsonDecode(jsonStr) as Map<String, dynamic>;
      return MarketPricesResponse.fromJson(data);
    } catch (e) {
      return null;
    }
  }

  /// Get market prices with caching
  Future<MarketPricesResponse> getMarketPricesWithCache({
    required String crop,
    String? location,
    String? clientId,
  }) async {
    // Try to get cached data first
    final cached = await getCachedMarketPrices(crop);
    if (cached != null) {
      return cached;
    }

    // Fetch fresh data
    final fresh = await getMarketPrices(
      crop: crop,
      location: location,
      clientId: clientId,
    );

    // Cache the fresh data
    await cacheMarketPrices(crop, fresh);
    
    return fresh;
  }
}
