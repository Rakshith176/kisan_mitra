import 'package:json_annotation/json_annotation.dart';

part 'catalog.g.dart';

@JsonSerializable()
class CropItemDto {
  final String id;
  final String name_en;
  final String? name_hi;
  final String? name_kn;
  CropItemDto({required this.id, required this.name_en, this.name_hi, this.name_kn});
  factory CropItemDto.fromJson(Map<String, dynamic> json) => _$CropItemDtoFromJson(json);
  Map<String, dynamic> toJson() => _$CropItemDtoToJson(this);
}

@JsonSerializable()
class CropsResponseDto {
  final List<CropItemDto> crops;
  CropsResponseDto({required this.crops});
  factory CropsResponseDto.fromJson(Map<String, dynamic> json) => _$CropsResponseDtoFromJson(json);
  Map<String, dynamic> toJson() => _$CropsResponseDtoToJson(this);
}


