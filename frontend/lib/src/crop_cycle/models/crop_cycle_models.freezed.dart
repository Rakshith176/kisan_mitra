// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'crop_cycle_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

CropCycle _$CropCycleFromJson(Map<String, dynamic> json) {
  return _CropCycle.fromJson(json);
}

/// @nodoc
mixin _$CropCycle {
  String get id => throw _privateConstructorUsedError;
  String get clientId => throw _privateConstructorUsedError;
  String get cropId => throw _privateConstructorUsedError;
  String get variety => throw _privateConstructorUsedError;
  DateTime get startDate => throw _privateConstructorUsedError;
  String get season => throw _privateConstructorUsedError;
  String get pincode => throw _privateConstructorUsedError;
  double get lat => throw _privateConstructorUsedError;
  double get lon => throw _privateConstructorUsedError;
  String get irrigationType => throw _privateConstructorUsedError;
  double get areaAcres => throw _privateConstructorUsedError;
  String get language => throw _privateConstructorUsedError;
  String get status => throw _privateConstructorUsedError;
  DateTime get plannedHarvestDate => throw _privateConstructorUsedError;
  DateTime? get actualHarvestDate => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;
  DateTime get updatedAt => throw _privateConstructorUsedError;
  Crop? get crop => throw _privateConstructorUsedError;
  List<GrowthStage>? get growthStages => throw _privateConstructorUsedError;
  List<CropTask>? get tasks => throw _privateConstructorUsedError;

  /// Serializes this CropCycle to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CropCycle
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CropCycleCopyWith<CropCycle> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CropCycleCopyWith<$Res> {
  factory $CropCycleCopyWith(CropCycle value, $Res Function(CropCycle) then) =
      _$CropCycleCopyWithImpl<$Res, CropCycle>;
  @useResult
  $Res call(
      {String id,
      String clientId,
      String cropId,
      String variety,
      DateTime startDate,
      String season,
      String pincode,
      double lat,
      double lon,
      String irrigationType,
      double areaAcres,
      String language,
      String status,
      DateTime plannedHarvestDate,
      DateTime? actualHarvestDate,
      DateTime createdAt,
      DateTime updatedAt,
      Crop? crop,
      List<GrowthStage>? growthStages,
      List<CropTask>? tasks});

  $CropCopyWith<$Res>? get crop;
}

/// @nodoc
class _$CropCycleCopyWithImpl<$Res, $Val extends CropCycle>
    implements $CropCycleCopyWith<$Res> {
  _$CropCycleCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CropCycle
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? clientId = null,
    Object? cropId = null,
    Object? variety = null,
    Object? startDate = null,
    Object? season = null,
    Object? pincode = null,
    Object? lat = null,
    Object? lon = null,
    Object? irrigationType = null,
    Object? areaAcres = null,
    Object? language = null,
    Object? status = null,
    Object? plannedHarvestDate = null,
    Object? actualHarvestDate = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
    Object? crop = freezed,
    Object? growthStages = freezed,
    Object? tasks = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      clientId: null == clientId
          ? _value.clientId
          : clientId // ignore: cast_nullable_to_non_nullable
              as String,
      cropId: null == cropId
          ? _value.cropId
          : cropId // ignore: cast_nullable_to_non_nullable
              as String,
      variety: null == variety
          ? _value.variety
          : variety // ignore: cast_nullable_to_non_nullable
              as String,
      startDate: null == startDate
          ? _value.startDate
          : startDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      season: null == season
          ? _value.season
          : season // ignore: cast_nullable_to_non_nullable
              as String,
      pincode: null == pincode
          ? _value.pincode
          : pincode // ignore: cast_nullable_to_non_nullable
              as String,
      lat: null == lat
          ? _value.lat
          : lat // ignore: cast_nullable_to_non_nullable
              as double,
      lon: null == lon
          ? _value.lon
          : lon // ignore: cast_nullable_to_non_nullable
              as double,
      irrigationType: null == irrigationType
          ? _value.irrigationType
          : irrigationType // ignore: cast_nullable_to_non_nullable
              as String,
      areaAcres: null == areaAcres
          ? _value.areaAcres
          : areaAcres // ignore: cast_nullable_to_non_nullable
              as double,
      language: null == language
          ? _value.language
          : language // ignore: cast_nullable_to_non_nullable
              as String,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      plannedHarvestDate: null == plannedHarvestDate
          ? _value.plannedHarvestDate
          : plannedHarvestDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      actualHarvestDate: freezed == actualHarvestDate
          ? _value.actualHarvestDate
          : actualHarvestDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      crop: freezed == crop
          ? _value.crop
          : crop // ignore: cast_nullable_to_non_nullable
              as Crop?,
      growthStages: freezed == growthStages
          ? _value.growthStages
          : growthStages // ignore: cast_nullable_to_non_nullable
              as List<GrowthStage>?,
      tasks: freezed == tasks
          ? _value.tasks
          : tasks // ignore: cast_nullable_to_non_nullable
              as List<CropTask>?,
    ) as $Val);
  }

  /// Create a copy of CropCycle
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $CropCopyWith<$Res>? get crop {
    if (_value.crop == null) {
      return null;
    }

    return $CropCopyWith<$Res>(_value.crop!, (value) {
      return _then(_value.copyWith(crop: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$CropCycleImplCopyWith<$Res>
    implements $CropCycleCopyWith<$Res> {
  factory _$$CropCycleImplCopyWith(
          _$CropCycleImpl value, $Res Function(_$CropCycleImpl) then) =
      __$$CropCycleImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String clientId,
      String cropId,
      String variety,
      DateTime startDate,
      String season,
      String pincode,
      double lat,
      double lon,
      String irrigationType,
      double areaAcres,
      String language,
      String status,
      DateTime plannedHarvestDate,
      DateTime? actualHarvestDate,
      DateTime createdAt,
      DateTime updatedAt,
      Crop? crop,
      List<GrowthStage>? growthStages,
      List<CropTask>? tasks});

  @override
  $CropCopyWith<$Res>? get crop;
}

/// @nodoc
class __$$CropCycleImplCopyWithImpl<$Res>
    extends _$CropCycleCopyWithImpl<$Res, _$CropCycleImpl>
    implements _$$CropCycleImplCopyWith<$Res> {
  __$$CropCycleImplCopyWithImpl(
      _$CropCycleImpl _value, $Res Function(_$CropCycleImpl) _then)
      : super(_value, _then);

  /// Create a copy of CropCycle
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? clientId = null,
    Object? cropId = null,
    Object? variety = null,
    Object? startDate = null,
    Object? season = null,
    Object? pincode = null,
    Object? lat = null,
    Object? lon = null,
    Object? irrigationType = null,
    Object? areaAcres = null,
    Object? language = null,
    Object? status = null,
    Object? plannedHarvestDate = null,
    Object? actualHarvestDate = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
    Object? crop = freezed,
    Object? growthStages = freezed,
    Object? tasks = freezed,
  }) {
    return _then(_$CropCycleImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      clientId: null == clientId
          ? _value.clientId
          : clientId // ignore: cast_nullable_to_non_nullable
              as String,
      cropId: null == cropId
          ? _value.cropId
          : cropId // ignore: cast_nullable_to_non_nullable
              as String,
      variety: null == variety
          ? _value.variety
          : variety // ignore: cast_nullable_to_non_nullable
              as String,
      startDate: null == startDate
          ? _value.startDate
          : startDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      season: null == season
          ? _value.season
          : season // ignore: cast_nullable_to_non_nullable
              as String,
      pincode: null == pincode
          ? _value.pincode
          : pincode // ignore: cast_nullable_to_non_nullable
              as String,
      lat: null == lat
          ? _value.lat
          : lat // ignore: cast_nullable_to_non_nullable
              as double,
      lon: null == lon
          ? _value.lon
          : lon // ignore: cast_nullable_to_non_nullable
              as double,
      irrigationType: null == irrigationType
          ? _value.irrigationType
          : irrigationType // ignore: cast_nullable_to_non_nullable
              as String,
      areaAcres: null == areaAcres
          ? _value.areaAcres
          : areaAcres // ignore: cast_nullable_to_non_nullable
              as double,
      language: null == language
          ? _value.language
          : language // ignore: cast_nullable_to_non_nullable
              as String,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      plannedHarvestDate: null == plannedHarvestDate
          ? _value.plannedHarvestDate
          : plannedHarvestDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      actualHarvestDate: freezed == actualHarvestDate
          ? _value.actualHarvestDate
          : actualHarvestDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      crop: freezed == crop
          ? _value.crop
          : crop // ignore: cast_nullable_to_non_nullable
              as Crop?,
      growthStages: freezed == growthStages
          ? _value._growthStages
          : growthStages // ignore: cast_nullable_to_non_nullable
              as List<GrowthStage>?,
      tasks: freezed == tasks
          ? _value._tasks
          : tasks // ignore: cast_nullable_to_non_nullable
              as List<CropTask>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CropCycleImpl implements _CropCycle {
  const _$CropCycleImpl(
      {required this.id,
      required this.clientId,
      required this.cropId,
      required this.variety,
      required this.startDate,
      required this.season,
      required this.pincode,
      required this.lat,
      required this.lon,
      required this.irrigationType,
      required this.areaAcres,
      required this.language,
      required this.status,
      required this.plannedHarvestDate,
      this.actualHarvestDate,
      required this.createdAt,
      required this.updatedAt,
      this.crop,
      final List<GrowthStage>? growthStages,
      final List<CropTask>? tasks})
      : _growthStages = growthStages,
        _tasks = tasks;

  factory _$CropCycleImpl.fromJson(Map<String, dynamic> json) =>
      _$$CropCycleImplFromJson(json);

  @override
  final String id;
  @override
  final String clientId;
  @override
  final String cropId;
  @override
  final String variety;
  @override
  final DateTime startDate;
  @override
  final String season;
  @override
  final String pincode;
  @override
  final double lat;
  @override
  final double lon;
  @override
  final String irrigationType;
  @override
  final double areaAcres;
  @override
  final String language;
  @override
  final String status;
  @override
  final DateTime plannedHarvestDate;
  @override
  final DateTime? actualHarvestDate;
  @override
  final DateTime createdAt;
  @override
  final DateTime updatedAt;
  @override
  final Crop? crop;
  final List<GrowthStage>? _growthStages;
  @override
  List<GrowthStage>? get growthStages {
    final value = _growthStages;
    if (value == null) return null;
    if (_growthStages is EqualUnmodifiableListView) return _growthStages;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  final List<CropTask>? _tasks;
  @override
  List<CropTask>? get tasks {
    final value = _tasks;
    if (value == null) return null;
    if (_tasks is EqualUnmodifiableListView) return _tasks;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  @override
  String toString() {
    return 'CropCycle(id: $id, clientId: $clientId, cropId: $cropId, variety: $variety, startDate: $startDate, season: $season, pincode: $pincode, lat: $lat, lon: $lon, irrigationType: $irrigationType, areaAcres: $areaAcres, language: $language, status: $status, plannedHarvestDate: $plannedHarvestDate, actualHarvestDate: $actualHarvestDate, createdAt: $createdAt, updatedAt: $updatedAt, crop: $crop, growthStages: $growthStages, tasks: $tasks)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CropCycleImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.clientId, clientId) ||
                other.clientId == clientId) &&
            (identical(other.cropId, cropId) || other.cropId == cropId) &&
            (identical(other.variety, variety) || other.variety == variety) &&
            (identical(other.startDate, startDate) ||
                other.startDate == startDate) &&
            (identical(other.season, season) || other.season == season) &&
            (identical(other.pincode, pincode) || other.pincode == pincode) &&
            (identical(other.lat, lat) || other.lat == lat) &&
            (identical(other.lon, lon) || other.lon == lon) &&
            (identical(other.irrigationType, irrigationType) ||
                other.irrigationType == irrigationType) &&
            (identical(other.areaAcres, areaAcres) ||
                other.areaAcres == areaAcres) &&
            (identical(other.language, language) ||
                other.language == language) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.plannedHarvestDate, plannedHarvestDate) ||
                other.plannedHarvestDate == plannedHarvestDate) &&
            (identical(other.actualHarvestDate, actualHarvestDate) ||
                other.actualHarvestDate == actualHarvestDate) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt) &&
            (identical(other.crop, crop) || other.crop == crop) &&
            const DeepCollectionEquality()
                .equals(other._growthStages, _growthStages) &&
            const DeepCollectionEquality().equals(other._tasks, _tasks));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hashAll([
        runtimeType,
        id,
        clientId,
        cropId,
        variety,
        startDate,
        season,
        pincode,
        lat,
        lon,
        irrigationType,
        areaAcres,
        language,
        status,
        plannedHarvestDate,
        actualHarvestDate,
        createdAt,
        updatedAt,
        crop,
        const DeepCollectionEquality().hash(_growthStages),
        const DeepCollectionEquality().hash(_tasks)
      ]);

  /// Create a copy of CropCycle
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CropCycleImplCopyWith<_$CropCycleImpl> get copyWith =>
      __$$CropCycleImplCopyWithImpl<_$CropCycleImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CropCycleImplToJson(
      this,
    );
  }
}

abstract class _CropCycle implements CropCycle {
  const factory _CropCycle(
      {required final String id,
      required final String clientId,
      required final String cropId,
      required final String variety,
      required final DateTime startDate,
      required final String season,
      required final String pincode,
      required final double lat,
      required final double lon,
      required final String irrigationType,
      required final double areaAcres,
      required final String language,
      required final String status,
      required final DateTime plannedHarvestDate,
      final DateTime? actualHarvestDate,
      required final DateTime createdAt,
      required final DateTime updatedAt,
      final Crop? crop,
      final List<GrowthStage>? growthStages,
      final List<CropTask>? tasks}) = _$CropCycleImpl;

  factory _CropCycle.fromJson(Map<String, dynamic> json) =
      _$CropCycleImpl.fromJson;

  @override
  String get id;
  @override
  String get clientId;
  @override
  String get cropId;
  @override
  String get variety;
  @override
  DateTime get startDate;
  @override
  String get season;
  @override
  String get pincode;
  @override
  double get lat;
  @override
  double get lon;
  @override
  String get irrigationType;
  @override
  double get areaAcres;
  @override
  String get language;
  @override
  String get status;
  @override
  DateTime get plannedHarvestDate;
  @override
  DateTime? get actualHarvestDate;
  @override
  DateTime get createdAt;
  @override
  DateTime get updatedAt;
  @override
  Crop? get crop;
  @override
  List<GrowthStage>? get growthStages;
  @override
  List<CropTask>? get tasks;

  /// Create a copy of CropCycle
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CropCycleImplCopyWith<_$CropCycleImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

Crop _$CropFromJson(Map<String, dynamic> json) {
  return _Crop.fromJson(json);
}

/// @nodoc
mixin _$Crop {
  String get id => throw _privateConstructorUsedError;
  String get nameEn => throw _privateConstructorUsedError;
  String get nameHi => throw _privateConstructorUsedError;
  String get nameKn => throw _privateConstructorUsedError;
  String get category => throw _privateConstructorUsedError;
  int get growthDurationDays => throw _privateConstructorUsedError;
  String get season => throw _privateConstructorUsedError;
  String get region => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  String get careInstructions => throw _privateConstructorUsedError;
  String get pestManagement => throw _privateConstructorUsedError;
  String get diseaseManagement => throw _privateConstructorUsedError;
  String get harvestingTips => throw _privateConstructorUsedError;
  String get storageTips => throw _privateConstructorUsedError;
  double get minTemperature => throw _privateConstructorUsedError;
  double get maxTemperature => throw _privateConstructorUsedError;
  double get minRainfall => throw _privateConstructorUsedError;
  double get maxRainfall => throw _privateConstructorUsedError;
  String get soilType => throw _privateConstructorUsedError;
  double get soilPhMin => throw _privateConstructorUsedError;
  double get soilPhMax => throw _privateConstructorUsedError;
  String get waterRequirement => throw _privateConstructorUsedError;
  String get fertilizerRequirement => throw _privateConstructorUsedError;
  String get seedRate => throw _privateConstructorUsedError;
  String get spacing => throw _privateConstructorUsedError;
  String get depth => throw _privateConstructorUsedError;
  String get thinning => throw _privateConstructorUsedError;
  String get weeding => throw _privateConstructorUsedError;
  String get irrigation => throw _privateConstructorUsedError;
  String get harvesting => throw _privateConstructorUsedError;
  String get postHarvest => throw _privateConstructorUsedError;
  String get marketDemand => throw _privateConstructorUsedError;
  double get expectedYield => throw _privateConstructorUsedError;
  String get unit => throw _privateConstructorUsedError;
  double get minPrice => throw _privateConstructorUsedError;
  double get maxPrice => throw _privateConstructorUsedError;
  String get currency => throw _privateConstructorUsedError;
  String get imageUrl => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;
  DateTime get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this Crop to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Crop
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CropCopyWith<Crop> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CropCopyWith<$Res> {
  factory $CropCopyWith(Crop value, $Res Function(Crop) then) =
      _$CropCopyWithImpl<$Res, Crop>;
  @useResult
  $Res call(
      {String id,
      String nameEn,
      String nameHi,
      String nameKn,
      String category,
      int growthDurationDays,
      String season,
      String region,
      String description,
      String careInstructions,
      String pestManagement,
      String diseaseManagement,
      String harvestingTips,
      String storageTips,
      double minTemperature,
      double maxTemperature,
      double minRainfall,
      double maxRainfall,
      String soilType,
      double soilPhMin,
      double soilPhMax,
      String waterRequirement,
      String fertilizerRequirement,
      String seedRate,
      String spacing,
      String depth,
      String thinning,
      String weeding,
      String irrigation,
      String harvesting,
      String postHarvest,
      String marketDemand,
      double expectedYield,
      String unit,
      double minPrice,
      double maxPrice,
      String currency,
      String imageUrl,
      DateTime createdAt,
      DateTime updatedAt});
}

/// @nodoc
class _$CropCopyWithImpl<$Res, $Val extends Crop>
    implements $CropCopyWith<$Res> {
  _$CropCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Crop
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? nameEn = null,
    Object? nameHi = null,
    Object? nameKn = null,
    Object? category = null,
    Object? growthDurationDays = null,
    Object? season = null,
    Object? region = null,
    Object? description = null,
    Object? careInstructions = null,
    Object? pestManagement = null,
    Object? diseaseManagement = null,
    Object? harvestingTips = null,
    Object? storageTips = null,
    Object? minTemperature = null,
    Object? maxTemperature = null,
    Object? minRainfall = null,
    Object? maxRainfall = null,
    Object? soilType = null,
    Object? soilPhMin = null,
    Object? soilPhMax = null,
    Object? waterRequirement = null,
    Object? fertilizerRequirement = null,
    Object? seedRate = null,
    Object? spacing = null,
    Object? depth = null,
    Object? thinning = null,
    Object? weeding = null,
    Object? irrigation = null,
    Object? harvesting = null,
    Object? postHarvest = null,
    Object? marketDemand = null,
    Object? expectedYield = null,
    Object? unit = null,
    Object? minPrice = null,
    Object? maxPrice = null,
    Object? currency = null,
    Object? imageUrl = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      nameEn: null == nameEn
          ? _value.nameEn
          : nameEn // ignore: cast_nullable_to_non_nullable
              as String,
      nameHi: null == nameHi
          ? _value.nameHi
          : nameHi // ignore: cast_nullable_to_non_nullable
              as String,
      nameKn: null == nameKn
          ? _value.nameKn
          : nameKn // ignore: cast_nullable_to_non_nullable
              as String,
      category: null == category
          ? _value.category
          : category // ignore: cast_nullable_to_non_nullable
              as String,
      growthDurationDays: null == growthDurationDays
          ? _value.growthDurationDays
          : growthDurationDays // ignore: cast_nullable_to_non_nullable
              as int,
      season: null == season
          ? _value.season
          : season // ignore: cast_nullable_to_non_nullable
              as String,
      region: null == region
          ? _value.region
          : region // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      careInstructions: null == careInstructions
          ? _value.careInstructions
          : careInstructions // ignore: cast_nullable_to_non_nullable
              as String,
      pestManagement: null == pestManagement
          ? _value.pestManagement
          : pestManagement // ignore: cast_nullable_to_non_nullable
              as String,
      diseaseManagement: null == diseaseManagement
          ? _value.diseaseManagement
          : diseaseManagement // ignore: cast_nullable_to_non_nullable
              as String,
      harvestingTips: null == harvestingTips
          ? _value.harvestingTips
          : harvestingTips // ignore: cast_nullable_to_non_nullable
              as String,
      storageTips: null == storageTips
          ? _value.storageTips
          : storageTips // ignore: cast_nullable_to_non_nullable
              as String,
      minTemperature: null == minTemperature
          ? _value.minTemperature
          : minTemperature // ignore: cast_nullable_to_non_nullable
              as double,
      maxTemperature: null == maxTemperature
          ? _value.maxTemperature
          : maxTemperature // ignore: cast_nullable_to_non_nullable
              as double,
      minRainfall: null == minRainfall
          ? _value.minRainfall
          : minRainfall // ignore: cast_nullable_to_non_nullable
              as double,
      maxRainfall: null == maxRainfall
          ? _value.maxRainfall
          : maxRainfall // ignore: cast_nullable_to_non_nullable
              as double,
      soilType: null == soilType
          ? _value.soilType
          : soilType // ignore: cast_nullable_to_non_nullable
              as String,
      soilPhMin: null == soilPhMin
          ? _value.soilPhMin
          : soilPhMin // ignore: cast_nullable_to_non_nullable
              as double,
      soilPhMax: null == soilPhMax
          ? _value.soilPhMax
          : soilPhMax // ignore: cast_nullable_to_non_nullable
              as double,
      waterRequirement: null == waterRequirement
          ? _value.waterRequirement
          : waterRequirement // ignore: cast_nullable_to_non_nullable
              as String,
      fertilizerRequirement: null == fertilizerRequirement
          ? _value.fertilizerRequirement
          : fertilizerRequirement // ignore: cast_nullable_to_non_nullable
              as String,
      seedRate: null == seedRate
          ? _value.seedRate
          : seedRate // ignore: cast_nullable_to_non_nullable
              as String,
      spacing: null == spacing
          ? _value.spacing
          : spacing // ignore: cast_nullable_to_non_nullable
              as String,
      depth: null == depth
          ? _value.depth
          : depth // ignore: cast_nullable_to_non_nullable
              as String,
      thinning: null == thinning
          ? _value.thinning
          : thinning // ignore: cast_nullable_to_non_nullable
              as String,
      weeding: null == weeding
          ? _value.weeding
          : weeding // ignore: cast_nullable_to_non_nullable
              as String,
      irrigation: null == irrigation
          ? _value.irrigation
          : irrigation // ignore: cast_nullable_to_non_nullable
              as String,
      harvesting: null == harvesting
          ? _value.harvesting
          : harvesting // ignore: cast_nullable_to_non_nullable
              as String,
      postHarvest: null == postHarvest
          ? _value.postHarvest
          : postHarvest // ignore: cast_nullable_to_non_nullable
              as String,
      marketDemand: null == marketDemand
          ? _value.marketDemand
          : marketDemand // ignore: cast_nullable_to_non_nullable
              as String,
      expectedYield: null == expectedYield
          ? _value.expectedYield
          : expectedYield // ignore: cast_nullable_to_non_nullable
              as double,
      unit: null == unit
          ? _value.unit
          : unit // ignore: cast_nullable_to_non_nullable
              as String,
      minPrice: null == minPrice
          ? _value.minPrice
          : minPrice // ignore: cast_nullable_to_non_nullable
              as double,
      maxPrice: null == maxPrice
          ? _value.maxPrice
          : maxPrice // ignore: cast_nullable_to_non_nullable
              as double,
      currency: null == currency
          ? _value.currency
          : currency // ignore: cast_nullable_to_non_nullable
              as String,
      imageUrl: null == imageUrl
          ? _value.imageUrl
          : imageUrl // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CropImplCopyWith<$Res> implements $CropCopyWith<$Res> {
  factory _$$CropImplCopyWith(
          _$CropImpl value, $Res Function(_$CropImpl) then) =
      __$$CropImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String nameEn,
      String nameHi,
      String nameKn,
      String category,
      int growthDurationDays,
      String season,
      String region,
      String description,
      String careInstructions,
      String pestManagement,
      String diseaseManagement,
      String harvestingTips,
      String storageTips,
      double minTemperature,
      double maxTemperature,
      double minRainfall,
      double maxRainfall,
      String soilType,
      double soilPhMin,
      double soilPhMax,
      String waterRequirement,
      String fertilizerRequirement,
      String seedRate,
      String spacing,
      String depth,
      String thinning,
      String weeding,
      String irrigation,
      String harvesting,
      String postHarvest,
      String marketDemand,
      double expectedYield,
      String unit,
      double minPrice,
      double maxPrice,
      String currency,
      String imageUrl,
      DateTime createdAt,
      DateTime updatedAt});
}

/// @nodoc
class __$$CropImplCopyWithImpl<$Res>
    extends _$CropCopyWithImpl<$Res, _$CropImpl>
    implements _$$CropImplCopyWith<$Res> {
  __$$CropImplCopyWithImpl(_$CropImpl _value, $Res Function(_$CropImpl) _then)
      : super(_value, _then);

  /// Create a copy of Crop
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? nameEn = null,
    Object? nameHi = null,
    Object? nameKn = null,
    Object? category = null,
    Object? growthDurationDays = null,
    Object? season = null,
    Object? region = null,
    Object? description = null,
    Object? careInstructions = null,
    Object? pestManagement = null,
    Object? diseaseManagement = null,
    Object? harvestingTips = null,
    Object? storageTips = null,
    Object? minTemperature = null,
    Object? maxTemperature = null,
    Object? minRainfall = null,
    Object? maxRainfall = null,
    Object? soilType = null,
    Object? soilPhMin = null,
    Object? soilPhMax = null,
    Object? waterRequirement = null,
    Object? fertilizerRequirement = null,
    Object? seedRate = null,
    Object? spacing = null,
    Object? depth = null,
    Object? thinning = null,
    Object? weeding = null,
    Object? irrigation = null,
    Object? harvesting = null,
    Object? postHarvest = null,
    Object? marketDemand = null,
    Object? expectedYield = null,
    Object? unit = null,
    Object? minPrice = null,
    Object? maxPrice = null,
    Object? currency = null,
    Object? imageUrl = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$CropImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      nameEn: null == nameEn
          ? _value.nameEn
          : nameEn // ignore: cast_nullable_to_non_nullable
              as String,
      nameHi: null == nameHi
          ? _value.nameHi
          : nameHi // ignore: cast_nullable_to_non_nullable
              as String,
      nameKn: null == nameKn
          ? _value.nameKn
          : nameKn // ignore: cast_nullable_to_non_nullable
              as String,
      category: null == category
          ? _value.category
          : category // ignore: cast_nullable_to_non_nullable
              as String,
      growthDurationDays: null == growthDurationDays
          ? _value.growthDurationDays
          : growthDurationDays // ignore: cast_nullable_to_non_nullable
              as int,
      season: null == season
          ? _value.season
          : season // ignore: cast_nullable_to_non_nullable
              as String,
      region: null == region
          ? _value.region
          : region // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      careInstructions: null == careInstructions
          ? _value.careInstructions
          : careInstructions // ignore: cast_nullable_to_non_nullable
              as String,
      pestManagement: null == pestManagement
          ? _value.pestManagement
          : pestManagement // ignore: cast_nullable_to_non_nullable
              as String,
      diseaseManagement: null == diseaseManagement
          ? _value.diseaseManagement
          : diseaseManagement // ignore: cast_nullable_to_non_nullable
              as String,
      harvestingTips: null == harvestingTips
          ? _value.harvestingTips
          : harvestingTips // ignore: cast_nullable_to_non_nullable
              as String,
      storageTips: null == storageTips
          ? _value.storageTips
          : storageTips // ignore: cast_nullable_to_non_nullable
              as String,
      minTemperature: null == minTemperature
          ? _value.minTemperature
          : minTemperature // ignore: cast_nullable_to_non_nullable
              as double,
      maxTemperature: null == maxTemperature
          ? _value.maxTemperature
          : maxTemperature // ignore: cast_nullable_to_non_nullable
              as double,
      minRainfall: null == minRainfall
          ? _value.minRainfall
          : minRainfall // ignore: cast_nullable_to_non_nullable
              as double,
      maxRainfall: null == maxRainfall
          ? _value.maxRainfall
          : maxRainfall // ignore: cast_nullable_to_non_nullable
              as double,
      soilType: null == soilType
          ? _value.soilType
          : soilType // ignore: cast_nullable_to_non_nullable
              as String,
      soilPhMin: null == soilPhMin
          ? _value.soilPhMin
          : soilPhMin // ignore: cast_nullable_to_non_nullable
              as double,
      soilPhMax: null == soilPhMax
          ? _value.soilPhMax
          : soilPhMax // ignore: cast_nullable_to_non_nullable
              as double,
      waterRequirement: null == waterRequirement
          ? _value.waterRequirement
          : waterRequirement // ignore: cast_nullable_to_non_nullable
              as String,
      fertilizerRequirement: null == fertilizerRequirement
          ? _value.fertilizerRequirement
          : fertilizerRequirement // ignore: cast_nullable_to_non_nullable
              as String,
      seedRate: null == seedRate
          ? _value.seedRate
          : seedRate // ignore: cast_nullable_to_non_nullable
              as String,
      spacing: null == spacing
          ? _value.spacing
          : spacing // ignore: cast_nullable_to_non_nullable
              as String,
      depth: null == depth
          ? _value.depth
          : depth // ignore: cast_nullable_to_non_nullable
              as String,
      thinning: null == thinning
          ? _value.thinning
          : thinning // ignore: cast_nullable_to_non_nullable
              as String,
      weeding: null == weeding
          ? _value.weeding
          : weeding // ignore: cast_nullable_to_non_nullable
              as String,
      irrigation: null == irrigation
          ? _value.irrigation
          : irrigation // ignore: cast_nullable_to_non_nullable
              as String,
      harvesting: null == harvesting
          ? _value.harvesting
          : harvesting // ignore: cast_nullable_to_non_nullable
              as String,
      postHarvest: null == postHarvest
          ? _value.postHarvest
          : postHarvest // ignore: cast_nullable_to_non_nullable
              as String,
      marketDemand: null == marketDemand
          ? _value.marketDemand
          : marketDemand // ignore: cast_nullable_to_non_nullable
              as String,
      expectedYield: null == expectedYield
          ? _value.expectedYield
          : expectedYield // ignore: cast_nullable_to_non_nullable
              as double,
      unit: null == unit
          ? _value.unit
          : unit // ignore: cast_nullable_to_non_nullable
              as String,
      minPrice: null == minPrice
          ? _value.minPrice
          : minPrice // ignore: cast_nullable_to_non_nullable
              as double,
      maxPrice: null == maxPrice
          ? _value.maxPrice
          : maxPrice // ignore: cast_nullable_to_non_nullable
              as double,
      currency: null == currency
          ? _value.currency
          : currency // ignore: cast_nullable_to_non_nullable
              as String,
      imageUrl: null == imageUrl
          ? _value.imageUrl
          : imageUrl // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CropImpl implements _Crop {
  const _$CropImpl(
      {required this.id,
      required this.nameEn,
      required this.nameHi,
      required this.nameKn,
      required this.category,
      required this.growthDurationDays,
      required this.season,
      required this.region,
      required this.description,
      required this.careInstructions,
      required this.pestManagement,
      required this.diseaseManagement,
      required this.harvestingTips,
      required this.storageTips,
      required this.minTemperature,
      required this.maxTemperature,
      required this.minRainfall,
      required this.maxRainfall,
      required this.soilType,
      required this.soilPhMin,
      required this.soilPhMax,
      required this.waterRequirement,
      required this.fertilizerRequirement,
      required this.seedRate,
      required this.spacing,
      required this.depth,
      required this.thinning,
      required this.weeding,
      required this.irrigation,
      required this.harvesting,
      required this.postHarvest,
      required this.marketDemand,
      required this.expectedYield,
      required this.unit,
      required this.minPrice,
      required this.maxPrice,
      required this.currency,
      required this.imageUrl,
      required this.createdAt,
      required this.updatedAt});

  factory _$CropImpl.fromJson(Map<String, dynamic> json) =>
      _$$CropImplFromJson(json);

  @override
  final String id;
  @override
  final String nameEn;
  @override
  final String nameHi;
  @override
  final String nameKn;
  @override
  final String category;
  @override
  final int growthDurationDays;
  @override
  final String season;
  @override
  final String region;
  @override
  final String description;
  @override
  final String careInstructions;
  @override
  final String pestManagement;
  @override
  final String diseaseManagement;
  @override
  final String harvestingTips;
  @override
  final String storageTips;
  @override
  final double minTemperature;
  @override
  final double maxTemperature;
  @override
  final double minRainfall;
  @override
  final double maxRainfall;
  @override
  final String soilType;
  @override
  final double soilPhMin;
  @override
  final double soilPhMax;
  @override
  final String waterRequirement;
  @override
  final String fertilizerRequirement;
  @override
  final String seedRate;
  @override
  final String spacing;
  @override
  final String depth;
  @override
  final String thinning;
  @override
  final String weeding;
  @override
  final String irrigation;
  @override
  final String harvesting;
  @override
  final String postHarvest;
  @override
  final String marketDemand;
  @override
  final double expectedYield;
  @override
  final String unit;
  @override
  final double minPrice;
  @override
  final double maxPrice;
  @override
  final String currency;
  @override
  final String imageUrl;
  @override
  final DateTime createdAt;
  @override
  final DateTime updatedAt;

  @override
  String toString() {
    return 'Crop(id: $id, nameEn: $nameEn, nameHi: $nameHi, nameKn: $nameKn, category: $category, growthDurationDays: $growthDurationDays, season: $season, region: $region, description: $description, careInstructions: $careInstructions, pestManagement: $pestManagement, diseaseManagement: $diseaseManagement, harvestingTips: $harvestingTips, storageTips: $storageTips, minTemperature: $minTemperature, maxTemperature: $maxTemperature, minRainfall: $minRainfall, maxRainfall: $maxRainfall, soilType: $soilType, soilPhMin: $soilPhMin, soilPhMax: $soilPhMax, waterRequirement: $waterRequirement, fertilizerRequirement: $fertilizerRequirement, seedRate: $seedRate, spacing: $spacing, depth: $depth, thinning: $thinning, weeding: $weeding, irrigation: $irrigation, harvesting: $harvesting, postHarvest: $postHarvest, marketDemand: $marketDemand, expectedYield: $expectedYield, unit: $unit, minPrice: $minPrice, maxPrice: $maxPrice, currency: $currency, imageUrl: $imageUrl, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CropImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.nameEn, nameEn) || other.nameEn == nameEn) &&
            (identical(other.nameHi, nameHi) || other.nameHi == nameHi) &&
            (identical(other.nameKn, nameKn) || other.nameKn == nameKn) &&
            (identical(other.category, category) ||
                other.category == category) &&
            (identical(other.growthDurationDays, growthDurationDays) ||
                other.growthDurationDays == growthDurationDays) &&
            (identical(other.season, season) || other.season == season) &&
            (identical(other.region, region) || other.region == region) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.careInstructions, careInstructions) ||
                other.careInstructions == careInstructions) &&
            (identical(other.pestManagement, pestManagement) ||
                other.pestManagement == pestManagement) &&
            (identical(other.diseaseManagement, diseaseManagement) ||
                other.diseaseManagement == diseaseManagement) &&
            (identical(other.harvestingTips, harvestingTips) ||
                other.harvestingTips == harvestingTips) &&
            (identical(other.storageTips, storageTips) ||
                other.storageTips == storageTips) &&
            (identical(other.minTemperature, minTemperature) ||
                other.minTemperature == minTemperature) &&
            (identical(other.maxTemperature, maxTemperature) ||
                other.maxTemperature == maxTemperature) &&
            (identical(other.minRainfall, minRainfall) ||
                other.minRainfall == minRainfall) &&
            (identical(other.maxRainfall, maxRainfall) ||
                other.maxRainfall == maxRainfall) &&
            (identical(other.soilType, soilType) ||
                other.soilType == soilType) &&
            (identical(other.soilPhMin, soilPhMin) ||
                other.soilPhMin == soilPhMin) &&
            (identical(other.soilPhMax, soilPhMax) ||
                other.soilPhMax == soilPhMax) &&
            (identical(other.waterRequirement, waterRequirement) ||
                other.waterRequirement == waterRequirement) &&
            (identical(other.fertilizerRequirement, fertilizerRequirement) ||
                other.fertilizerRequirement == fertilizerRequirement) &&
            (identical(other.seedRate, seedRate) ||
                other.seedRate == seedRate) &&
            (identical(other.spacing, spacing) || other.spacing == spacing) &&
            (identical(other.depth, depth) || other.depth == depth) &&
            (identical(other.thinning, thinning) ||
                other.thinning == thinning) &&
            (identical(other.weeding, weeding) || other.weeding == weeding) &&
            (identical(other.irrigation, irrigation) ||
                other.irrigation == irrigation) &&
            (identical(other.harvesting, harvesting) ||
                other.harvesting == harvesting) &&
            (identical(other.postHarvest, postHarvest) ||
                other.postHarvest == postHarvest) &&
            (identical(other.marketDemand, marketDemand) ||
                other.marketDemand == marketDemand) &&
            (identical(other.expectedYield, expectedYield) ||
                other.expectedYield == expectedYield) &&
            (identical(other.unit, unit) || other.unit == unit) &&
            (identical(other.minPrice, minPrice) ||
                other.minPrice == minPrice) &&
            (identical(other.maxPrice, maxPrice) ||
                other.maxPrice == maxPrice) &&
            (identical(other.currency, currency) ||
                other.currency == currency) &&
            (identical(other.imageUrl, imageUrl) ||
                other.imageUrl == imageUrl) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hashAll([
        runtimeType,
        id,
        nameEn,
        nameHi,
        nameKn,
        category,
        growthDurationDays,
        season,
        region,
        description,
        careInstructions,
        pestManagement,
        diseaseManagement,
        harvestingTips,
        storageTips,
        minTemperature,
        maxTemperature,
        minRainfall,
        maxRainfall,
        soilType,
        soilPhMin,
        soilPhMax,
        waterRequirement,
        fertilizerRequirement,
        seedRate,
        spacing,
        depth,
        thinning,
        weeding,
        irrigation,
        harvesting,
        postHarvest,
        marketDemand,
        expectedYield,
        unit,
        minPrice,
        maxPrice,
        currency,
        imageUrl,
        createdAt,
        updatedAt
      ]);

  /// Create a copy of Crop
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CropImplCopyWith<_$CropImpl> get copyWith =>
      __$$CropImplCopyWithImpl<_$CropImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CropImplToJson(
      this,
    );
  }
}

