import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../api/endpoints.dart';
import '../api/http_client.dart';
import '../api/dto/feed.dart';

class FeedRepository {
  final Dio _dio;
  FeedRepository({Dio? dio}) : _dio = dio ?? ApiClient.standard().dio;

  Future<FeedResponse> fetchFeed(String clientId) async {
    // Backend expects snake_case: client_id
    final res = await _dio.get(ApiConfig.feed, queryParameters: {'client_id': clientId});
    final feed = FeedResponse.fromJson(res.data as Map<String, dynamic>);
    // Cache last successful feed
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('last_feed_json:$clientId', jsonEncode(feed.toJson()));
    await prefs.setString('last_feed_ts:$clientId', DateTime.now().toIso8601String());
    return feed;
  }

  Future<(FeedResponse?, DateTime?)> readCachedFeed(String clientId) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonStr = prefs.getString('last_feed_json:$clientId');
    if (jsonStr == null) return (null, null);
    final tsStr = prefs.getString('last_feed_ts:$clientId');
    final ts = tsStr != null ? DateTime.tryParse(tsStr) : null;
    return (FeedResponse.fromJson(jsonDecode(jsonStr) as Map<String, dynamic>), ts);
  }
}


