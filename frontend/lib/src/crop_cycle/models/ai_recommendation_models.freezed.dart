// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'ai_recommendation_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

AIRecommendation _$AIRecommendationFromJson(Map<String, dynamic> json) {
  return _AIRecommendation.fromJson(json);
}

/// @nodoc
mixin _$AIRecommendation {
  String get recommendationId => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  String get recommendationType => throw _privateConstructorUsedError;
  String get priority => throw _privateConstructorUsedError;
  List<String> get actionItems => throw _privateConstructorUsedError;
  String get reasoning => throw _privateConstructorUsedError;
  String get expectedImpact => throw _privateConstructorUsedError;
  int get urgencyHours => throw _privateConstructorUsedError;
  Map<String, dynamic> get dataSources => throw _privateConstructorUsedError;
  String get createdAt => throw _privateConstructorUsedError;
  String? get expiresAt => throw _privateConstructorUsedError;

  /// Serializes this AIRecommendation to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AIRecommendation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AIRecommendationCopyWith<AIRecommendation> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AIRecommendationCopyWith<$Res> {
  factory $AIRecommendationCopyWith(
          AIRecommendation value, $Res Function(AIRecommendation) then) =
      _$AIRecommendationCopyWithImpl<$Res, AIRecommendation>;
  @useResult
  $Res call(
      {String recommendationId,
      String title,
      String description,
      String recommendationType,
      String priority,
      List<String> actionItems,
      String reasoning,
      String expectedImpact,
      int urgencyHours,
      Map<String, dynamic> dataSources,
      String createdAt,
      String? expiresAt});
}