abstract class _Crop implements Crop {
  const factory _Crop(
      {required final String id,
      required final String nameEn,
      required final String nameHi,
      required final String nameKn,
      required final String category,
      required final int growthDurationDays,
      required final String season,
      required final String region,
      required final String description,
      required final String careInstructions,
      required final String pestManagement,
      required final String diseaseManagement,
      required final String harvestingTips,
      required final String storageTips,
      required final double minTemperature,
      required final double maxTemperature,
      required final double minRainfall,
      required final double maxRainfall,
      required final String soilType,
      required final double soilPhMin,
      required final double soilPhMax,
      required final String waterRequirement,
      required final String fertilizerRequirement,
      required final String seedRate,
      required final String spacing,
      required final String depth,
      required final String thinning,
      required final String weeding,
      required final String irrigation,
      required final String harvesting,
      required final String postHarvest,
      required final String marketDemand,
      required final double expectedYield,
      required final String unit,
      required final double minPrice,
      required final double maxPrice,
      required final String currency,
      required final String imageUrl,
      required final DateTime createdAt,
      required final DateTime updatedAt}) = _$CropImpl;

  factory _Crop.fromJson(Map<String, dynamic> json) = _$CropImpl.fromJson;

  @override
  String get id;
  @override
  String get nameEn;
  @override
  String get nameHi;
  @override
  String get nameKn;
  @override
  String get category;
  @override
  int get growthDurationDays;
  @override
  String get season;
  @override
  String get region;
  @override
  String get description;
  @override
  String get careInstructions;
  @override
  String get pestManagement;
  @override
  String get diseaseManagement;
  @override
  String get harvestingTips;
  @override
  String get storageTips;
  @override
  double get minTemperature;
  @override
  double get maxTemperature;
  @override
  double get minRainfall;
  @override
  double get maxRainfall;
  @override
  String get soilType;
  @override
  double get soilPhMin;
  @override
  double get soilPhMax;
  @override
  String get waterRequirement;
  @override
  String get fertilizerRequirement;
  @override
  String get seedRate;
  @override
  String get spacing;
  @override
  String get depth;
  @override
  String get thinning;
  @override
  String get weeding;
  @override
  String get irrigation;
  @override
  String get harvesting;
  @override
  String get postHarvest;
  @override
  String get marketDemand;
  @override
  double get expectedYield;
  @override
  String get unit;
  @override
  double get minPrice;
  @override
  double get maxPrice;
  @override
  String get currency;
  @override
  String get imageUrl;
  @override
  DateTime get createdAt;
  @override
  DateTime get updatedAt;

