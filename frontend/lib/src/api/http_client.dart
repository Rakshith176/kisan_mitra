import 'package:dio/dio.dart';
import 'endpoints.dart';

class ApiClient {
  final Dio _dio;
  ApiClient._(this._dio);

  factory ApiClient.standard() {
    final dio = Dio(
      BaseOptions(
        baseUrl: ApiConfig.baseUrl,
        // Allow slow backend responses
        connectTimeout: const Duration(minutes: 5),
        receiveTimeout: const Duration(minutes: 5),
        headers: {
          'Content-Type': 'application/json',
        },
      ),
    );
    dio.interceptors.add(LogInterceptor(responseBody: false));
    return ApiClient._(dio);
  }

  Dio get dio => _dio;
}


