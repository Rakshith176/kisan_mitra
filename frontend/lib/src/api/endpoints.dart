class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8080',
  );

  static const String catalogCrops = '/catalog/crops';
  static String profile(String clientId) => '/profiles/$clientId';
  static const String feed = '/feed';
  
  /// WebSocket endpoint for chat
  /// Matches the backend WebSocket endpoint: /chat/ws/{session_id}
  static String wsChat(String sessionId, String clientId, String language) =>
      'ws://${baseUrl.replaceFirst(RegExp(r'^https?://'), '')}/chat/ws/$sessionId?client_id=$clientId&language=$language';
  
  /// WebSocket endpoint for Live API
  /// Matches the backend Live API WebSocket endpoint: /live/ws/{session_id}
  static String wsLiveAPI(String sessionId, String clientId, String language) =>
      'ws://${baseUrl.replaceFirst(RegExp(r'^https?://'), '')}/live/ws/$sessionId?client_id=$clientId&language=$language';
}