  /// Create a copy of Crop
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CropImplCopyWith<_$CropImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

GrowthStage _$GrowthStageFromJson(Map<String, dynamic> json) {
  return _GrowthStage.fromJson(json);
}

/// @nodoc
mixin _$GrowthStage {
  String get id => throw _privateConstructorUsedError;
  String get cycleId => throw _privateConstructorUsedError;
  String get stageName => throw _privateConstructorUsedError;
  DateTime get expectedStartDate => throw _privateConstructorUsedError;
  DateTime? get actualStartDate => throw _privateConstructorUsedError;
  int get expectedDurationDays => throw _privateConstructorUsedError;
  double get progressPercentage => throw _privateConstructorUsedError;
  String? get notes => throw _privateConstructorUsedError;
  List<String>? get photos => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;

  /// Serializes this GrowthStage to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of GrowthStage
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $GrowthStageCopyWith<GrowthStage> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $GrowthStageCopyWith<$Res> {
  factory $GrowthStageCopyWith(
          GrowthStage value, $Res Function(GrowthStage) then) =
      _$GrowthStageCopyWithImpl<$Res, GrowthStage>;
  @useResult
  $Res call(
      {String id,
      String cycleId,
      String stageName,
      DateTime expectedStartDate,
      DateTime? actualStartDate,
      int expectedDurationDays,
      double progressPercentage,
      String? notes,
      List<String>? photos,
      DateTime createdAt});
}

/// @nodoc
class _$GrowthStageCopyWithImpl<$Res, $Val extends GrowthStage>
    implements $GrowthStageCopyWith<$Res> {
  _$GrowthStageCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of GrowthStage
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? cycleId = null,
    Object? stageName = null,
    Object? expectedStartDate = null,
    Object? actualStartDate = freezed,
    Object? expectedDurationDays = null,
    Object? progressPercentage = null,
    Object? notes = freezed,
    Object? photos = freezed,
    Object? createdAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      cycleId: null == cycleId
          ? _value.cycleId
          : cycleId // ignore: cast_nullable_to_non_nullable
              as String,
      stageName: null == stageName
          ? _value.stageName
          : stageName // ignore: cast_nullable_to_non_nullable
              as String,
      expectedStartDate: null == expectedStartDate
          ? _value.expectedStartDate
          : expectedStartDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      actualStartDate: freezed == actualStartDate
          ? _value.actualStartDate
          : actualStartDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      expectedDurationDays: null == expectedDurationDays
          ? _value.expectedDurationDays
          : expectedDurationDays // ignore: cast_nullable_to_non_nullable
              as int,
      progressPercentage: null == progressPercentage
          ? _value.progressPercentage
          : progressPercentage // ignore: cast_nullable_to_non_nullable
              as double,
      notes: freezed == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String?,
      photos: freezed == photos
          ? _value.photos
          : photos // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$GrowthStageImplCopyWith<$Res>
    implements $GrowthStageCopyWith<$Res> {
  factory _$$GrowthStageImplCopyWith(
          _$GrowthStageImpl value, $Res Function(_$GrowthStageImpl) then) =
      __$$GrowthStageImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String cycleId,
      String stageName,
      DateTime expectedStartDate,
      DateTime? actualStartDate,
      int expectedDurationDays,
      double progressPercentage,
      String? notes,
      List<String>? photos,
      DateTime createdAt});
}

/// @nodoc
class __$$GrowthStageImplCopyWithImpl<$Res>
    extends _$GrowthStageCopyWithImpl<$Res, _$GrowthStageImpl>
    implements _$$GrowthStageImplCopyWith<$Res> {
  __$$GrowthStageImplCopyWithImpl(
      _$GrowthStageImpl _value, $Res Function(_$GrowthStageImpl) _then)
      : super(_value, _then);

  /// Create a copy of GrowthStage
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? cycleId = null,
    Object? stageName = null,
    Object? expectedStartDate = null,
    Object? actualStartDate = freezed,
    Object? expectedDurationDays = null,
    Object? progressPercentage = null,
    Object? notes = freezed,
    Object? photos = freezed,
    Object? createdAt = null,
  }) {
    return _then(_$GrowthStageImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      cycleId: null == cycleId
          ? _value.cycleId
          : cycleId // ignore: cast_nullable_to_non_nullable
              as String,
      stageName: null == stageName
          ? _value.stageName
          : stageName // ignore: cast_nullable_to_non_nullable
              as String,
      expectedStartDate: null == expectedStartDate
          ? _value.expectedStartDate
          : expectedStartDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      actualStartDate: freezed == actualStartDate
          ? _value.actualStartDate
          : actualStartDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      expectedDurationDays: null == expectedDurationDays
          ? _value.expectedDurationDays
          : expectedDurationDays // ignore: cast_nullable_to_non_nullable
              as int,
      progressPercentage: null == progressPercentage
          ? _value.progressPercentage
          : progressPercentage // ignore: cast_nullable_to_non_nullable
              as double,
      notes: freezed == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String?,
      photos: freezed == photos
          ? _value._photos
          : photos // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$GrowthStageImpl implements _GrowthStage {
  const _$GrowthStageImpl(
      {required this.id,
      required this.cycleId,
      required this.stageName,
      required this.expectedStartDate,
      this.actualStartDate,
      required this.expectedDurationDays,
      required this.progressPercentage,
      this.notes,
      final List<String>? photos,
      required this.createdAt})
      : _photos = photos;

  factory _$GrowthStageImpl.fromJson(Map<String, dynamic> json) =>
      _$$GrowthStageImplFromJson(json);

  @override
  final String id;
  @override
  final String cycleId;
  @override
  final String stageName;
  @override
  final DateTime expectedStartDate;
  @override
  final DateTime? actualStartDate;
  @override
  final int expectedDurationDays;
  @override
  final double progressPercentage;
  @override
  final String? notes;
  final List<String>? _photos;
  @override
  List<String>? get photos {
    final value = _photos;
    if (value == null) return null;
    if (_photos is EqualUnmodifiableListView) return _photos;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  @override
  final DateTime createdAt;

  @override
  String toString() {
    return 'GrowthStage(id: $id, cycleId: $cycleId, stageName: $stageName, expectedStartDate: $expectedStartDate, actualStartDate: $actualStartDate, expectedDurationDays: $expectedDurationDays, progressPercentage: $progressPercentage, notes: $notes, photos: $photos, createdAt: $createdAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$GrowthStageImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.cycleId, cycleId) || other.cycleId == cycleId) &&
            (identical(other.stageName, stageName) ||
                other.stageName == stageName) &&
            (identical(other.expectedStartDate, expectedStartDate) ||
                other.expectedStartDate == expectedStartDate) &&
            (identical(other.actualStartDate, actualStartDate) ||
                other.actualStartDate == actualStartDate) &&
            (identical(other.expectedDurationDays, expectedDurationDays) ||
                other.expectedDurationDays == expectedDurationDays) &&
            (identical(other.progressPercentage, progressPercentage) ||
                other.progressPercentage == progressPercentage) &&
            (identical(other.notes, notes) || other.notes == notes) &&
            const DeepCollectionEquality().equals(other._photos, _photos) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      cycleId,
      stageName,
      expectedStartDate,
      actualStartDate,
      expectedDurationDays,
      progressPercentage,
      notes,
      const DeepCollectionEquality().hash(_photos),
      createdAt);

  /// Create a copy of GrowthStage
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$GrowthStageImplCopyWith<_$GrowthStageImpl> get copyWith =>
      __$$GrowthStageImplCopyWithImpl<_$GrowthStageImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$GrowthStageImplToJson(
      this,
    );
  }
}

abstract class _GrowthStage implements GrowthStage {
  const factory _GrowthStage(
      {required final String id,
      required final String cycleId,
      required final String stageName,
      required final DateTime expectedStartDate,
      final DateTime? actualStartDate,
      required final int expectedDurationDays,
      required final double progressPercentage,
      final String? notes,
      final List<String>? photos,
      required final DateTime createdAt}) = _$GrowthStageImpl;

  factory _GrowthStage.fromJson(Map<String, dynamic> json) =
      _$GrowthStageImpl.fromJson;

  @override
  String get id;
  @override
  String get cycleId;
  @override
  String get stageName;
  @override
  DateTime get expectedStartDate;
  @override
  DateTime? get actualStartDate;
  @override
  int get expectedDurationDays;
  @override
  double get progressPercentage;
  @override
  String? get notes;
  @override
  List<String>? get photos;
  @override
  DateTime get createdAt;

  /// Create a copy of GrowthStage
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$GrowthStageImplCopyWith<_$GrowthStageImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CropTask _$CropTaskFromJson(Map<String, dynamic> json) {
  return _CropTask.fromJson(json);
}

/// @nodoc
mixin _$CropTask {
  String get id => throw _privateConstructorUsedError;
  String get cycleId => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  String get priority => throw _privateConstructorUsedError;
  DateTime get dueDate => throw _privateConstructorUsedError;
  String get status => throw _privateConstructorUsedError;
  int get estimatedHours => throw _privateConstructorUsedError;
  String? get notes => throw _privateConstructorUsedError;
  List<String>? get photos => throw _privateConstructorUsedError;
  String? get voiceNote => throw _privateConstructorUsedError;
  DateTime? get completedAt => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;
  DateTime get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this CropTask to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CropTask
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CropTaskCopyWith<CropTask> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CropTaskCopyWith<$Res> {
  factory $CropTaskCopyWith(CropTask value, $Res Function(CropTask) then) =
      _$CropTaskCopyWithImpl<$Res, CropTask>;
  @useResult
  $Res call(
      {String id,
      String cycleId,
      String title,
      String description,
      String priority,
      DateTime dueDate,
      String status,
      int estimatedHours,
      String? notes,
      List<String>? photos,
      String? voiceNote,
      DateTime? completedAt,
      DateTime createdAt,
      DateTime updatedAt});
}

/// @nodoc
class _$CropTaskCopyWithImpl<$Res, $Val extends CropTask>
    implements $CropTaskCopyWith<$Res> {
  _$CropTaskCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CropTask
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? cycleId = null,
    Object? title = null,
    Object? description = null,
    Object? priority = null,
    Object? dueDate = null,
    Object? status = null,
    Object? estimatedHours = null,
    Object? notes = freezed,
    Object? photos = freezed,
    Object? voiceNote = freezed,
    Object? completedAt = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      cycleId: null == cycleId
          ? _value.cycleId
          : cycleId // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      priority: null == priority
          ? _value.priority
          : priority // ignore: cast_nullable_to_non_nullable
              as String,
      dueDate: null == dueDate
          ? _value.dueDate
          : dueDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      estimatedHours: null == estimatedHours
          ? _value.estimatedHours
          : estimatedHours // ignore: cast_nullable_to_non_nullable
              as int,
      notes: freezed == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String?,
      photos: freezed == photos
          ? _value.photos
          : photos // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      voiceNote: freezed == voiceNote
          ? _value.voiceNote
          : voiceNote // ignore: cast_nullable_to_non_nullable
              as String?,
      completedAt: freezed == completedAt
          ? _value.completedAt
          : completedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CropTaskImplCopyWith<$Res>
    implements $CropTaskCopyWith<$Res> {
  factory _$$CropTaskImplCopyWith(
          _$CropTaskImpl value, $Res Function(_$CropTaskImpl) then) =
      __$$CropTaskImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String cycleId,
      String title,
      String description,
      String priority,
      DateTime dueDate,
      String status,
      int estimatedHours,
      String? notes,
      List<String>? photos,
      String? voiceNote,
      DateTime? completedAt,
      DateTime createdAt,
      DateTime updatedAt});
}

/// @nodoc
class __$$CropTaskImplCopyWithImpl<$Res>
    extends _$CropTaskCopyWithImpl<$Res, _$CropTaskImpl>
    implements _$$CropTaskImplCopyWith<$Res> {
  __$$CropTaskImplCopyWithImpl(
      _$CropTaskImpl _value, $Res Function(_$CropTaskImpl) _then)
      : super(_value, _then);

  /// Create a copy of CropTask
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? cycleId = null,
    Object? title = null,
    Object? description = null,
    Object? priority = null,
    Object? dueDate = null,
    Object? status = null,
    Object? estimatedHours = null,
    Object? notes = freezed,
    Object? photos = freezed,
    Object? voiceNote = freezed,
    Object? completedAt = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$CropTaskImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      cycleId: null == cycleId
          ? _value.cycleId
          : cycleId // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      priority: null == priority
          ? _value.priority
          : priority // ignore: cast_nullable_to_non_nullable
              as String,
      dueDate: null == dueDate
          ? _value.dueDate
          : dueDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      estimatedHours: null == estimatedHours
          ? _value.estimatedHours
          : estimatedHours // ignore: cast_nullable_to_non_nullable
              as int,
      notes: freezed == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String?,
      photos: freezed == photos
          ? _value._photos
          : photos // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      voiceNote: freezed == voiceNote
          ? _value.voiceNote
          : voiceNote // ignore: cast_nullable_to_non_nullable
              as String?,
      completedAt: freezed == completedAt
          ? _value.completedAt
          : completedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CropTaskImpl implements _CropTask {
  const _$CropTaskImpl(
      {required this.id,
      required this.cycleId,
      required this.title,
      required this.description,
      required this.priority,
      required this.dueDate,
      required this.status,
      required this.estimatedHours,
      this.notes,
      final List<String>? photos,
      this.voiceNote,
      this.completedAt,
      required this.createdAt,
      required this.updatedAt})
      : _photos = photos;

  factory _$CropTaskImpl.fromJson(Map<String, dynamic> json) =>
      _$$CropTaskImplFromJson(json);

  @override
  final String id;
  @override
  final String cycleId;
  @override
  final String title;
  @override
  final String description;
  @override
  final String priority;
  @override
  final DateTime dueDate;
  @override
  final String status;
  @override
  final int estimatedHours;
  @override
  final String? notes;
  final List<String>? _photos;
  @override
  List<String>? get photos {
    final value = _photos;
    if (value == null) return null;
    if (_photos is EqualUnmodifiableListView) return _photos;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  @override
  final String? voiceNote;
  @override
  final DateTime? completedAt;
  @override
  final DateTime createdAt;
  @override
  final DateTime updatedAt;

  @override
  String toString() {
    return 'CropTask(id: $id, cycleId: $cycleId, title: $title, description: $description, priority: $priority, dueDate: $dueDate, status: $status, estimatedHours: $estimatedHours, notes: $notes, photos: $photos, voiceNote: $voiceNote, completedAt: $completedAt, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CropTaskImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.cycleId, cycleId) || other.cycleId == cycleId) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.priority, priority) ||
                other.priority == priority) &&
            (identical(other.dueDate, dueDate) || other.dueDate == dueDate) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.estimatedHours, estimatedHours) ||
                other.estimatedHours == estimatedHours) &&
            (identical(other.notes, notes) || other.notes == notes) &&
            const DeepCollectionEquality().equals(other._photos, _photos) &&
            (identical(other.voiceNote, voiceNote) ||
                other.voiceNote == voiceNote) &&
            (identical(other.completedAt, completedAt) ||
                other.completedAt == completedAt) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      cycleId,
      title,
      description,
      priority,
      dueDate,
      status,
      estimatedHours,
      notes,
      const DeepCollectionEquality().hash(_photos),
      voiceNote,
      completedAt,
      createdAt,
      updatedAt);

  /// Create a copy of CropTask
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CropTaskImplCopyWith<_$CropTaskImpl> get copyWith =>
      __$$CropTaskImplCopyWithImpl<_$CropTaskImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CropTaskImplToJson(
      this,
    );
  }
}

