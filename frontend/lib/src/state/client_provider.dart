import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

final clientIdProvider = FutureProvider<String>((ref) async {
  final prefs = await SharedPreferences.getInstance();
  final id = prefs.getString('clientId');
  if (id == null || id.isEmpty) {
    throw StateError('clientId not initialized');
  }
  return id;
});


