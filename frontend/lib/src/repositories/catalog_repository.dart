import 'package:dio/dio.dart';

import '../api/endpoints.dart';
import '../api/http_client.dart';
import '../api/dto/catalog.dart';

class CatalogRepository {
  final Dio _dio;
  CatalogRepository({Dio? dio}) : _dio = dio ?? ApiClient.standard().dio;

  Future<List<CropItemDto>> fetchCrops() async {
    final res = await _dio.get(ApiConfig.catalogCrops);
    final dto = CropsResponseDto.fromJson(res.data as Map<String, dynamic>);
    return dto.crops;
  }
}