abstract class _CropTask implements CropTask {
  const factory _CropTask(
      {required final String id,
      required final String cycleId,
      required final String title,
      required final String description,
      required final String priority,
      required final DateTime dueDate,
      required final String status,
      required final int estimatedHours,
      final String? notes,
      final List<String>? photos,
      final String? voiceNote,
      final DateTime? completedAt,
      required final DateTime createdAt,
      required final DateTime updatedAt}) = _$CropTaskImpl;

  factory _CropTask.fromJson(Map<String, dynamic> json) =
      _$CropTaskImpl.fromJson;

  @override
  String get id;
  @override
  String get cycleId;
  @override
  String get title;
  @override
  String get description;
  @override
  String get priority;
  @override
  DateTime get dueDate;
  @override
  String get status;
  @override
  int get estimatedHours;
  @override
  String? get notes;
  @override
  List<String>? get photos;
  @override
  String? get voiceNote;
  @override
  DateTime? get completedAt;
  @override
  DateTime get createdAt;
  @override
  DateTime get updatedAt;

  /// Create a copy of CropTask
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CropTaskImplCopyWith<_$CropTaskImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CropObservation _$CropObservationFromJson(Map<String, dynamic> json) {
  return _CropObservation.fromJson(json);
}

/// @nodoc
mixin _$CropObservation {
  String get id => throw _privateConstructorUsedError;
  String get cycleId => throw _privateConstructorUsedError;
  String get observationType => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  DateTime get observedAt => throw _privateConstructorUsedError;
  List<String>? get photos => throw _privateConstructorUsedError;
  String? get voiceNote => throw _privateConstructorUsedError;
  String? get notes => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;

  /// Serializes this CropObservation to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CropObservation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CropObservationCopyWith<CropObservation> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CropObservationCopyWith<$Res> {
  factory $CropObservationCopyWith(
          CropObservation value, $Res Function(CropObservation) then) =
      _$CropObservationCopyWithImpl<$Res, CropObservation>;
  @useResult
  $Res call(
      {String id,
      String cycleId,
      String observationType,
      String description,
      DateTime observedAt,
      List<String>? photos,
      String? voiceNote,
      String? notes,
      DateTime createdAt});
}

/// @nodoc
class _$CropObservationCopyWithImpl<$Res, $Val extends CropObservation>
    implements $CropObservationCopyWith<$Res> {
  _$CropObservationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CropObservation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? cycleId = null,
    Object? observationType = null,
    Object? description = null,
    Object? observedAt = null,
    Object? photos = freezed,
    Object? voiceNote = freezed,
    Object? notes = freezed,
    Object? createdAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      cycleId: null == cycleId
          ? _value.cycleId
          : cycleId // ignore: cast_nullable_to_non_nullable
              as String,
      observationType: null == observationType
          ? _value.observationType
          : observationType // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      observedAt: null == observedAt
          ? _value.observedAt
          : observedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      photos: freezed == photos
          ? _value.photos
          : photos // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      voiceNote: freezed == voiceNote
          ? _value.voiceNote
          : voiceNote // ignore: cast_nullable_to_non_nullable
              as String?,
      notes: freezed == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CropObservationImplCopyWith<$Res>
    implements $CropObservationCopyWith<$Res> {
  factory _$$CropObservationImplCopyWith(_$CropObservationImpl value,
          $Res Function(_$CropObservationImpl) then) =
      __$$CropObservationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String cycleId,
      String observationType,
      String description,
      DateTime observedAt,
      List<String>? photos,
      String? voiceNote,
      String? notes,
      DateTime createdAt});
}

