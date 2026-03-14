// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'create_order_request.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$CreateOrderRequest {

 String get recipientPhone; String get startLat; String get startLng; String get deliveryLat; String get deliveryLng;
/// Create a copy of CreateOrderRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CreateOrderRequestCopyWith<CreateOrderRequest> get copyWith => _$CreateOrderRequestCopyWithImpl<CreateOrderRequest>(this as CreateOrderRequest, _$identity);

  /// Serializes this CreateOrderRequest to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CreateOrderRequest&&(identical(other.recipientPhone, recipientPhone) || other.recipientPhone == recipientPhone)&&(identical(other.startLat, startLat) || other.startLat == startLat)&&(identical(other.startLng, startLng) || other.startLng == startLng)&&(identical(other.deliveryLat, deliveryLat) || other.deliveryLat == deliveryLat)&&(identical(other.deliveryLng, deliveryLng) || other.deliveryLng == deliveryLng));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipientPhone,startLat,startLng,deliveryLat,deliveryLng);

@override
String toString() {
  return 'CreateOrderRequest(recipientPhone: $recipientPhone, startLat: $startLat, startLng: $startLng, deliveryLat: $deliveryLat, deliveryLng: $deliveryLng)';
}


}

/// @nodoc
abstract mixin class $CreateOrderRequestCopyWith<$Res>  {
  factory $CreateOrderRequestCopyWith(CreateOrderRequest value, $Res Function(CreateOrderRequest) _then) = _$CreateOrderRequestCopyWithImpl;
@useResult
$Res call({
 String recipientPhone, String startLat, String startLng, String deliveryLat, String deliveryLng
});




}
/// @nodoc
class _$CreateOrderRequestCopyWithImpl<$Res>
    implements $CreateOrderRequestCopyWith<$Res> {
  _$CreateOrderRequestCopyWithImpl(this._self, this._then);

  final CreateOrderRequest _self;
  final $Res Function(CreateOrderRequest) _then;

/// Create a copy of CreateOrderRequest
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipientPhone = null,Object? startLat = null,Object? startLng = null,Object? deliveryLat = null,Object? deliveryLng = null,}) {
  return _then(_self.copyWith(
recipientPhone: null == recipientPhone ? _self.recipientPhone : recipientPhone // ignore: cast_nullable_to_non_nullable
as String,startLat: null == startLat ? _self.startLat : startLat // ignore: cast_nullable_to_non_nullable
as String,startLng: null == startLng ? _self.startLng : startLng // ignore: cast_nullable_to_non_nullable
as String,deliveryLat: null == deliveryLat ? _self.deliveryLat : deliveryLat // ignore: cast_nullable_to_non_nullable
as String,deliveryLng: null == deliveryLng ? _self.deliveryLng : deliveryLng // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [CreateOrderRequest].
extension CreateOrderRequestPatterns on CreateOrderRequest {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CreateOrderRequest value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CreateOrderRequest() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CreateOrderRequest value)  $default,){
final _that = this;
switch (_that) {
case _CreateOrderRequest():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CreateOrderRequest value)?  $default,){
final _that = this;
switch (_that) {
case _CreateOrderRequest() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String recipientPhone,  String startLat,  String startLng,  String deliveryLat,  String deliveryLng)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CreateOrderRequest() when $default != null:
return $default(_that.recipientPhone,_that.startLat,_that.startLng,_that.deliveryLat,_that.deliveryLng);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String recipientPhone,  String startLat,  String startLng,  String deliveryLat,  String deliveryLng)  $default,) {final _that = this;
switch (_that) {
case _CreateOrderRequest():
return $default(_that.recipientPhone,_that.startLat,_that.startLng,_that.deliveryLat,_that.deliveryLng);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String recipientPhone,  String startLat,  String startLng,  String deliveryLat,  String deliveryLng)?  $default,) {final _that = this;
switch (_that) {
case _CreateOrderRequest() when $default != null:
return $default(_that.recipientPhone,_that.startLat,_that.startLng,_that.deliveryLat,_that.deliveryLng);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CreateOrderRequest implements CreateOrderRequest {
  const _CreateOrderRequest({required this.recipientPhone, required this.startLat, required this.startLng, required this.deliveryLat, required this.deliveryLng});
  factory _CreateOrderRequest.fromJson(Map<String, dynamic> json) => _$CreateOrderRequestFromJson(json);

@override final  String recipientPhone;
@override final  String startLat;
@override final  String startLng;
@override final  String deliveryLat;
@override final  String deliveryLng;

/// Create a copy of CreateOrderRequest
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CreateOrderRequestCopyWith<_CreateOrderRequest> get copyWith => __$CreateOrderRequestCopyWithImpl<_CreateOrderRequest>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CreateOrderRequestToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _CreateOrderRequest&&(identical(other.recipientPhone, recipientPhone) || other.recipientPhone == recipientPhone)&&(identical(other.startLat, startLat) || other.startLat == startLat)&&(identical(other.startLng, startLng) || other.startLng == startLng)&&(identical(other.deliveryLat, deliveryLat) || other.deliveryLat == deliveryLat)&&(identical(other.deliveryLng, deliveryLng) || other.deliveryLng == deliveryLng));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipientPhone,startLat,startLng,deliveryLat,deliveryLng);

@override
String toString() {
  return 'CreateOrderRequest(recipientPhone: $recipientPhone, startLat: $startLat, startLng: $startLng, deliveryLat: $deliveryLat, deliveryLng: $deliveryLng)';
}


}

/// @nodoc
abstract mixin class _$CreateOrderRequestCopyWith<$Res> implements $CreateOrderRequestCopyWith<$Res> {
  factory _$CreateOrderRequestCopyWith(_CreateOrderRequest value, $Res Function(_CreateOrderRequest) _then) = __$CreateOrderRequestCopyWithImpl;
@override @useResult
$Res call({
 String recipientPhone, String startLat, String startLng, String deliveryLat, String deliveryLng
});




}
/// @nodoc
class __$CreateOrderRequestCopyWithImpl<$Res>
    implements _$CreateOrderRequestCopyWith<$Res> {
  __$CreateOrderRequestCopyWithImpl(this._self, this._then);

  final _CreateOrderRequest _self;
  final $Res Function(_CreateOrderRequest) _then;

/// Create a copy of CreateOrderRequest
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipientPhone = null,Object? startLat = null,Object? startLng = null,Object? deliveryLat = null,Object? deliveryLng = null,}) {
  return _then(_CreateOrderRequest(
recipientPhone: null == recipientPhone ? _self.recipientPhone : recipientPhone // ignore: cast_nullable_to_non_nullable
as String,startLat: null == startLat ? _self.startLat : startLat // ignore: cast_nullable_to_non_nullable
as String,startLng: null == startLng ? _self.startLng : startLng // ignore: cast_nullable_to_non_nullable
as String,deliveryLat: null == deliveryLat ? _self.deliveryLat : deliveryLat // ignore: cast_nullable_to_non_nullable
as String,deliveryLng: null == deliveryLng ? _self.deliveryLng : deliveryLng // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
