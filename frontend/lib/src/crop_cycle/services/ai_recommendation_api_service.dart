import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/ai_recommendation_models.dart';

class AIRecommendationApiService {
  static const String baseUrl = 'http://localhost:8080';
  
  // Headers for API requests
  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  // Helper method to handle API responses
  dynamic _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return json.decode(response.body);
    } else {
      throw Exception('API Error: ${response.statusCode} - ${response.body}');
    }
  }

  /// Generate real-time AI recommendations
  Future<List<AIRecommendation>> generateRecommendations(
    String clientId, {
    bool includeWeather = true,
    bool includeMarket = true,
    bool includeSoil = true,
  }) async {
    try {
      final requestBody = {
        'include_weather': includeWeather,
        'include_market': includeMarket,
        'include_soil': includeSoil,
      };

      final response = await http.post(
        Uri.parse('$baseUrl/crop-cycle/ai-recommendations?client_id=$clientId'),
        headers: _headers,
        body: json.encode(requestBody),
      );

      final data = _handleResponse(response);
      
      // Backend returns list directly
      final List<dynamic> recommendations = data is List ? data : [];
      
      return recommendations.map((rec) => AIRecommendation.fromJson(rec)).toList();
    } catch (e) {
      throw Exception('Failed to generate AI recommendations: $e');
    }
  }

  /// Get cached recommendations for a client
  Future<List<AIRecommendation>> getCachedRecommendations(
    String clientId, {
    int maxRecommendations = 10,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/crop-cycle/ai-recommendations/$clientId?max_recommendations=$maxRecommendations'),
        headers: _headers,
      );

      final data = _handleResponse(response);
      
      // Backend returns list directly
      final List<dynamic> recommendations = data is List ? data : [];
      
      return recommendations.map((rec) => AIRecommendation.fromJson(rec)).toList();
    } catch (e) {
      throw Exception('Failed to fetch cached AI recommendations: $e');
    }
  }

  /// Refresh recommendations (force new generation)
  Future<List<AIRecommendation>> refreshRecommendations(
    String clientId, {
    bool includeWeather = true,
    bool includeMarket = true,
    bool includeSoil = true,
  }) async {
    try {
      // Clear any cache and generate fresh recommendations
      final requestBody = {
        'include_weather': includeWeather,
        'include_market': includeMarket,
        'include_soil': includeSoil,
      };

      final response = await http.post(
        Uri.parse('$baseUrl/crop-cycle/ai-recommendations?client_id=$clientId'),
        headers: _headers,
        body: json.encode(requestBody),
      );

      final data = _handleResponse(response);
      
      // Backend returns list directly
      final List<dynamic> recommendations = data is List ? data : [];
      
      return recommendations.map((rec) => AIRecommendation.fromJson(rec)).toList();
    } catch (e) {
      throw Exception('Failed to refresh AI recommendations: $e');
    }
  }

  /// Get recommendations by priority
  Future<List<AIRecommendation>> getRecommendationsByPriority(
    String clientId,
    String priority, {
    int maxRecommendations = 10,
  }) async {
    try {
      final recommendations = await getCachedRecommendations(clientId, maxRecommendations: 50);
      
      // Filter by priority
      return recommendations
          .where((rec) => rec.priority.toLowerCase() == priority.toLowerCase())
          .take(maxRecommendations)
          .toList();
    } catch (e) {
      throw Exception('Failed to get recommendations by priority: $e');
    }
  }

  /// Get urgent recommendations (within 24 hours)
  Future<List<AIRecommendation>> getUrgentRecommendations(
    String clientId, {
    int maxRecommendations = 10,
  }) async {
    try {
      final recommendations = await getCachedRecommendations(clientId, maxRecommendations: 50);
      
      // Filter urgent recommendations
      return recommendations
          .where((rec) => rec.urgencyHours <= 24)
          .take(maxRecommendations)
          .toList();
    } catch (e) {
      throw Exception('Failed to get urgent recommendations: $e');
    }
  }

  /// Get recommendations by type
  Future<List<AIRecommendation>> getRecommendationsByType(
    String clientId,
    String type, {
    int maxRecommendations = 10,
  }) async {
    try {
      final recommendations = await getCachedRecommendations(clientId, maxRecommendations: 50);
      
      // Filter by type
      return recommendations
          .where((rec) => rec.recommendationType.toLowerCase() == type.toLowerCase())
          .take(maxRecommendations)
          .toList();
    } catch (e) {
      throw Exception('Failed to get recommendations by type: $e');
    }
  }

  /// Get weather-based recommendations
  Future<List<AIRecommendation>> getWeatherRecommendations(
    String clientId, {
    int maxRecommendations = 10,
  }) async {
    return getRecommendationsByType(clientId, 'weather_adaptation', maxRecommendations: maxRecommendations);
  }

  /// Get market-based recommendations
  Future<List<AIRecommendation>> getMarketRecommendations(
    String clientId, {
    int maxRecommendations = 10,
  }) async {
    return getRecommendationsByType(clientId, 'market_action', maxRecommendations: maxRecommendations);
  }

  /// Get soil-based recommendations
  Future<List<AIRecommendation>> getSoilRecommendations(
    String clientId, {
    int maxRecommendations = 10,
  }) async {
    return getRecommendationsByType(clientId, 'soil_improvement', maxRecommendations: maxRecommendations);
  }

  /// Get crop protection recommendations
  Future<List<AIRecommendation>> getCropProtectionRecommendations(
    String clientId, {
    int maxRecommendations = 10,
  }) async {
    return getRecommendationsByType(clientId, 'crop_protection', maxRecommendations: maxRecommendations);
  }

  /// Get irrigation recommendations
  Future<List<AIRecommendation>> getIrrigationRecommendations(
    String clientId, {
    int maxRecommendations = 10,
  }) async {
    return getRecommendationsByType(clientId, 'irrigation', maxRecommendations: maxRecommendations);
  }

  /// Get fertilization recommendations
  Future<List<AIRecommendation>> getFertilizationRecommendations(
    String clientId, {
    int maxRecommendations = 10,
  }) async {
    return getRecommendationsByType(clientId, 'fertilization', maxRecommendations: maxRecommendations);
  }

  /// Get pest control recommendations
  Future<List<AIRecommendation>> getPestControlRecommendations(
    String clientId, {
    int maxRecommendations = 10,
  }) async {
    return getRecommendationsByType(clientId, 'pest_control', maxRecommendations: maxRecommendations);
  }

  /// Get harvest timing recommendations
  Future<List<AIRecommendation>> getHarvestTimingRecommendations(
    String clientId, {
    int maxRecommendations = 10,
  }) async {
    return getRecommendationsByType(clientId, 'harvest_timing', maxRecommendations: maxRecommendations);
  }
}