/// @nodoc
class __$$CropObservationImplCopyWithImpl<$Res>
    extends _$CropObservationCopyWithImpl<$Res, _$CropObservationImpl>
    implements _$$CropObservationImplCopyWith<$Res> {
  __$$CropObservationImplCopyWithImpl(
      _$CropObservationImpl _value, $Res Function(_$CropObservationImpl) _then)
      : super(_value, _then);

  /// Create a copy of CropObservation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? cycleId = null,
    Object? observationType = null,
    Object? description = null,
    Object? observedAt = null,
    Object? photos = freezed,
    Object? voiceNote = freezed,
    Object? notes = freezed,
    Object? createdAt = null,
  }) {
    return _then(_$CropObservationImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      cycleId: null == cycleId
          ? _value.cycleId
          : cycleId // ignore: cast_nullable_to_non_nullable
              as String,
      observationType: null == observationType
          ? _value.observationType
          : observationType // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      observedAt: null == observedAt
          ? _value.observedAt
          : observedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      photos: freezed == photos
          ? _value._photos
          : photos // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      voiceNote: freezed == voiceNote
          ? _value.voiceNote
          : voiceNote // ignore: cast_nullable_to_non_nullable
              as String?,
      notes: freezed == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CropObservationImpl implements _CropObservation {
  const _$CropObservationImpl(
      {required this.id,
      required this.cycleId,
      required this.observationType,
      required this.description,
      required this.observedAt,
      final List<String>? photos,
      this.voiceNote,
      this.notes,
      required this.createdAt})
      : _photos = photos;

  factory _$CropObservationImpl.fromJson(Map<String, dynamic> json) =>
      _$$CropObservationImplFromJson(json);

  @override
  final String id;
  @override
  final String cycleId;
  @override
  final String observationType;
  @override
  final String description;
  @override
  final DateTime observedAt;
  final List<String>? _photos;
  @override
  List<String>? get photos {
    final value = _photos;
    if (value == null) return null;
    if (_photos is EqualUnmodifiableListView) return _photos;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  @override
  final String? voiceNote;
  @override
  final String? notes;
  @override
  final DateTime createdAt;

  @override
  String toString() {
    return 'CropObservation(id: $id, cycleId: $cycleId, observationType: $observationType, description: $description, observedAt: $observedAt, photos: $photos, voiceNote: $voiceNote, notes: $notes, createdAt: $createdAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CropObservationImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.cycleId, cycleId) || other.cycleId == cycleId) &&
            (identical(other.observationType, observationType) ||
                other.observationType == observationType) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.observedAt, observedAt) ||
                other.observedAt == observedAt) &&
            const DeepCollectionEquality().equals(other._photos, _photos) &&
            (identical(other.voiceNote, voiceNote) ||
                other.voiceNote == voiceNote) &&
            (identical(other.notes, notes) || other.notes == notes) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      cycleId,
      observationType,
      description,
      observedAt,
      const DeepCollectionEquality().hash(_photos),
      voiceNote,
      notes,
      createdAt);

  /// Create a copy of CropObservation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CropObservationImplCopyWith<_$CropObservationImpl> get copyWith =>
      __$$CropObservationImplCopyWithImpl<_$CropObservationImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CropObservationImplToJson(
      this,
    );
  }
}

abstract class _CropObservation implements CropObservation {
  const factory _CropObservation(
      {required final String id,
      required final String cycleId,
      required final String observationType,
      required final String description,
      required final DateTime observedAt,
      final List<String>? photos,
      final String? voiceNote,
      final String? notes,
      required final DateTime createdAt}) = _$CropObservationImpl;

  factory _CropObservation.fromJson(Map<String, dynamic> json) =
      _$CropObservationImpl.fromJson;

  @override
  String get id;
  @override
  String get cycleId;
  @override
  String get observationType;
  @override
  String get description;
  @override
  DateTime get observedAt;
  @override
  List<String>? get photos;
  @override
  String? get voiceNote;
  @override
  String? get notes;
  @override
  DateTime get createdAt;

