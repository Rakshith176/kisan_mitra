import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../api/endpoints.dart';
import '../api/http_client.dart';

class ProfileRepository {
  final Dio _dio;
  ProfileRepository({Dio? dio}) : _dio = dio ?? ApiClient.standard().dio;

  Future<String> ensureClientId() async {
    final prefs = await SharedPreferences.getInstance();
    var id = prefs.getString('clientId');
    if (id == null || id.isEmpty) {
      // UUID generated earlier in main(); this is a safety check
      id = DateTime.now().millisecondsSinceEpoch.toString();
      await prefs.setString('clientId', id);
    }
    return id;
  }

  Future<void> upsertProfile({
    required String clientId,
    required String language,
    double? lat,
    double? lon,
    String? pincode,
    List<String>? cropIds,
    double? farmSizeAcres,
    int? experienceYears,
  }) async {
    final payload = {
      'language': language,
      if (lat != null) 'lat': lat,
      if (lon != null) 'lon': lon,
      if (lat == null || lon == null) if (pincode != null) 'pincode': pincode,
      if (cropIds != null) 'crop_ids': cropIds,
      if (farmSizeAcres != null) 'farm_size': farmSizeAcres,
      if (experienceYears != null) 'experience_years': experienceYears,
    };
    await _dio.put(ApiConfig.profile(clientId), data: payload);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('profile_json', jsonEncode(payload));
  }
}


