import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/crop_cycle_models.dart';

class CropCycleApiService {
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

  // Get all crop cycles for a farmer
  Future<List<CropCycle>> getCropCycles(String clientId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/crop-cycle/?client_id=$clientId'),
        headers: _headers,
      );
      
      final data = _handleResponse(response);
      // Backend returns the list directly, not wrapped in 'items'
      final List<dynamic> cycles = data is List ? data : [];
      
      // Add validation and better error handling
      if (cycles.isEmpty) {
        print('No crop cycles found for client: $clientId');
        return [];
      }
      
      final List<CropCycle> result = [];
      for (int i = 0; i < cycles.length; i++) {
        try {
          // Validate that cycles[i] is actually a Map
          if (cycles[i] is! Map<String, dynamic>) {
            print('Error: cycles[$i] is not a Map. Type: ${cycles[i].runtimeType}, Value: ${cycles[i]}');
            continue;
          }
          
          final cycle = CropCycle.fromJson(cycles[i]);
          result.add(cycle);
        } catch (parseError) {
          print('Error parsing crop cycle at index $i: $parseError');
          print('Raw data: ${cycles[i]}');
          print('Data type: ${cycles[i].runtimeType}');
          // Continue with other cycles instead of failing completely
        }
      }
      
      return result;
    } catch (e) {
      throw Exception('Failed to fetch crop cycles: $e');
    }
  }

  // Get a specific crop cycle
  Future<CropCycle> getCropCycle(String cycleId, String clientId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/crop-cycle/$cycleId?client_id=$clientId'),
        headers: _headers,
      );
      
      final data = _handleResponse(response);
      
      // Validate data is a Map before parsing
      if (data is! Map<String, dynamic>) {
        throw Exception('Invalid response format: expected Map<String, dynamic>, got ${data.runtimeType}');
      }
      
      return CropCycle.fromJson(data);
    } catch (e) {
      throw Exception('Failed to fetch crop cycle: $e');
    }
  }

  // Create a new crop cycle
  Future<CropCycle> createCropCycle(Map<String, dynamic> cycleData) async {
    try {
      // Extract clientId from cycleData and add it as query parameter
      final clientId = cycleData['clientId'];
      final cycleDataWithoutClientId = Map<String, dynamic>.from(cycleData);
      cycleDataWithoutClientId.remove('clientId');
      
      final response = await http.post(
        Uri.parse('$baseUrl/crop-cycle/?client_id=$clientId'),
        headers: _headers,
        body: json.encode(cycleDataWithoutClientId),
      );
      
      final data = _handleResponse(response);
      
      // Validate data is a Map before parsing
      if (data is! Map<String, dynamic>) {
        throw Exception('Invalid response format: expected Map<String, dynamic>, got ${data.runtimeType}');
      }
      
      return CropCycle.fromJson(data);
    } catch (e) {
      throw Exception('Failed to create crop cycle: $e');
    }
  }

  // Update a crop cycle
  Future<CropCycle> updateCropCycle(String cycleId, Map<String, dynamic> cycleData) async {
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/crop-cycle/$cycleId'),
        headers: _headers,
        body: json.encode(cycleData),
      );
      
      final data = _handleResponse(response);
      
      // Validate data is a Map before parsing
      if (data is! Map<String, dynamic>) {
        throw Exception('Invalid response format: expected Map<String, dynamic>, got ${data.runtimeType}');
      }
      
      return CropCycle.fromJson(data);
    } catch (e) {
      throw Exception('Failed to update crop cycle: $e');
    }
  }

  // Delete a crop cycle
  Future<void> deleteCropCycle(String cycleId, String clientId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/crop-cycle/$cycleId?client_id=$clientId'),
        headers: _headers,
      );
      
      if (response.statusCode != 204) {
        throw Exception('Failed to delete crop cycle');
      }
    } catch (e) {
      throw Exception('Failed to delete crop cycle: $e');
    }
  }

  // Get tasks for a crop cycle
  Future<List<CropTask>> getCropTasks(String cycleId, String clientId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/crop-cycle/$cycleId/tasks?client_id=$clientId'),
        headers: _headers,
      );
      
      final data = _handleResponse(response);
      final List<dynamic> tasks = data['items'] ?? [];
      
      final List<CropTask> result = [];
      for (int i = 0; i < tasks.length; i++) {
        try {
          if (tasks[i] is! Map<String, dynamic>) {
            print('Error: tasks[$i] is not a Map. Type: ${tasks[i].runtimeType}, Value: ${tasks[i]}');
            continue;
          }
          result.add(CropTask.fromJson(tasks[i]));
        } catch (parseError) {
          print('Error parsing task at index $i: $parseError');
          print('Raw data: ${tasks[i]}');
          print('Data type: ${tasks[i].runtimeType}');
        }
      }
      
      return result;
    } catch (e) {
      throw Exception('Failed to fetch crop tasks: $e');
    }
  }

  // Create a new task
  Future<CropTask> createTask(String cycleId, Map<String, dynamic> taskData) async {
    try {
      // Extract clientId from taskData and add it as query parameter
      final clientId = taskData['clientId'];
      final taskDataWithoutClientId = Map<String, dynamic>.from(taskData);
      taskDataWithoutClientId.remove('clientId');
      
      final response = await http.post(
        Uri.parse('$baseUrl/crop-cycle/$cycleId/tasks?client_id=$clientId'),
        headers: _headers,
        body: json.encode(taskDataWithoutClientId),
      );
      
      final data = _handleResponse(response);
      
      // Validate data is a Map before parsing
      if (data is! Map<String, dynamic>) {
        throw Exception('Invalid response format: expected Map<String, dynamic>, got ${data.runtimeType}');
      }
      
      return CropTask.fromJson(data);
    } catch (e) {
      throw Exception('Failed to create task: $e');
    }
  }

  // Update a task
  Future<CropTask> updateTask(String cycleId, String taskId, Map<String, dynamic> taskData) async {
    try {
      // Extract clientId from taskData and add it as query parameter
      final clientId = taskData['clientId'];
      final taskDataWithoutClientId = Map<String, dynamic>.from(taskData);
      taskDataWithoutClientId.remove('clientId');
      
      final response = await http.put(
        Uri.parse('$baseUrl/crop-cycle/$cycleId/tasks/$taskId?client_id=$clientId'),
        headers: _headers,
        body: json.encode(taskDataWithoutClientId),
      );
      
      final data = _handleResponse(response);
      
      // Validate data is a Map before parsing
      if (data is! Map<String, dynamic>) {
        throw Exception('Invalid response format: expected Map<String, dynamic>, got ${data.runtimeType}');
      }
      
      return CropTask.fromJson(data);
    } catch (e) {
      throw Exception('Failed to update task: $e');
    }
  }

  // Delete a task
  Future<void> deleteTask(String cycleId, String taskId, String clientId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/crop-cycle/$cycleId/tasks/$taskId?client_id=$clientId'),
        headers: _headers,
      );
      
      if (response.statusCode != 204) {
        throw Exception('Failed to delete task');
      }
    } catch (e) {
      throw Exception('Failed to delete task: $e');
    }
  }

  // Get observations for a crop cycle
  Future<List<CropObservation>> getObservations(String cycleId, String clientId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/crop-cycle/$cycleId/observations?client_id=$clientId'),
        headers: _headers,
      );
      
      final data = _handleResponse(response);
      final List<dynamic> observations = data['items'] ?? [];
      
      return observations.map((json) => CropObservation.fromJson(json)).toList();
    } catch (e) {
      throw Exception('Failed to fetch observations: $e');
    }
  }

  // Create a new observation
  Future<CropObservation> createObservation(String cycleId, Map<String, dynamic> observationData) async {
    try {
      // Extract clientId from observationData and add it as query parameter
      final clientId = observationData['clientId'];
      final observationDataWithoutClientId = Map<String, dynamic>.from(observationData);
      observationDataWithoutClientId.remove('clientId');
      
      final response = await http.post(
        Uri.parse('$baseUrl/crop-cycle/$cycleId/observations?client_id=$clientId'),
        headers: _headers,
        body: json.encode(observationDataWithoutClientId),
      );
      
      final data = _handleResponse(response);
      return CropObservation.fromJson(data);
    } catch (e) {
      throw Exception('Failed to create observation: $e');
    }
  }

  // Get risk alerts for a crop cycle
  Future<List<RiskAlert>> getRiskAlerts(String cycleId, String clientId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/crop-cycle/$cycleId/risks?client_id=$clientId'),
        headers: _headers,
      );
      
      final data = _handleResponse(response);
      final List<dynamic> risks = data['items'] ?? [];
      
      return risks.map((json) => RiskAlert.fromJson(json)).toList();
    } catch (e) {
      throw Exception('Failed to fetch risk alerts: $e');
    }
  }

  // Acknowledge a risk alert
  Future<RiskAlert> acknowledgeRisk(String cycleId, String riskId, String clientId) async {
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/crop-cycle/$cycleId/risks/$riskId/acknowledge?client_id=$clientId'),
        headers: _headers,
        body: json.encode({'acknowledged_at': DateTime.now().toIso8601String()}),
      );
      
      final data = _handleResponse(response);
      return RiskAlert.fromJson(data);
    } catch (e) {
      throw Exception('Failed to acknowledge risk: $e');
    }
  }

  // Generate smart checklist
  Future<SmartChecklistResponse> generateSmartChecklist(SmartChecklistRequest request) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/crop-cycle/smart-checklist'),
        headers: _headers,
        body: json.encode(request.toJson()),
      );
      
      final data = _handleResponse(response);
      return SmartChecklistResponse.fromJson(data);
    } catch (e) {
      throw Exception('Failed to generate smart checklist: $e');
    }
  }

  // Export crop tracker data
  Future<Map<String, dynamic>> exportCropTracker(String cycleId, String clientId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/crop-cycle/$cycleId/export?client_id=$clientId'),
        headers: _headers,
      );
      
      return _handleResponse(response);
    } catch (e) {
      throw Exception('Failed to export crop tracker: $e');
    }
  }

  // Get available crops for selection
  Future<List<Crop>> getAvailableCrops() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/catalog/crops'),
        headers: _headers,
      );
      
      final data = _handleResponse(response);
      final List<dynamic> crops = data['crops'] ?? [];
      
      // Convert CropItem to Crop format
      return crops.map((json) => Crop.fromJson({
        'id': json['id'],
        'nameEn': json['name_en'],
        'nameHi': json['name_hi'] ?? '',
        'nameKn': json['name_kn'] ?? '',
        'category': 'general', // Default category since CropItem doesn't have it
        'growthDurationDays': 120, // Default value
        'season': 'yearRound', // Default value
        'region': 'India', // Default value
        'description': 'Crop from catalog',
        'careInstructions': 'Follow standard care practices',
        'pestManagement': 'Monitor for pests regularly',
        'diseaseManagement': 'Watch for common diseases',
        'harvestingTips': 'Harvest when ready',
        'storageTips': 'Store in cool, dry place',
        'minTemperature': 20.0,
        'maxTemperature': 35.0,
        'minRainfall': 500.0,
        'maxRainfall': 1500.0,
        'soilType': 'Loamy',
        'soilPhMin': 6.0,
        'soilPhMax': 7.5,
        'waterRequirement': 'Moderate',
        'fertilizerRequirement': 'Balanced NPK',
        'seedRate': 'Standard rate',
        'spacing': 'Standard spacing',
        'depth': 'Standard depth',
        'thinning': 'Thin as needed',
        'weeding': 'Regular weeding',
        'irrigation': 'As needed',
        'harvesting': 'When mature',
        'postHarvest': 'Proper storage',
        'marketDemand': 'Stable',
        'expectedYield': 2.5,
        'unit': 'tons/acre',
        'minPrice': 1000.0,
        'maxPrice': 2000.0,
        'currency': 'INR',
        'imageUrl': '',
        'createdAt': DateTime.now().toIso8601String(),
        'updatedAt': DateTime.now().toIso8601String(),
      })).toList();
    } catch (e) {
      throw Exception('Failed to fetch available crops: $e');
    }
  }

  // Get farmer profile for planning
  Future<Map<String, dynamic>> getFarmerProfile(String clientId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/farmer-profiles/$clientId'),
        headers: _headers,
      );
      
      return _handleResponse(response);
    } catch (e) {
      throw Exception('Failed to fetch farmer profile: $e');
    }
  }

  // ============================================================================
  // Real-Time Data Integration APIs
  // ============================================================================

  // Get real-time weather data
  Future<Map<String, dynamic>> getRealTimeWeather(
    double latitude,
    double longitude,
    String clientId,
  ) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/crop-cycle/real-data/weather/$latitude/$longitude?client_id=$clientId'),
        headers: _headers,
      );
      
      final data = _handleResponse(response);
      
      // Check if the API returned an error status
      if (data['status'] == 'error') {
        print('API Error: ${data['message']}');
        return {};
      }
      
      // Add better error handling and logging
      if (data['weather_data'] == null) {
        print('Warning: No weather_data in response. Full response: $data');
        return {};
      }
      
      final weatherData = data['weather_data'];
      if (weatherData is! Map<String, dynamic>) {
        print('Error: weather_data is not a Map. Type: ${weatherData.runtimeType}, Value: $weatherData');
        return {};
      }
      
      return weatherData;
    } catch (e) {
      print('Error fetching weather data: $e');
      throw Exception('Failed to fetch real-time weather: $e');
    }
  }

  // Get weather forecast
  Future<List<Map<String, dynamic>>> getWeatherForecast(
    double latitude,
    double longitude,
    String clientId, {
    int days = 7,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/crop-cycle/real-data/weather/$latitude/$longitude?client_id=$clientId&days=$days'),
        headers: _headers,
      );
      
      final data = _handleResponse(response);
      
      // Check if the API returned an error status
      if (data['status'] == 'error') {
        print('API Error: ${data['message']}');
        return [];
      }
      
      return List<Map<String, dynamic>>.from(data['forecast'] ?? []);
    } catch (e) {
      throw Exception('Failed to fetch weather forecast: $e');
    }
  }

  // Get real-time market data
  Future<List<Map<String, dynamic>>> getRealTimeMarketData(
    String cropName,
    String? state,
    String? district,
    String clientId,
  ) async {
    try {
      final queryParams = <String, String>{
        'client_id': clientId,
      };
      
      if (state != null) queryParams['state'] = state;
      if (district != null) queryParams['district'] = district;
      
      final uri = Uri.parse('$baseUrl/crop-cycle/real-data/market/$cropName').replace(queryParameters: queryParams);
      
      final response = await http.get(uri, headers: _headers);
      
      final data = _handleResponse(response);
      return List<Map<String, dynamic>>.from(data['market_data'] ?? []);
    } catch (e) {
      throw Exception('Failed to fetch real-time market data: $e');
    }
  }

  // Get market price trends
  Future<Map<String, dynamic>> getMarketPriceTrends(
    String cropName,
    String? state,
    String clientId, {
    int days = 30,
  }) async {
    try {
      final queryParams = <String, String>{
        'client_id': clientId,
        'days': days.toString(),
      };
      
      if (state != null) queryParams['state'] = state;
      
      final uri = Uri.parse('$baseUrl/crop-cycle/real-data/market/$cropName/trends').replace(queryParameters: queryParams);
      
      final response = await http.get(uri, headers: _headers);
      final data = _handleResponse(response);
      return data;
    } catch (e) {
      throw Exception('Failed to fetch market price trends: $e');
    }
  }

  // Get real-time soil data
  Future<Map<String, dynamic>> getRealTimeSoilData(
    String pincode,
    String clientId,
  ) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/crop-cycle/real-data/soil/$pincode?client_id=$clientId'),
        headers: _headers,
      );
      
      final data = _handleResponse(response);
      return data['soil_data'] ?? {};
    } catch (e) {
      throw Exception('Failed to fetch real-time soil data: $e');
    }
  }

  // Get real-time data integration status
  Future<Map<String, dynamic>> getRealTimeDataStatus(String clientId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/crop-cycle/real-data/status?client_id=$clientId'),
        headers: _headers,
      );
      
      final data = _handleResponse(response);
      return data;
    } catch (e) {
      throw Exception('Failed to fetch real-time data status: $e');
    }
  }
}