  /// Create a copy of CropObservation
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CropObservationImplCopyWith<_$CropObservationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

RiskAlert _$RiskAlertFromJson(Map<String, dynamic> json) {
  return _RiskAlert.fromJson(json);
}

/// @nodoc
mixin _$RiskAlert {
  String get id => throw _privateConstructorUsedError;
  String get cycleId => throw _privateConstructorUsedError;
  String get riskType => throw _privateConstructorUsedError;
  String get severity => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  String get mitigationStrategy => throw _privateConstructorUsedError;
  DateTime get detectedAt => throw _privateConstructorUsedError;
  DateTime? get acknowledgedAt => throw _privateConstructorUsedError;
  DateTime? get resolvedAt => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;

  /// Serializes this RiskAlert to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of RiskAlert
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $RiskAlertCopyWith<RiskAlert> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $RiskAlertCopyWith<$Res> {
  factory $RiskAlertCopyWith(RiskAlert value, $Res Function(RiskAlert) then) =
      _$RiskAlertCopyWithImpl<$Res, RiskAlert>;
  @useResult
  $Res call(
      {String id,
      String cycleId,
      String riskType,
      String severity,
      String description,
      String mitigationStrategy,
      DateTime detectedAt,
      DateTime? acknowledgedAt,
      DateTime? resolvedAt,
      DateTime createdAt});
}

/// @nodoc
class _$RiskAlertCopyWithImpl<$Res, $Val extends RiskAlert>
    implements $RiskAlertCopyWith<$Res> {
  _$RiskAlertCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of RiskAlert
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? cycleId = null,
    Object? riskType = null,
    Object? severity = null,
    Object? description = null,
    Object? mitigationStrategy = null,
    Object? detectedAt = null,
    Object? acknowledgedAt = freezed,
    Object? resolvedAt = freezed,
    Object? createdAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      cycleId: null == cycleId
          ? _value.cycleId
          : cycleId // ignore: cast_nullable_to_non_nullable
              as String,
      riskType: null == riskType
          ? _value.riskType
          : riskType // ignore: cast_nullable_to_non_nullable
              as String,
      severity: null == severity
          ? _value.severity
          : severity // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      mitigationStrategy: null == mitigationStrategy
          ? _value.mitigationStrategy
          : mitigationStrategy // ignore: cast_nullable_to_non_nullable
              as String,
      detectedAt: null == detectedAt
          ? _value.detectedAt
          : detectedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      acknowledgedAt: freezed == acknowledgedAt
          ? _value.acknowledgedAt
          : acknowledgedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      resolvedAt: freezed == resolvedAt
          ? _value.resolvedAt
          : resolvedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$RiskAlertImplCopyWith<$Res>
    implements $RiskAlertCopyWith<$Res> {
  factory _$$RiskAlertImplCopyWith(
          _$RiskAlertImpl value, $Res Function(_$RiskAlertImpl) then) =
      __$$RiskAlertImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String cycleId,
      String riskType,
      String severity,
      String description,
      String mitigationStrategy,
      DateTime detectedAt,
      DateTime? acknowledgedAt,
      DateTime? resolvedAt,
      DateTime createdAt});
}

/// @nodoc
class __$$RiskAlertImplCopyWithImpl<$Res>
    extends _$RiskAlertCopyWithImpl<$Res, _$RiskAlertImpl>
    implements _$$RiskAlertImplCopyWith<$Res> {
  __$$RiskAlertImplCopyWithImpl(
      _$RiskAlertImpl _value, $Res Function(_$RiskAlertImpl) _then)
      : super(_value, _then);

  /// Create a copy of RiskAlert
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? cycleId = null,
    Object? riskType = null,
    Object? severity = null,
    Object? description = null,
    Object? mitigationStrategy = null,
    Object? detectedAt = null,
    Object? acknowledgedAt = freezed,
    Object? resolvedAt = freezed,
    Object? createdAt = null,
  }) {
    return _then(_$RiskAlertImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      cycleId: null == cycleId
          ? _value.cycleId
          : cycleId // ignore: cast_nullable_to_non_nullable
              as String,
      riskType: null == riskType
          ? _value.riskType
          : riskType // ignore: cast_nullable_to_non_nullable
              as String,
      severity: null == severity
          ? _value.severity
          : severity // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      mitigationStrategy: null == mitigationStrategy
          ? _value.mitigationStrategy
          : mitigationStrategy // ignore: cast_nullable_to_non_nullable
              as String,
      detectedAt: null == detectedAt
          ? _value.detectedAt
          : detectedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      acknowledgedAt: freezed == acknowledgedAt
          ? _value.acknowledgedAt
          : acknowledgedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      resolvedAt: freezed == resolvedAt
          ? _value.resolvedAt
          : resolvedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$RiskAlertImpl implements _RiskAlert {
  const _$RiskAlertImpl(
      {required this.id,
      required this.cycleId,
      required this.riskType,
      required this.severity,
      required this.description,
      required this.mitigationStrategy,
      required this.detectedAt,
      this.acknowledgedAt,
      this.resolvedAt,
      required this.createdAt});

  factory _$RiskAlertImpl.fromJson(Map<String, dynamic> json) =>
      _$$RiskAlertImplFromJson(json);

  @override
  final String id;
  @override
  final String cycleId;
  @override
  final String riskType;
  @override
  final String severity;
  @override
  final String description;
  @override
  final String mitigationStrategy;
  @override
  final DateTime detectedAt;
  @override
  final DateTime? acknowledgedAt;
  @override
  final DateTime? resolvedAt;
  @override
  final DateTime createdAt;

  @override
  String toString() {
    return 'RiskAlert(id: $id, cycleId: $cycleId, riskType: $riskType, severity: $severity, description: $description, mitigationStrategy: $mitigationStrategy, detectedAt: $detectedAt, acknowledgedAt: $acknowledgedAt, resolvedAt: $resolvedAt, createdAt: $createdAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$RiskAlertImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.cycleId, cycleId) || other.cycleId == cycleId) &&
            (identical(other.riskType, riskType) ||
                other.riskType == riskType) &&
            (identical(other.severity, severity) ||
                other.severity == severity) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.mitigationStrategy, mitigationStrategy) ||
                other.mitigationStrategy == mitigationStrategy) &&
            (identical(other.detectedAt, detectedAt) ||
                other.detectedAt == detectedAt) &&
            (identical(other.acknowledgedAt, acknowledgedAt) ||
                other.acknowledgedAt == acknowledgedAt) &&
            (identical(other.resolvedAt, resolvedAt) ||
                other.resolvedAt == resolvedAt) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      cycleId,
      riskType,
      severity,
      description,
      mitigationStrategy,
      detectedAt,
      acknowledgedAt,
      resolvedAt,
      createdAt);

  /// Create a copy of RiskAlert
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$RiskAlertImplCopyWith<_$RiskAlertImpl> get copyWith =>
      __$$RiskAlertImplCopyWithImpl<_$RiskAlertImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$RiskAlertImplToJson(
      this,
    );
  }
}

abstract class _RiskAlert implements RiskAlert {
  const factory _RiskAlert(
      {required final String id,
      required final String cycleId,
      required final String riskType,
      required final String severity,
      required final String description,
      required final String mitigationStrategy,
      required final DateTime detectedAt,
      final DateTime? acknowledgedAt,
      final DateTime? resolvedAt,
      required final DateTime createdAt}) = _$RiskAlertImpl;

  factory _RiskAlert.fromJson(Map<String, dynamic> json) =
      _$RiskAlertImpl.fromJson;

  @override
  String get id;
  @override
  String get cycleId;
  @override
  String get riskType;
  @override
  String get severity;
  @override
  String get description;
  @override
  String get mitigationStrategy;
  @override
  DateTime get detectedAt;
  @override
  DateTime? get acknowledgedAt;
  @override
  DateTime? get resolvedAt;
  @override
  DateTime get createdAt;

  /// Create a copy of RiskAlert
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$RiskAlertImplCopyWith<_$RiskAlertImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CropPlan _$CropPlanFromJson(Map<String, dynamic> json) {
  return _CropPlan.fromJson(json);
}

/// @nodoc
mixin _$CropPlan {
  String get id => throw _privateConstructorUsedError;
  String get clientId => throw _privateConstructorUsedError;
  String get cropId => throw _privateConstructorUsedError;
  String get variety => throw _privateConstructorUsedError;
  DateTime get plannedStartDate => throw _privateConstructorUsedError;
  String get season => throw _privateConstructorUsedError;
  String get pincode => throw _privateConstructorUsedError;
  double get lat => throw _privateConstructorUsedError;
  double get lon => throw _privateConstructorUsedError;
  String get irrigationType => throw _privateConstructorUsedError;
  double get areaAcres => throw _privateConstructorUsedError;
  String get language => throw _privateConstructorUsedError;
  String get status => throw _privateConstructorUsedError;
  DateTime get plannedHarvestDate => throw _privateConstructorUsedError;
  List<CropTask> get tasks => throw _privateConstructorUsedError;
  List<RiskAlert> get risks => throw _privateConstructorUsedError;
  Map<String, dynamic> get recommendations =>
      throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;
  DateTime get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this CropPlan to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CropPlan
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CropPlanCopyWith<CropPlan> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CropPlanCopyWith<$Res> {
  factory $CropPlanCopyWith(CropPlan value, $Res Function(CropPlan) then) =
      _$CropPlanCopyWithImpl<$Res, CropPlan>;
  @useResult
  $Res call(
      {String id,
      String clientId,
      String cropId,
      String variety,
      DateTime plannedStartDate,
      String season,
      String pincode,
      double lat,
      double lon,
      String irrigationType,
      double areaAcres,
      String language,
      String status,
      DateTime plannedHarvestDate,
      List<CropTask> tasks,
      List<RiskAlert> risks,
      Map<String, dynamic> recommendations,
      DateTime createdAt,
      DateTime updatedAt});
}

/// @nodoc
class _$CropPlanCopyWithImpl<$Res, $Val extends CropPlan>
    implements $CropPlanCopyWith<$Res> {
  _$CropPlanCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CropPlan
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? clientId = null,
    Object? cropId = null,
    Object? variety = null,
    Object? plannedStartDate = null,
    Object? season = null,
    Object? pincode = null,
    Object? lat = null,
    Object? lon = null,
    Object? irrigationType = null,
    Object? areaAcres = null,
    Object? language = null,
    Object? status = null,
    Object? plannedHarvestDate = null,
    Object? tasks = null,
    Object? risks = null,
    Object? recommendations = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      clientId: null == clientId
          ? _value.clientId
          : clientId // ignore: cast_nullable_to_non_nullable
              as String,
      cropId: null == cropId
          ? _value.cropId
          : cropId // ignore: cast_nullable_to_non_nullable
              as String,
      variety: null == variety
          ? _value.variety
          : variety // ignore: cast_nullable_to_non_nullable
              as String,
      plannedStartDate: null == plannedStartDate
          ? _value.plannedStartDate
          : plannedStartDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      season: null == season
          ? _value.season
          : season // ignore: cast_nullable_to_non_nullable
              as String,
      pincode: null == pincode
          ? _value.pincode
          : pincode // ignore: cast_nullable_to_non_nullable
              as String,
      lat: null == lat
          ? _value.lat
          : lat // ignore: cast_nullable_to_non_nullable
              as double,
      lon: null == lon
          ? _value.lon
          : lon // ignore: cast_nullable_to_non_nullable
              as double,
      irrigationType: null == irrigationType
          ? _value.irrigationType
          : irrigationType // ignore: cast_nullable_to_non_nullable
              as String,
      areaAcres: null == areaAcres
          ? _value.areaAcres
          : areaAcres // ignore: cast_nullable_to_non_nullable
              as double,
      language: null == language
          ? _value.language
          : language // ignore: cast_nullable_to_non_nullable
              as String,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      plannedHarvestDate: null == plannedHarvestDate
          ? _value.plannedHarvestDate
          : plannedHarvestDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      tasks: null == tasks
          ? _value.tasks
          : tasks // ignore: cast_nullable_to_non_nullable
              as List<CropTask>,
      risks: null == risks
          ? _value.risks
          : risks // ignore: cast_nullable_to_non_nullable
              as List<RiskAlert>,
      recommendations: null == recommendations
          ? _value.recommendations
          : recommendations // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CropPlanImplCopyWith<$Res>
    implements $CropPlanCopyWith<$Res> {
  factory _$$CropPlanImplCopyWith(
          _$CropPlanImpl value, $Res Function(_$CropPlanImpl) then) =
      __$$CropPlanImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String clientId,
      String cropId,
      String variety,
      DateTime plannedStartDate,
      String season,
      String pincode,
      double lat,
      double lon,
      String irrigationType,
      double areaAcres,
      String language,
      String status,
      DateTime plannedHarvestDate,
      List<CropTask> tasks,
      List<RiskAlert> risks,
      Map<String, dynamic> recommendations,
      DateTime createdAt,
      DateTime updatedAt});
}

/// @nodoc
class __$$CropPlanImplCopyWithImpl<$Res>
    extends _$CropPlanCopyWithImpl<$Res, _$CropPlanImpl>
    implements _$$CropPlanImplCopyWith<$Res> {
  __$$CropPlanImplCopyWithImpl(
      _$CropPlanImpl _value, $Res Function(_$CropPlanImpl) _then)
      : super(_value, _then);

  /// Create a copy of CropPlan
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? clientId = null,
    Object? cropId = null,
    Object? variety = null,
    Object? plannedStartDate = null,
    Object? season = null,
    Object? pincode = null,
    Object? lat = null,
    Object? lon = null,
    Object? irrigationType = null,
    Object? areaAcres = null,
    Object? language = null,
    Object? status = null,
    Object? plannedHarvestDate = null,
    Object? tasks = null,
    Object? risks = null,
    Object? recommendations = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$CropPlanImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      clientId: null == clientId
          ? _value.clientId
          : clientId // ignore: cast_nullable_to_non_nullable
              as String,
      cropId: null == cropId
          ? _value.cropId
          : cropId // ignore: cast_nullable_to_non_nullable
              as String,
      variety: null == variety
          ? _value.variety
          : variety // ignore: cast_nullable_to_non_nullable
              as String,
      plannedStartDate: null == plannedStartDate
          ? _value.plannedStartDate
          : plannedStartDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      season: null == season
          ? _value.season
          : season // ignore: cast_nullable_to_non_nullable
              as String,
      pincode: null == pincode
          ? _value.pincode
          : pincode // ignore: cast_nullable_to_non_nullable
              as String,
      lat: null == lat
          ? _value.lat
          : lat // ignore: cast_nullable_to_non_nullable
              as double,
      lon: null == lon
          ? _value.lon
          : lon // ignore: cast_nullable_to_non_nullable
              as double,
      irrigationType: null == irrigationType
          ? _value.irrigationType
          : irrigationType // ignore: cast_nullable_to_non_nullable
              as String,
      areaAcres: null == areaAcres
          ? _value.areaAcres
          : areaAcres // ignore: cast_nullable_to_non_nullable
              as double,
      language: null == language
          ? _value.language
          : language // ignore: cast_nullable_to_non_nullable
              as String,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      plannedHarvestDate: null == plannedHarvestDate
          ? _value.plannedHarvestDate
          : plannedHarvestDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      tasks: null == tasks
          ? _value._tasks
          : tasks // ignore: cast_nullable_to_non_nullable
              as List<CropTask>,
      risks: null == risks
          ? _value._risks
          : risks // ignore: cast_nullable_to_non_nullable
              as List<RiskAlert>,
      recommendations: null == recommendations
          ? _value._recommendations
          : recommendations // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CropPlanImpl implements _CropPlan {
  const _$CropPlanImpl(
      {required this.id,
      required this.clientId,
      required this.cropId,
      required this.variety,
      required this.plannedStartDate,
      required this.season,
      required this.pincode,
      required this.lat,
      required this.lon,
      required this.irrigationType,
      required this.areaAcres,
      required this.language,
      required this.status,
      required this.plannedHarvestDate,
      required final List<CropTask> tasks,
      required final List<RiskAlert> risks,
      required final Map<String, dynamic> recommendations,
      required this.createdAt,
      required this.updatedAt})
      : _tasks = tasks,
        _risks = risks,
        _recommendations = recommendations;

  factory _$CropPlanImpl.fromJson(Map<String, dynamic> json) =>
      _$$CropPlanImplFromJson(json);

  @override
  final String id;
  @override
  final String clientId;
  @override
  final String cropId;
  @override
  final String variety;
  @override
  final DateTime plannedStartDate;
  @override
  final String season;
  @override
  final String pincode;
  @override
  final double lat;
  @override
  final double lon;
  @override
  final String irrigationType;
  @override
  final double areaAcres;
  @override
  final String language;
  @override
  final String status;
  @override
  final DateTime plannedHarvestDate;
  final List<CropTask> _tasks;
  @override
  List<CropTask> get tasks {
    if (_tasks is EqualUnmodifiableListView) return _tasks;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_tasks);
  }