/// @nodoc
class _$AIRecommendationCopyWithImpl<$Res, $Val extends AIRecommendation>
    implements $AIRecommendationCopyWith<$Res> {
  _$AIRecommendationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AIRecommendation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? recommendationId = null,
    Object? title = null,
    Object? description = null,
    Object? recommendationType = null,
    Object? priority = null,
    Object? actionItems = null,
    Object? reasoning = null,
    Object? expectedImpact = null,
    Object? urgencyHours = null,
    Object? dataSources = null,
    Object? createdAt = null,
    Object? expiresAt = freezed,
  }) {
    return _then(_value.copyWith(
      recommendationId: null == recommendationId
          ? _value.recommendationId
          : recommendationId // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      recommendationType: null == recommendationType
          ? _value.recommendationType
          : recommendationType // ignore: cast_nullable_to_non_nullable
              as String,
      priority: null == priority
          ? _value.priority
          : priority // ignore: cast_nullable_to_non_nullable
              as String,
      actionItems: null == actionItems
          ? _value.actionItems
          : actionItems // ignore: cast_nullable_to_non_nullable
              as List<String>,
      reasoning: null == reasoning
          ? _value.reasoning
          : reasoning // ignore: cast_nullable_to_non_nullable
              as String,
      expectedImpact: null == expectedImpact
          ? _value.expectedImpact
          : expectedImpact // ignore: cast_nullable_to_non_nullable
              as String,
      urgencyHours: null == urgencyHours
          ? _value.urgencyHours
          : urgencyHours // ignore: cast_nullable_to_non_nullable
              as int,
      dataSources: null == dataSources
          ? _value.dataSources
          : dataSources // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      expiresAt: freezed == expiresAt
          ? _value.expiresAt
          : expiresAt // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AIRecommendationImplCopyWith<$Res>
    implements $AIRecommendationCopyWith<$Res> {
  factory _$$AIRecommendationImplCopyWith(_$AIRecommendationImpl value,
          $Res Function(_$AIRecommendationImpl) then) =
      __$$AIRecommendationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String recommendationId,
      String title,
      String description,
      String recommendationType,
      String priority,
      List<String> actionItems,
      String reasoning,
      String expectedImpact,
      int urgencyHours,
      Map<String, dynamic> dataSources,
      String createdAt,
      String? expiresAt});
}

/// @nodoc
class __$$AIRecommendationImplCopyWithImpl<$Res>
    extends _$AIRecommendationCopyWithImpl<$Res, _$AIRecommendationImpl>
    implements _$$AIRecommendationImplCopyWith<$Res> {
  __$$AIRecommendationImplCopyWithImpl(_$AIRecommendationImpl _value,
      $Res Function(_$AIRecommendationImpl) _then)
      : super(_value, _then);

  /// Create a copy of AIRecommendation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? recommendationId = null,
    Object? title = null,
    Object? description = null,
    Object? recommendationType = null,
    Object? priority = null,
    Object? actionItems = null,
    Object? reasoning = null,
    Object? expectedImpact = null,
    Object? urgencyHours = null,
    Object? dataSources = null,
    Object? createdAt = null,
    Object? expiresAt = freezed,
  }) {
    return _then(_$AIRecommendationImpl(
      recommendationId: null == recommendationId
          ? _value.recommendationId
          : recommendationId // ignore: cast_nullable_to_non_nullable
              as String,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      recommendationType: null == recommendationType
          ? _value.recommendationType
          : recommendationType // ignore: cast_nullable_to_non_nullable
              as String,
      priority: null == priority
          ? _value.priority
          : priority // ignore: cast_nullable_to_non_nullable
              as String,
      actionItems: null == actionItems
          ? _value._actionItems
          : actionItems // ignore: cast_nullable_to_non_nullable
              as List<String>,
      reasoning: null == reasoning
          ? _value.reasoning
          : reasoning // ignore: cast_nullable_to_non_nullable
              as String,
      expectedImpact: null == expectedImpact
          ? _value.expectedImpact
          : expectedImpact // ignore: cast_nullable_to_non_nullable
              as String,
      urgencyHours: null == urgencyHours
          ? _value.urgencyHours
          : urgencyHours // ignore: cast_nullable_to_non_nullable
              as int,
      dataSources: null == dataSources
          ? _value._dataSources
          : dataSources // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      expiresAt: freezed == expiresAt
          ? _value.expiresAt
          : expiresAt // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AIRecommendationImpl implements _AIRecommendation {
  const _$AIRecommendationImpl(
      {required this.recommendationId,
      required this.title,
      required this.description,
      required this.recommendationType,
      required this.priority,
      required final List<String> actionItems,
      required this.reasoning,
      required this.expectedImpact,
      required this.urgencyHours,
      required final Map<String, dynamic> dataSources,
      required this.createdAt,
      this.expiresAt})
      : _actionItems = actionItems,
        _dataSources = dataSources;

  factory _$AIRecommendationImpl.fromJson(Map<String, dynamic> json) =>
      _$$AIRecommendationImplFromJson(json);

  @override
  final String recommendationId;
  @override
  final String title;
  @override
  final String description;
  @override
  final String recommendationType;
  @override
  final String priority;
  final List<String> _actionItems;
  @override
  List<String> get actionItems {
    if (_actionItems is EqualUnmodifiableListView) return _actionItems;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_actionItems);
  }

  @override
  final String reasoning;
  @override
  final String expectedImpact;
  @override
  final int urgencyHours;
  final Map<String, dynamic> _dataSources;
  @override
  Map<String, dynamic> get dataSources {
    if (_dataSources is EqualUnmodifiableMapView) return _dataSources;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_dataSources);
  }

  @override
  final String createdAt;
  @override
  final String? expiresAt;

  @override
  String toString() {
    return 'AIRecommendation(recommendationId: $recommendationId, title: $title, description: $description, recommendationType: $recommendationType, priority: $priority, actionItems: $actionItems, reasoning: $reasoning, expectedImpact: $expectedImpact, urgencyHours: $urgencyHours, dataSources: $dataSources, createdAt: $createdAt, expiresAt: $expiresAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AIRecommendationImpl &&
            (identical(other.recommendationId, recommendationId) ||
                other.recommendationId == recommendationId) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.recommendationType, recommendationType) ||
                other.recommendationType == recommendationType) &&
            (identical(other.priority, priority) ||
                other.priority == priority) &&
            const DeepCollectionEquality()
                .equals(other._actionItems, _actionItems) &&
            (identical(other.reasoning, reasoning) ||
                other.reasoning == reasoning) &&
            (identical(other.expectedImpact, expectedImpact) ||
                other.expectedImpact == expectedImpact) &&
            (identical(other.urgencyHours, urgencyHours) ||
                other.urgencyHours == urgencyHours) &&
            const DeepCollectionEquality()
                .equals(other._dataSources, _dataSources) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.expiresAt, expiresAt) ||
                other.expiresAt == expiresAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      recommendationId,
      title,
      description,
      recommendationType,
      priority,
      const DeepCollectionEquality().hash(_actionItems),
      reasoning,
      expectedImpact,
      urgencyHours,
      const DeepCollectionEquality().hash(_dataSources),
      createdAt,
      expiresAt);

  /// Create a copy of AIRecommendation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AIRecommendationImplCopyWith<_$AIRecommendationImpl> get copyWith =>
      __$$AIRecommendationImplCopyWithImpl<_$AIRecommendationImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AIRecommendationImplToJson(
      this,
    );
  }
}

