// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'response_data.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ResponseData<T> {

 String? get message; T? get data;
/// Create a copy of ResponseData
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ResponseDataCopyWith<T, ResponseData<T>> get copyWith => _$ResponseDataCopyWithImpl<T, ResponseData<T>>(this as ResponseData<T>, _$identity);

  /// Serializes this ResponseData to a JSON map.
  Map<String, dynamic> toJson(Object? Function(T) toJsonT);


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ResponseData<T>&&(identical(other.message, message) || other.message == message)&&const DeepCollectionEquality().equals(other.data, data));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,message,const DeepCollectionEquality().hash(data));

@override
String toString() {
  return 'ResponseData<$T>(message: $message, data: $data)';
}


}

/// @nodoc
abstract mixin class $ResponseDataCopyWith<T,$Res>  {
  factory $ResponseDataCopyWith(ResponseData<T> value, $Res Function(ResponseData<T>) _then) = _$ResponseDataCopyWithImpl;
@useResult
$Res call({
 String? message, T? data
});




}
/// @nodoc
class _$ResponseDataCopyWithImpl<T,$Res>
    implements $ResponseDataCopyWith<T, $Res> {
  _$ResponseDataCopyWithImpl(this._self, this._then);

  final ResponseData<T> _self;
  final $Res Function(ResponseData<T>) _then;

/// Create a copy of ResponseData
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? message = freezed,Object? data = freezed,}) {
  return _then(_self.copyWith(
message: freezed == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String?,data: freezed == data ? _self.data : data // ignore: cast_nullable_to_non_nullable
as T?,
  ));
}

}


/// Adds pattern-matching-related methods to [ResponseData].
extension ResponseDataPatterns<T> on ResponseData<T> {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ResponseData<T> value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ResponseData() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ResponseData<T> value)  $default,){
final _that = this;
switch (_that) {
case _ResponseData():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ResponseData<T> value)?  $default,){
final _that = this;
switch (_that) {
case _ResponseData() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? message,  T? data)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ResponseData() when $default != null:
return $default(_that.message,_that.data);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? message,  T? data)  $default,) {final _that = this;
switch (_that) {
case _ResponseData():
return $default(_that.message,_that.data);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? message,  T? data)?  $default,) {final _that = this;
switch (_that) {
case _ResponseData() when $default != null:
return $default(_that.message,_that.data);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable(genericArgumentFactories: true)

class _ResponseData<T> implements ResponseData<T> {
  const _ResponseData({this.message, this.data});
  factory _ResponseData.fromJson(Map<String, dynamic> json,T Function(Object?) fromJsonT) => _$ResponseDataFromJson(json,fromJsonT);

@override final  String? message;
@override final  T? data;

/// Create a copy of ResponseData
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ResponseDataCopyWith<T, _ResponseData<T>> get copyWith => __$ResponseDataCopyWithImpl<T, _ResponseData<T>>(this, _$identity);

@override
Map<String, dynamic> toJson(Object? Function(T) toJsonT) {
  return _$ResponseDataToJson<T>(this, toJsonT);
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ResponseData<T>&&(identical(other.message, message) || other.message == message)&&const DeepCollectionEquality().equals(other.data, data));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,message,const DeepCollectionEquality().hash(data));

@override
String toString() {
  return 'ResponseData<$T>(message: $message, data: $data)';
}


}

/// @nodoc
abstract mixin class _$ResponseDataCopyWith<T,$Res> implements $ResponseDataCopyWith<T, $Res> {
  factory _$ResponseDataCopyWith(_ResponseData<T> value, $Res Function(_ResponseData<T>) _then) = __$ResponseDataCopyWithImpl;
@override @useResult
$Res call({
 String? message, T? data
});




}
/// @nodoc
class __$ResponseDataCopyWithImpl<T,$Res>
    implements _$ResponseDataCopyWith<T, $Res> {
  __$ResponseDataCopyWithImpl(this._self, this._then);

  final _ResponseData<T> _self;
  final $Res Function(_ResponseData<T>) _then;

/// Create a copy of ResponseData
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? message = freezed,Object? data = freezed,}) {
  return _then(_ResponseData<T>(
message: freezed == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String?,data: freezed == data ? _self.data : data // ignore: cast_nullable_to_non_nullable
as T?,
  ));
}


}

// dart format on