  final List<RiskAlert> _risks;
  @override
  List<RiskAlert> get risks {
    if (_risks is EqualUnmodifiableListView) return _risks;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_risks);
  }

  final Map<String, dynamic> _recommendations;
  @override
  Map<String, dynamic> get recommendations {
    if (_recommendations is EqualUnmodifiableMapView) return _recommendations;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_recommendations);
  }

  @override
  final DateTime createdAt;
  @override
  final DateTime updatedAt;

  @override
  String toString() {
    return 'CropPlan(id: $id, clientId: $clientId, cropId: $cropId, variety: $variety, plannedStartDate: $plannedStartDate, season: $season, pincode: $pincode, lat: $lat, lon: $lon, irrigationType: $irrigationType, areaAcres: $areaAcres, language: $language, status: $status, plannedHarvestDate: $plannedHarvestDate, tasks: $tasks, risks: $risks, recommendations: $recommendations, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CropPlanImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.clientId, clientId) ||
                other.clientId == clientId) &&
            (identical(other.cropId, cropId) || other.cropId == cropId) &&
            (identical(other.variety, variety) || other.variety == variety) &&
            (identical(other.plannedStartDate, plannedStartDate) ||
                other.plannedStartDate == plannedStartDate) &&
            (identical(other.season, season) || other.season == season) &&
            (identical(other.pincode, pincode) || other.pincode == pincode) &&
            (identical(other.lat, lat) || other.lat == lat) &&
            (identical(other.lon, lon) || other.lon == lon) &&
            (identical(other.irrigationType, irrigationType) ||
                other.irrigationType == irrigationType) &&
            (identical(other.areaAcres, areaAcres) ||
                other.areaAcres == areaAcres) &&
            (identical(other.language, language) ||
                other.language == language) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.plannedHarvestDate, plannedHarvestDate) ||
                other.plannedHarvestDate == plannedHarvestDate) &&
            const DeepCollectionEquality().equals(other._tasks, _tasks) &&
            const DeepCollectionEquality().equals(other._risks, _risks) &&
            const DeepCollectionEquality()
                .equals(other._recommendations, _recommendations) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hashAll([
        runtimeType,
        id,
        clientId,
        cropId,
        variety,
        plannedStartDate,
        season,
        pincode,
        lat,
        lon,
        irrigationType,
        areaAcres,
        language,
        status,
        plannedHarvestDate,
        const DeepCollectionEquality().hash(_tasks),
        const DeepCollectionEquality().hash(_risks),
        const DeepCollectionEquality().hash(_recommendations),
        createdAt,
        updatedAt
      ]);

  /// Create a copy of CropPlan
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CropPlanImplCopyWith<_$CropPlanImpl> get copyWith =>
      __$$CropPlanImplCopyWithImpl<_$CropPlanImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CropPlanImplToJson(
      this,
    );
  }
}

abstract class _CropPlan implements CropPlan {
  const factory _CropPlan(
      {required final String id,
      required final String clientId,
      required final String cropId,
      required final String variety,
      required final DateTime plannedStartDate,
      required final String season,
      required final String pincode,
      required final double lat,
      required final double lon,
      required final String irrigationType,
      required final double areaAcres,
      required final String language,
      required final String status,
      required final DateTime plannedHarvestDate,
      required final List<CropTask> tasks,
      required final List<RiskAlert> risks,
      required final Map<String, dynamic> recommendations,
      required final DateTime createdAt,
      required final DateTime updatedAt}) = _$CropPlanImpl;

  factory _CropPlan.fromJson(Map<String, dynamic> json) =
      _$CropPlanImpl.fromJson;

  @override
  String get id;
  @override
  String get clientId;
  @override
  String get cropId;
  @override
  String get variety;
  @override
  DateTime get plannedStartDate;
  @override
  String get season;
  @override
  String get pincode;
  @override
  double get lat;
  @override
  double get lon;
  @override
  String get irrigationType;
  @override
  double get areaAcres;
  @override
  String get language;
  @override
  String get status;
  @override
  DateTime get plannedHarvestDate;
  @override
  List<CropTask> get tasks;
  @override
  List<RiskAlert> get risks;
  @override
  Map<String, dynamic> get recommendations;
  @override
  DateTime get createdAt;
  @override
  DateTime get updatedAt;

  /// Create a copy of CropPlan
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CropPlanImplCopyWith<_$CropPlanImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SmartChecklistRequest _$SmartChecklistRequestFromJson(
    Map<String, dynamic> json) {
  return _SmartChecklistRequest.fromJson(json);
}

/// @nodoc
mixin _$SmartChecklistRequest {
  String get clientId => throw _privateConstructorUsedError;
  String get cropId => throw _privateConstructorUsedError;
  String get variety => throw _privateConstructorUsedError;
  DateTime get startDate => throw _privateConstructorUsedError;
  String get season => throw _privateConstructorUsedError;
  String get pincode => throw _privateConstructorUsedError;
  double get lat => throw _privateConstructorUsedError;
  double get lon => throw _privateConstructorUsedError;
  String get irrigationType => throw _privateConstructorUsedError;
  double get areaAcres => throw _privateConstructorUsedError;
  String get language => throw _privateConstructorUsedError;
  int get farmerExperienceYears => throw _privateConstructorUsedError;
  String get farmSizeCategory => throw _privateConstructorUsedError;
  Map<String, dynamic> get weatherConditions =>
      throw _privateConstructorUsedError;
  Map<String, dynamic> get soilConditions => throw _privateConstructorUsedError;
  Map<String, dynamic> get marketConditions =>
      throw _privateConstructorUsedError;

  /// Serializes this SmartChecklistRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SmartChecklistRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SmartChecklistRequestCopyWith<SmartChecklistRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SmartChecklistRequestCopyWith<$Res> {
  factory $SmartChecklistRequestCopyWith(SmartChecklistRequest value,
          $Res Function(SmartChecklistRequest) then) =
      _$SmartChecklistRequestCopyWithImpl<$Res, SmartChecklistRequest>;
  @useResult
  $Res call(
      {String clientId,
      String cropId,
      String variety,
      DateTime startDate,
      String season,
      String pincode,
      double lat,
      double lon,
      String irrigationType,
      double areaAcres,
      String language,
      int farmerExperienceYears,
      String farmSizeCategory,
      Map<String, dynamic> weatherConditions,
      Map<String, dynamic> soilConditions,
      Map<String, dynamic> marketConditions});
}

/// @nodoc
class _$SmartChecklistRequestCopyWithImpl<$Res,
        $Val extends SmartChecklistRequest>
    implements $SmartChecklistRequestCopyWith<$Res> {
  _$SmartChecklistRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SmartChecklistRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? clientId = null,
    Object? cropId = null,
    Object? variety = null,
    Object? startDate = null,
    Object? season = null,
    Object? pincode = null,
    Object? lat = null,
    Object? lon = null,
    Object? irrigationType = null,
    Object? areaAcres = null,
    Object? language = null,
    Object? farmerExperienceYears = null,
    Object? farmSizeCategory = null,
    Object? weatherConditions = null,
    Object? soilConditions = null,
    Object? marketConditions = null,
  }) {
    return _then(_value.copyWith(
      clientId: null == clientId
          ? _value.clientId
          : clientId // ignore: cast_nullable_to_non_nullable
              as String,
      cropId: null == cropId
          ? _value.cropId
          : cropId // ignore: cast_nullable_to_non_nullable
              as String,
      variety: null == variety
          ? _value.variety
          : variety // ignore: cast_nullable_to_non_nullable
              as String,
      startDate: null == startDate
          ? _value.startDate
          : startDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      season: null == season
          ? _value.season
          : season // ignore: cast_nullable_to_non_nullable
              as String,
      pincode: null == pincode
          ? _value.pincode
          : pincode // ignore: cast_nullable_to_non_nullable
              as String,
      lat: null == lat
          ? _value.lat
          : lat // ignore: cast_nullable_to_non_nullable
              as double,
      lon: null == lon
          ? _value.lon
          : lon // ignore: cast_nullable_to_non_nullable
              as double,
      irrigationType: null == irrigationType
          ? _value.irrigationType
          : irrigationType // ignore: cast_nullable_to_non_nullable
              as String,
      areaAcres: null == areaAcres
          ? _value.areaAcres
          : areaAcres // ignore: cast_nullable_to_non_nullable
              as double,
      language: null == language
          ? _value.language
          : language // ignore: cast_nullable_to_non_nullable
              as String,
      farmerExperienceYears: null == farmerExperienceYears
          ? _value.farmerExperienceYears
          : farmerExperienceYears // ignore: cast_nullable_to_non_nullable
              as int,
      farmSizeCategory: null == farmSizeCategory
          ? _value.farmSizeCategory
          : farmSizeCategory // ignore: cast_nullable_to_non_nullable
              as String,
      weatherConditions: null == weatherConditions
          ? _value.weatherConditions
          : weatherConditions // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      soilConditions: null == soilConditions
          ? _value.soilConditions
          : soilConditions // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      marketConditions: null == marketConditions
          ? _value.marketConditions
          : marketConditions // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SmartChecklistRequestImplCopyWith<$Res>
    implements $SmartChecklistRequestCopyWith<$Res> {
  factory _$$SmartChecklistRequestImplCopyWith(
          _$SmartChecklistRequestImpl value,
          $Res Function(_$SmartChecklistRequestImpl) then) =
      __$$SmartChecklistRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String clientId,
      String cropId,
      String variety,
      DateTime startDate,
      String season,
      String pincode,
      double lat,
      double lon,
      String irrigationType,
      double areaAcres,
      String language,
      int farmerExperienceYears,
      String farmSizeCategory,
      Map<String, dynamic> weatherConditions,
      Map<String, dynamic> soilConditions,
      Map<String, dynamic> marketConditions});
}

/// @nodoc
class __$$SmartChecklistRequestImplCopyWithImpl<$Res>
    extends _$SmartChecklistRequestCopyWithImpl<$Res,
        _$SmartChecklistRequestImpl>
    implements _$$SmartChecklistRequestImplCopyWith<$Res> {
  __$$SmartChecklistRequestImplCopyWithImpl(_$SmartChecklistRequestImpl _value,
      $Res Function(_$SmartChecklistRequestImpl) _then)
      : super(_value, _then);

  /// Create a copy of SmartChecklistRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? clientId = null,
    Object? cropId = null,
    Object? variety = null,
    Object? startDate = null,
    Object? season = null,
    Object? pincode = null,
    Object? lat = null,
    Object? lon = null,
    Object? irrigationType = null,
    Object? areaAcres = null,
    Object? language = null,
    Object? farmerExperienceYears = null,
    Object? farmSizeCategory = null,
    Object? weatherConditions = null,
    Object? soilConditions = null,
    Object? marketConditions = null,
  }) {
    return _then(_$SmartChecklistRequestImpl(
      clientId: null == clientId
          ? _value.clientId
          : clientId // ignore: cast_nullable_to_non_nullable
              as String,
      cropId: null == cropId
          ? _value.cropId
          : cropId // ignore: cast_nullable_to_non_nullable
              as String,
      variety: null == variety
          ? _value.variety
          : variety // ignore: cast_nullable_to_non_nullable
              as String,
      startDate: null == startDate
          ? _value.startDate
          : startDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      season: null == season
          ? _value.season
          : season // ignore: cast_nullable_to_non_nullable
              as String,
      pincode: null == pincode
          ? _value.pincode
          : pincode // ignore: cast_nullable_to_non_nullable
              as String,
      lat: null == lat
          ? _value.lat
          : lat // ignore: cast_nullable_to_non_nullable
              as double,
      lon: null == lon
          ? _value.lon
          : lon // ignore: cast_nullable_to_non_nullable
              as double,
      irrigationType: null == irrigationType
          ? _value.irrigationType
          : irrigationType // ignore: cast_nullable_to_non_nullable
              as String,
      areaAcres: null == areaAcres
          ? _value.areaAcres
          : areaAcres // ignore: cast_nullable_to_non_nullable
              as double,
      language: null == language
          ? _value.language
          : language // ignore: cast_nullable_to_non_nullable
              as String,
      farmerExperienceYears: null == farmerExperienceYears
          ? _value.farmerExperienceYears
          : farmerExperienceYears // ignore: cast_nullable_to_non_nullable
              as int,
      farmSizeCategory: null == farmSizeCategory
          ? _value.farmSizeCategory
          : farmSizeCategory // ignore: cast_nullable_to_non_nullable
              as String,
      weatherConditions: null == weatherConditions
          ? _value._weatherConditions
          : weatherConditions // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      soilConditions: null == soilConditions
          ? _value._soilConditions
          : soilConditions // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      marketConditions: null == marketConditions
          ? _value._marketConditions
          : marketConditions // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SmartChecklistRequestImpl implements _SmartChecklistRequest {
  const _$SmartChecklistRequestImpl(
      {required this.clientId,
      required this.cropId,
      required this.variety,
      required this.startDate,
      required this.season,
      required this.pincode,
      required this.lat,
      required this.lon,
      required this.irrigationType,
      required this.areaAcres,
      required this.language,
      required this.farmerExperienceYears,
      required this.farmSizeCategory,
      required final Map<String, dynamic> weatherConditions,
      required final Map<String, dynamic> soilConditions,
      required final Map<String, dynamic> marketConditions})
      : _weatherConditions = weatherConditions,
        _soilConditions = soilConditions,
        _marketConditions = marketConditions;

  factory _$SmartChecklistRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$SmartChecklistRequestImplFromJson(json);

  @override
  final String clientId;
  @override
  final String cropId;
  @override
  final String variety;
  @override
  final DateTime startDate;
  @override
  final String season;
  @override
  final String pincode;
  @override
  final double lat;
  @override
  final double lon;
  @override
  final String irrigationType;
  @override
  final double areaAcres;
  @override
  final String language;
  @override
  final int farmerExperienceYears;
  @override
  final String farmSizeCategory;
  final Map<String, dynamic> _weatherConditions;
  @override
  Map<String, dynamic> get weatherConditions {
    if (_weatherConditions is EqualUnmodifiableMapView)
      return _weatherConditions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_weatherConditions);
  }

  final Map<String, dynamic> _soilConditions;
  @override
  Map<String, dynamic> get soilConditions {
    if (_soilConditions is EqualUnmodifiableMapView) return _soilConditions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_soilConditions);
  }

  final Map<String, dynamic> _marketConditions;
  @override
  Map<String, dynamic> get marketConditions {
    if (_marketConditions is EqualUnmodifiableMapView) return _marketConditions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_marketConditions);
  }

  @override
  String toString() {
    return 'SmartChecklistRequest(clientId: $clientId, cropId: $cropId, variety: $variety, startDate: $startDate, season: $season, pincode: $pincode, lat: $lat, lon: $lon, irrigationType: $irrigationType, areaAcres: $areaAcres, language: $language, farmerExperienceYears: $farmerExperienceYears, farmSizeCategory: $farmSizeCategory, weatherConditions: $weatherConditions, soilConditions: $soilConditions, marketConditions: $marketConditions)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SmartChecklistRequestImpl &&
            (identical(other.clientId, clientId) ||
                other.clientId == clientId) &&
            (identical(other.cropId, cropId) || other.cropId == cropId) &&
            (identical(other.variety, variety) || other.variety == variety) &&
            (identical(other.startDate, startDate) ||
                other.startDate == startDate) &&
            (identical(other.season, season) || other.season == season) &&
            (identical(other.pincode, pincode) || other.pincode == pincode) &&
            (identical(other.lat, lat) || other.lat == lat) &&
            (identical(other.lon, lon) || other.lon == lon) &&
            (identical(other.irrigationType, irrigationType) ||
                other.irrigationType == irrigationType) &&
            (identical(other.areaAcres, areaAcres) ||
                other.areaAcres == areaAcres) &&
            (identical(other.language, language) ||
                other.language == language) &&
            (identical(other.farmerExperienceYears, farmerExperienceYears) ||
                other.farmerExperienceYears == farmerExperienceYears) &&
            (identical(other.farmSizeCategory, farmSizeCategory) ||
                other.farmSizeCategory == farmSizeCategory) &&
            const DeepCollectionEquality()
                .equals(other._weatherConditions, _weatherConditions) &&
            const DeepCollectionEquality()
                .equals(other._soilConditions, _soilConditions) &&
            const DeepCollectionEquality()
                .equals(other._marketConditions, _marketConditions));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      clientId,
      cropId,
      variety,
      startDate,
      season,
      pincode,
      lat,
      lon,
      irrigationType,
      areaAcres,
      language,
      farmerExperienceYears,
      farmSizeCategory,
      const DeepCollectionEquality().hash(_weatherConditions),
      const DeepCollectionEquality().hash(_soilConditions),
      const DeepCollectionEquality().hash(_marketConditions));

  /// Create a copy of SmartChecklistRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SmartChecklistRequestImplCopyWith<_$SmartChecklistRequestImpl>
      get copyWith => __$$SmartChecklistRequestImplCopyWithImpl<
          _$SmartChecklistRequestImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SmartChecklistRequestImplToJson(
      this,
    );
  }
}