abstract class _AIRecommendation implements AIRecommendation {
  const factory _AIRecommendation(
      {required final String recommendationId,
      required final String title,
      required final String description,
      required final String recommendationType,
      required final String priority,
      required final List<String> actionItems,
      required final String reasoning,
      required final String expectedImpact,
      required final int urgencyHours,
      required final Map<String, dynamic> dataSources,
      required final String createdAt,
      final String? expiresAt}) = _$AIRecommendationImpl;

  factory _AIRecommendation.fromJson(Map<String, dynamic> json) =
      _$AIRecommendationImpl.fromJson;

  @override
  String get recommendationId;
  @override
  String get title;
  @override
  String get description;
  @override
  String get recommendationType;
  @override
  String get priority;
  @override
  List<String> get actionItems;
  @override
  String get reasoning;
  @override
  String get expectedImpact;
  @override
  int get urgencyHours;
  @override
  Map<String, dynamic> get dataSources;
  @override
  String get createdAt;
  @override
  String? get expiresAt;

  /// Create a copy of AIRecommendation
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AIRecommendationImplCopyWith<_$AIRecommendationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

AIRecommendationRequest _$AIRecommendationRequestFromJson(
    Map<String, dynamic> json) {
  return _AIRecommendationRequest.fromJson(json);
}

/// @nodoc
mixin _$AIRecommendationRequest {
  bool get includeWeather => throw _privateConstructorUsedError;
  bool get includeMarket => throw _privateConstructorUsedError;
  bool get includeSoil => throw _privateConstructorUsedError;

  /// Serializes this AIRecommendationRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AIRecommendationRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AIRecommendationRequestCopyWith<AIRecommendationRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AIRecommendationRequestCopyWith<$Res> {
  factory $AIRecommendationRequestCopyWith(AIRecommendationRequest value,
          $Res Function(AIRecommendationRequest) then) =
      _$AIRecommendationRequestCopyWithImpl<$Res, AIRecommendationRequest>;
  @useResult
  $Res call({bool includeWeather, bool includeMarket, bool includeSoil});
}

/// @nodoc
class _$AIRecommendationRequestCopyWithImpl<$Res,
        $Val extends AIRecommendationRequest>
    implements $AIRecommendationRequestCopyWith<$Res> {
  _$AIRecommendationRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AIRecommendationRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? includeWeather = null,
    Object? includeMarket = null,
    Object? includeSoil = null,
  }) {
    return _then(_value.copyWith(
      includeWeather: null == includeWeather
          ? _value.includeWeather
          : includeWeather // ignore: cast_nullable_to_non_nullable
              as bool,
      includeMarket: null == includeMarket
          ? _value.includeMarket
          : includeMarket // ignore: cast_nullable_to_non_nullable
              as bool,
      includeSoil: null == includeSoil
          ? _value.includeSoil
          : includeSoil // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AIRecommendationRequestImplCopyWith<$Res>
    implements $AIRecommendationRequestCopyWith<$Res> {
  factory _$$AIRecommendationRequestImplCopyWith(
          _$AIRecommendationRequestImpl value,
          $Res Function(_$AIRecommendationRequestImpl) then) =
      __$$AIRecommendationRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({bool includeWeather, bool includeMarket, bool includeSoil});
}

/// @nodoc
class __$$AIRecommendationRequestImplCopyWithImpl<$Res>
    extends _$AIRecommendationRequestCopyWithImpl<$Res,
        _$AIRecommendationRequestImpl>
    implements _$$AIRecommendationRequestImplCopyWith<$Res> {
  __$$AIRecommendationRequestImplCopyWithImpl(
      _$AIRecommendationRequestImpl _value,
      $Res Function(_$AIRecommendationRequestImpl) _then)
      : super(_value, _then);

  /// Create a copy of AIRecommendationRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? includeWeather = null,
    Object? includeMarket = null,
    Object? includeSoil = null,
  }) {
    return _then(_$AIRecommendationRequestImpl(
      includeWeather: null == includeWeather
          ? _value.includeWeather
          : includeWeather // ignore: cast_nullable_to_non_nullable
              as bool,
      includeMarket: null == includeMarket
          ? _value.includeMarket
          : includeMarket // ignore: cast_nullable_to_non_nullable
              as bool,
      includeSoil: null == includeSoil
          ? _value.includeSoil
          : includeSoil // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AIRecommendationRequestImpl implements _AIRecommendationRequest {
  const _$AIRecommendationRequestImpl(
      {this.includeWeather = true,
      this.includeMarket = true,
      this.includeSoil = true});

  factory _$AIRecommendationRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$AIRecommendationRequestImplFromJson(json);

  @override
  @JsonKey()
  final bool includeWeather;
  @override
  @JsonKey()
  final bool includeMarket;
  @override
  @JsonKey()
  final bool includeSoil;

  @override
  String toString() {
    return 'AIRecommendationRequest(includeWeather: $includeWeather, includeMarket: $includeMarket, includeSoil: $includeSoil)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AIRecommendationRequestImpl &&
            (identical(other.includeWeather, includeWeather) ||
                other.includeWeather == includeWeather) &&
            (identical(other.includeMarket, includeMarket) ||
                other.includeMarket == includeMarket) &&
            (identical(other.includeSoil, includeSoil) ||
                other.includeSoil == includeSoil));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, includeWeather, includeMarket, includeSoil);

  /// Create a copy of AIRecommendationRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AIRecommendationRequestImplCopyWith<_$AIRecommendationRequestImpl>
      get copyWith => __$$AIRecommendationRequestImplCopyWithImpl<
          _$AIRecommendationRequestImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AIRecommendationRequestImplToJson(
      this,
    );
  }
}

abstract class _AIRecommendationRequest implements AIRecommendationRequest {
  const factory _AIRecommendationRequest(
      {final bool includeWeather,
      final bool includeMarket,
      final bool includeSoil}) = _$AIRecommendationRequestImpl;

  factory _AIRecommendationRequest.fromJson(Map<String, dynamic> json) =
      _$AIRecommendationRequestImpl.fromJson;

  @override
  bool get includeWeather;
  @override
  bool get includeMarket;
  @override
  bool get includeSoil;

  /// Create a copy of AIRecommendationRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AIRecommendationRequestImplCopyWith<_$AIRecommendationRequestImpl>
      get copyWith => throw _privateConstructorUsedError;
}

AIRecommendationState _$AIRecommendationStateFromJson(
    Map<String, dynamic> json) {
  return _AIRecommendationState.fromJson(json);
}

/// @nodoc
mixin _$AIRecommendationState {
  List<AIRecommendation> get recommendations =>
      throw _privateConstructorUsedError;
  bool get isLoading => throw _privateConstructorUsedError;
  bool get isRefreshing => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;
  DateTime? get lastUpdated => throw _privateConstructorUsedError;

  /// Serializes this AIRecommendationState to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AIRecommendationState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AIRecommendationStateCopyWith<AIRecommendationState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AIRecommendationStateCopyWith<$Res> {
  factory $AIRecommendationStateCopyWith(AIRecommendationState value,
          $Res Function(AIRecommendationState) then) =
      _$AIRecommendationStateCopyWithImpl<$Res, AIRecommendationState>;
  @useResult
  $Res call(
      {List<AIRecommendation> recommendations,
      bool isLoading,
      bool isRefreshing,
      String? error,
      DateTime? lastUpdated});
}

/// @nodoc
class _$AIRecommendationStateCopyWithImpl<$Res,
        $Val extends AIRecommendationState>
    implements $AIRecommendationStateCopyWith<$Res> {
  _$AIRecommendationStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AIRecommendationState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? recommendations = null,
    Object? isLoading = null,
    Object? isRefreshing = null,
    Object? error = freezed,
    Object? lastUpdated = freezed,
  }) {
    return _then(_value.copyWith(
      recommendations: null == recommendations
          ? _value.recommendations
          : recommendations // ignore: cast_nullable_to_non_nullable
              as List<AIRecommendation>,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      isRefreshing: null == isRefreshing
          ? _value.isRefreshing
          : isRefreshing // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      lastUpdated: freezed == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AIRecommendationStateImplCopyWith<$Res>
    implements $AIRecommendationStateCopyWith<$Res> {
  factory _$$AIRecommendationStateImplCopyWith(
          _$AIRecommendationStateImpl value,
          $Res Function(_$AIRecommendationStateImpl) then) =
      __$$AIRecommendationStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {List<AIRecommendation> recommendations,
      bool isLoading,
      bool isRefreshing,
      String? error,
      DateTime? lastUpdated});
}

/// @nodoc
class __$$AIRecommendationStateImplCopyWithImpl<$Res>
    extends _$AIRecommendationStateCopyWithImpl<$Res,
        _$AIRecommendationStateImpl>
    implements _$$AIRecommendationStateImplCopyWith<$Res> {
  __$$AIRecommendationStateImplCopyWithImpl(_$AIRecommendationStateImpl _value,
      $Res Function(_$AIRecommendationStateImpl) _then)
      : super(_value, _then);

  /// Create a copy of AIRecommendationState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? recommendations = null,
    Object? isLoading = null,
    Object? isRefreshing = null,
    Object? error = freezed,
    Object? lastUpdated = freezed,
  }) {
    return _then(_$AIRecommendationStateImpl(
      recommendations: null == recommendations
          ? _value._recommendations
          : recommendations // ignore: cast_nullable_to_non_nullable
              as List<AIRecommendation>,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      isRefreshing: null == isRefreshing
          ? _value.isRefreshing
          : isRefreshing // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      lastUpdated: freezed == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AIRecommendationStateImpl implements _AIRecommendationState {
  const _$AIRecommendationStateImpl(
      {final List<AIRecommendation> recommendations = const [],
      this.isLoading = false,
      this.isRefreshing = false,
      this.error,
      this.lastUpdated})
      : _recommendations = recommendations;

  factory _$AIRecommendationStateImpl.fromJson(Map<String, dynamic> json) =>
      _$$AIRecommendationStateImplFromJson(json);

  final List<AIRecommendation> _recommendations;
  @override
  @JsonKey()
  List<AIRecommendation> get recommendations {
    if (_recommendations is EqualUnmodifiableListView) return _recommendations;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_recommendations);
  }

  @override
  @JsonKey()
  final bool isLoading;
  @override
  @JsonKey()
  final bool isRefreshing;
  @override
  final String? error;
  @override
  final DateTime? lastUpdated;

  @override
  String toString() {
    return 'AIRecommendationState(recommendations: $recommendations, isLoading: $isLoading, isRefreshing: $isRefreshing, error: $error, lastUpdated: $lastUpdated)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AIRecommendationStateImpl &&
            const DeepCollectionEquality()
                .equals(other._recommendations, _recommendations) &&
            (identical(other.isLoading, isLoading) ||
                other.isLoading == isLoading) &&
            (identical(other.isRefreshing, isRefreshing) ||
                other.isRefreshing == isRefreshing) &&
            (identical(other.error, error) || other.error == error) &&
            (identical(other.lastUpdated, lastUpdated) ||
                other.lastUpdated == lastUpdated));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_recommendations),
      isLoading,
      isRefreshing,
      error,
      lastUpdated);

  /// Create a copy of AIRecommendationState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AIRecommendationStateImplCopyWith<_$AIRecommendationStateImpl>
      get copyWith => __$$AIRecommendationStateImplCopyWithImpl<
          _$AIRecommendationStateImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AIRecommendationStateImplToJson(
      this,
    );
  }
}

abstract class _AIRecommendationState implements AIRecommendationState {
  const factory _AIRecommendationState(
      {final List<AIRecommendation> recommendations,
      final bool isLoading,
      final bool isRefreshing,
      final String? error,
      final DateTime? lastUpdated}) = _$AIRecommendationStateImpl;

  factory _AIRecommendationState.fromJson(Map<String, dynamic> json) =
      _$AIRecommendationStateImpl.fromJson;

  @override
  List<AIRecommendation> get recommendations;
  @override
  bool get isLoading;
  @override
  bool get isRefreshing;
  @override
  String? get error;
  @override
  DateTime? get lastUpdated;

  /// Create a copy of AIRecommendationState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AIRecommendationStateImplCopyWith<_$AIRecommendationStateImpl>
      get copyWith => throw _privateConstructorUsedError;
}
