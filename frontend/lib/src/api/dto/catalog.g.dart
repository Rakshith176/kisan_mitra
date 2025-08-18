// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'catalog.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

CropItemDto _$CropItemDtoFromJson(Map<String, dynamic> json) => CropItemDto(
      id: json['id'] as String,
      name_en: json['name_en'] as String,
      name_hi: json['name_hi'] as String?,
      name_kn: json['name_kn'] as String?,
    );

Map<String, dynamic> _$CropItemDtoToJson(CropItemDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name_en': instance.name_en,
      'name_hi': instance.name_hi,
      'name_kn': instance.name_kn,
    };

CropsResponseDto _$CropsResponseDtoFromJson(Map<String, dynamic> json) =>
    CropsResponseDto(
      crops: (json['crops'] as List<dynamic>)
          .map((e) => CropItemDto.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$CropsResponseDtoToJson(CropsResponseDto instance) =>
    <String, dynamic>{
      'crops': instance.crops,
    };