abstract class _SmartChecklistRequest implements SmartChecklistRequest {
  const factory _SmartChecklistRequest(
          {required final String clientId,
          required final String cropId,
          required final String variety,
          required final DateTime startDate,
          required final String season,
          required final String pincode,
          required final double lat,
          required final double lon,
          required final String irrigationType,
          required final double areaAcres,
          required final String language,
          required final int farmerExperienceYears,
          required final String farmSizeCategory,
          required final Map<String, dynamic> weatherConditions,
          required final Map<String, dynamic> soilConditions,
          required final Map<String, dynamic> marketConditions}) =
      _$SmartChecklistRequestImpl;

  factory _SmartChecklistRequest.fromJson(Map<String, dynamic> json) =
      _$SmartChecklistRequestImpl.fromJson;

  @override
  String get clientId;
  @override
  String get cropId;
  @override
  String get variety;
  @override
  DateTime get startDate;
  @override
  String get season;
  @override
  String get pincode;
  @override
  double get lat;
  @override
  double get lon;
  @override
  String get irrigationType;
  @override
  double get areaAcres;
  @override
  String get language;
  @override
  int get farmerExperienceYears;
  @override
  String get farmSizeCategory;
  @override
  Map<String, dynamic> get weatherConditions;
  @override
  Map<String, dynamic> get soilConditions;
  @override
  Map<String, dynamic> get marketConditions;

  /// Create a copy of SmartChecklistRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SmartChecklistRequestImplCopyWith<_$SmartChecklistRequestImpl>
      get copyWith => throw _privateConstructorUsedError;
}

SmartChecklistResponse _$SmartChecklistResponseFromJson(
    Map<String, dynamic> json) {
  return _SmartChecklistResponse.fromJson(json);
}

/// @nodoc
mixin _$SmartChecklistResponse {
  List<CropTask> get tasks => throw _privateConstructorUsedError;
  Map<String, dynamic> get recommendations =>
      throw _privateConstructorUsedError;
  String get riskLevel => throw _privateConstructorUsedError;
  List<String> get riskFactors => throw _privateConstructorUsedError;
  List<String> get mitigationStrategies => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;

  /// Serializes this SmartChecklistResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SmartChecklistResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SmartChecklistResponseCopyWith<SmartChecklistResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SmartChecklistResponseCopyWith<$Res> {
  factory $SmartChecklistResponseCopyWith(SmartChecklistResponse value,
          $Res Function(SmartChecklistResponse) then) =
      _$SmartChecklistResponseCopyWithImpl<$Res, SmartChecklistResponse>;
  @useResult
  $Res call(
      {List<CropTask> tasks,
      Map<String, dynamic> recommendations,
      String riskLevel,
      List<String> riskFactors,
      List<String> mitigationStrategies,
      DateTime createdAt});
}

/// @nodoc
class _$SmartChecklistResponseCopyWithImpl<$Res,
        $Val extends SmartChecklistResponse>
    implements $SmartChecklistResponseCopyWith<$Res> {
  _$SmartChecklistResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SmartChecklistResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? tasks = null,
    Object? recommendations = null,
    Object? riskLevel = null,
    Object? riskFactors = null,
    Object? mitigationStrategies = null,
    Object? createdAt = null,
  }) {
    return _then(_value.copyWith(
      tasks: null == tasks
          ? _value.tasks
          : tasks // ignore: cast_nullable_to_non_nullable
              as List<CropTask>,
      recommendations: null == recommendations
          ? _value.recommendations
          : recommendations // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      riskLevel: null == riskLevel
          ? _value.riskLevel
          : riskLevel // ignore: cast_nullable_to_non_nullable
              as String,
      riskFactors: null == riskFactors
          ? _value.riskFactors
          : riskFactors // ignore: cast_nullable_to_non_nullable
              as List<String>,
      mitigationStrategies: null == mitigationStrategies
          ? _value.mitigationStrategies
          : mitigationStrategies // ignore: cast_nullable_to_non_nullable
              as List<String>,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SmartChecklistResponseImplCopyWith<$Res>
    implements $SmartChecklistResponseCopyWith<$Res> {
  factory _$$SmartChecklistResponseImplCopyWith(
          _$SmartChecklistResponseImpl value,
          $Res Function(_$SmartChecklistResponseImpl) then) =
      __$$SmartChecklistResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {List<CropTask> tasks,
      Map<String, dynamic> recommendations,
      String riskLevel,
      List<String> riskFactors,
      List<String> mitigationStrategies,
      DateTime createdAt});
}

/// @nodoc
class __$$SmartChecklistResponseImplCopyWithImpl<$Res>
    extends _$SmartChecklistResponseCopyWithImpl<$Res,
        _$SmartChecklistResponseImpl>
    implements _$$SmartChecklistResponseImplCopyWith<$Res> {
  __$$SmartChecklistResponseImplCopyWithImpl(
      _$SmartChecklistResponseImpl _value,
      $Res Function(_$SmartChecklistResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of SmartChecklistResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? tasks = null,
    Object? recommendations = null,
    Object? riskLevel = null,
    Object? riskFactors = null,
    Object? mitigationStrategies = null,
    Object? createdAt = null,
  }) {
    return _then(_$SmartChecklistResponseImpl(
      tasks: null == tasks
          ? _value._tasks
          : tasks // ignore: cast_nullable_to_non_nullable
              as List<CropTask>,
      recommendations: null == recommendations
          ? _value._recommendations
          : recommendations // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      riskLevel: null == riskLevel
          ? _value.riskLevel
          : riskLevel // ignore: cast_nullable_to_non_nullable
              as String,
      riskFactors: null == riskFactors
          ? _value._riskFactors
          : riskFactors // ignore: cast_nullable_to_non_nullable
              as List<String>,
      mitigationStrategies: null == mitigationStrategies
          ? _value._mitigationStrategies
          : mitigationStrategies // ignore: cast_nullable_to_non_nullable
              as List<String>,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SmartChecklistResponseImpl implements _SmartChecklistResponse {
  const _$SmartChecklistResponseImpl(
      {required final List<CropTask> tasks,
      required final Map<String, dynamic> recommendations,
      required this.riskLevel,
      required final List<String> riskFactors,
      required final List<String> mitigationStrategies,
      required this.createdAt})
      : _tasks = tasks,
        _recommendations = recommendations,
        _riskFactors = riskFactors,
        _mitigationStrategies = mitigationStrategies;

  factory _$SmartChecklistResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$SmartChecklistResponseImplFromJson(json);

  final List<CropTask> _tasks;
  @override
  List<CropTask> get tasks {
    if (_tasks is EqualUnmodifiableListView) return _tasks;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_tasks);
  }

  final Map<String, dynamic> _recommendations;
  @override
  Map<String, dynamic> get recommendations {
    if (_recommendations is EqualUnmodifiableMapView) return _recommendations;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_recommendations);
  }

  @override
  final String riskLevel;
  final List<String> _riskFactors;
  @override
  List<String> get riskFactors {
    if (_riskFactors is EqualUnmodifiableListView) return _riskFactors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_riskFactors);
  }

  final List<String> _mitigationStrategies;
  @override
  List<String> get mitigationStrategies {
    if (_mitigationStrategies is EqualUnmodifiableListView)
      return _mitigationStrategies;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_mitigationStrategies);
  }

  @override
  final DateTime createdAt;

  @override
  String toString() {
    return 'SmartChecklistResponse(tasks: $tasks, recommendations: $recommendations, riskLevel: $riskLevel, riskFactors: $riskFactors, mitigationStrategies: $mitigationStrategies, createdAt: $createdAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SmartChecklistResponseImpl &&
            const DeepCollectionEquality().equals(other._tasks, _tasks) &&
            const DeepCollectionEquality()
                .equals(other._recommendations, _recommendations) &&
            (identical(other.riskLevel, riskLevel) ||
                other.riskLevel == riskLevel) &&
            const DeepCollectionEquality()
                .equals(other._riskFactors, _riskFactors) &&
            const DeepCollectionEquality()
                .equals(other._mitigationStrategies, _mitigationStrategies) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_tasks),
      const DeepCollectionEquality().hash(_recommendations),
      riskLevel,
      const DeepCollectionEquality().hash(_riskFactors),
      const DeepCollectionEquality().hash(_mitigationStrategies),
      createdAt);

  /// Create a copy of SmartChecklistResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SmartChecklistResponseImplCopyWith<_$SmartChecklistResponseImpl>
      get copyWith => __$$SmartChecklistResponseImplCopyWithImpl<
          _$SmartChecklistResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SmartChecklistResponseImplToJson(
      this,
    );
  }
}

abstract class _SmartChecklistResponse implements SmartChecklistResponse {
  const factory _SmartChecklistResponse(
      {required final List<CropTask> tasks,
      required final Map<String, dynamic> recommendations,
      required final String riskLevel,
      required final List<String> riskFactors,
      required final List<String> mitigationStrategies,
      required final DateTime createdAt}) = _$SmartChecklistResponseImpl;

  factory _SmartChecklistResponse.fromJson(Map<String, dynamic> json) =
      _$SmartChecklistResponseImpl.fromJson;

  @override
  List<CropTask> get tasks;
  @override
  Map<String, dynamic> get recommendations;
  @override
  String get riskLevel;
  @override
  List<String> get riskFactors;
  @override
  List<String> get mitigationStrategies;
  @override
  DateTime get createdAt;

  /// Create a copy of SmartChecklistResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SmartChecklistResponseImplCopyWith<_$SmartChecklistResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}
