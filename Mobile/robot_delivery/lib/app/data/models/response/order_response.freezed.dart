// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'order_response.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$OrderResponse {

 int get id; String get orderId; Customer get customer; Customer get recipient; String get recipientPhone; double get streamLat; double get streamLng; double get deliveryLat; double get deliveryLng; String get pinCode; String get senderName; int get robotId; String get robotName; String get status; DateTime get createdAt;
/// Create a copy of OrderResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OrderResponseCopyWith<OrderResponse> get copyWith => _$OrderResponseCopyWithImpl<OrderResponse>(this as OrderResponse, _$identity);

  /// Serializes this OrderResponse to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is OrderResponse&&(identical(other.id, id) || other.id == id)&&(identical(other.orderId, orderId) || other.orderId == orderId)&&(identical(other.customer, customer) || other.customer == customer)&&(identical(other.recipient, recipient) || other.recipient == recipient)&&(identical(other.recipientPhone, recipientPhone) || other.recipientPhone == recipientPhone)&&(identical(other.streamLat, streamLat) || other.streamLat == streamLat)&&(identical(other.streamLng, streamLng) || other.streamLng == streamLng)&&(identical(other.deliveryLat, deliveryLat) || other.deliveryLat == deliveryLat)&&(identical(other.deliveryLng, deliveryLng) || other.deliveryLng == deliveryLng)&&(identical(other.pinCode, pinCode) || other.pinCode == pinCode)&&(identical(other.senderName, senderName) || other.senderName == senderName)&&(identical(other.robotId, robotId) || other.robotId == robotId)&&(identical(other.robotName, robotName) || other.robotName == robotName)&&(identical(other.status, status) || other.status == status)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,orderId,customer,recipient,recipientPhone,streamLat,streamLng,deliveryLat,deliveryLng,pinCode,senderName,robotId,robotName,status,createdAt);

@override
String toString() {
  return 'OrderResponse(id: $id, orderId: $orderId, customer: $customer, recipient: $recipient, recipientPhone: $recipientPhone, streamLat: $streamLat, streamLng: $streamLng, deliveryLat: $deliveryLat, deliveryLng: $deliveryLng, pinCode: $pinCode, senderName: $senderName, robotId: $robotId, robotName: $robotName, status: $status, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class $OrderResponseCopyWith<$Res>  {
  factory $OrderResponseCopyWith(OrderResponse value, $Res Function(OrderResponse) _then) = _$OrderResponseCopyWithImpl;
@useResult
$Res call({
 int id, String orderId, Customer customer, Customer recipient, String recipientPhone, double streamLat, double streamLng, double deliveryLat, double deliveryLng, String pinCode, String senderName, int robotId, String robotName, String status, DateTime createdAt
});


$CustomerCopyWith<$Res> get customer;$CustomerCopyWith<$Res> get recipient;

}
/// @nodoc
class _$OrderResponseCopyWithImpl<$Res>
    implements $OrderResponseCopyWith<$Res> {
  _$OrderResponseCopyWithImpl(this._self, this._then);

  final OrderResponse _self;
  final $Res Function(OrderResponse) _then;

/// Create a copy of OrderResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? orderId = null,Object? customer = null,Object? recipient = null,Object? recipientPhone = null,Object? streamLat = null,Object? streamLng = null,Object? deliveryLat = null,Object? deliveryLng = null,Object? pinCode = null,Object? senderName = null,Object? robotId = null,Object? robotName = null,Object? status = null,Object? createdAt = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,orderId: null == orderId ? _self.orderId : orderId // ignore: cast_nullable_to_non_nullable
as String,customer: null == customer ? _self.customer : customer // ignore: cast_nullable_to_non_nullable
as Customer,recipient: null == recipient ? _self.recipient : recipient // ignore: cast_nullable_to_non_nullable
as Customer,recipientPhone: null == recipientPhone ? _self.recipientPhone : recipientPhone // ignore: cast_nullable_to_non_nullable
as String,streamLat: null == streamLat ? _self.streamLat : streamLat // ignore: cast_nullable_to_non_nullable
as double,streamLng: null == streamLng ? _self.streamLng : streamLng // ignore: cast_nullable_to_non_nullable
as double,deliveryLat: null == deliveryLat ? _self.deliveryLat : deliveryLat // ignore: cast_nullable_to_non_nullable
as double,deliveryLng: null == deliveryLng ? _self.deliveryLng : deliveryLng // ignore: cast_nullable_to_non_nullable
as double,pinCode: null == pinCode ? _self.pinCode : pinCode // ignore: cast_nullable_to_non_nullable
as String,senderName: null == senderName ? _self.senderName : senderName // ignore: cast_nullable_to_non_nullable
as String,robotId: null == robotId ? _self.robotId : robotId // ignore: cast_nullable_to_non_nullable
as int,robotName: null == robotName ? _self.robotName : robotName // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}
/// Create a copy of OrderResponse
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CustomerCopyWith<$Res> get customer {
  
  return $CustomerCopyWith<$Res>(_self.customer, (value) {
    return _then(_self.copyWith(customer: value));
  });
}/// Create a copy of OrderResponse
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CustomerCopyWith<$Res> get recipient {
  
  return $CustomerCopyWith<$Res>(_self.recipient, (value) {
    return _then(_self.copyWith(recipient: value));
  });
}
}


/// Adds pattern-matching-related methods to [OrderResponse].
extension OrderResponsePatterns on OrderResponse {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OrderResponse value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OrderResponse() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OrderResponse value)  $default,){
final _that = this;
switch (_that) {
case _OrderResponse():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OrderResponse value)?  $default,){
final _that = this;
switch (_that) {
case _OrderResponse() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String orderId,  Customer customer,  Customer recipient,  String recipientPhone,  double streamLat,  double streamLng,  double deliveryLat,  double deliveryLng,  String pinCode,  String senderName,  int robotId,  String robotName,  String status,  DateTime createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OrderResponse() when $default != null:
return $default(_that.id,_that.orderId,_that.customer,_that.recipient,_that.recipientPhone,_that.streamLat,_that.streamLng,_that.deliveryLat,_that.deliveryLng,_that.pinCode,_that.senderName,_that.robotId,_that.robotName,_that.status,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String orderId,  Customer customer,  Customer recipient,  String recipientPhone,  double streamLat,  double streamLng,  double deliveryLat,  double deliveryLng,  String pinCode,  String senderName,  int robotId,  String robotName,  String status,  DateTime createdAt)  $default,) {final _that = this;
switch (_that) {
case _OrderResponse():
return $default(_that.id,_that.orderId,_that.customer,_that.recipient,_that.recipientPhone,_that.streamLat,_that.streamLng,_that.deliveryLat,_that.deliveryLng,_that.pinCode,_that.senderName,_that.robotId,_that.robotName,_that.status,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String orderId,  Customer customer,  Customer recipient,  String recipientPhone,  double streamLat,  double streamLng,  double deliveryLat,  double deliveryLng,  String pinCode,  String senderName,  int robotId,  String robotName,  String status,  DateTime createdAt)?  $default,) {final _that = this;
switch (_that) {
case _OrderResponse() when $default != null:
return $default(_that.id,_that.orderId,_that.customer,_that.recipient,_that.recipientPhone,_that.streamLat,_that.streamLng,_that.deliveryLat,_that.deliveryLng,_that.pinCode,_that.senderName,_that.robotId,_that.robotName,_that.status,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _OrderResponse implements OrderResponse {
  const _OrderResponse({required this.id, required this.orderId, required this.customer, required this.recipient, required this.recipientPhone, required this.streamLat, required this.streamLng, required this.deliveryLat, required this.deliveryLng, required this.pinCode, required this.senderName, required this.robotId, required this.robotName, required this.status, required this.createdAt});
  factory _OrderResponse.fromJson(Map<String, dynamic> json) => _$OrderResponseFromJson(json);

@override final  int id;
@override final  String orderId;
@override final  Customer customer;
@override final  Customer recipient;
@override final  String recipientPhone;
@override final  double streamLat;
@override final  double streamLng;
@override final  double deliveryLat;
@override final  double deliveryLng;
@override final  String pinCode;
@override final  String senderName;
@override final  int robotId;
@override final  String robotName;
@override final  String status;
@override final  DateTime createdAt;

/// Create a copy of OrderResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OrderResponseCopyWith<_OrderResponse> get copyWith => __$OrderResponseCopyWithImpl<_OrderResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OrderResponseToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _OrderResponse&&(identical(other.id, id) || other.id == id)&&(identical(other.orderId, orderId) || other.orderId == orderId)&&(identical(other.customer, customer) || other.customer == customer)&&(identical(other.recipient, recipient) || other.recipient == recipient)&&(identical(other.recipientPhone, recipientPhone) || other.recipientPhone == recipientPhone)&&(identical(other.streamLat, streamLat) || other.streamLat == streamLat)&&(identical(other.streamLng, streamLng) || other.streamLng == streamLng)&&(identical(other.deliveryLat, deliveryLat) || other.deliveryLat == deliveryLat)&&(identical(other.deliveryLng, deliveryLng) || other.deliveryLng == deliveryLng)&&(identical(other.pinCode, pinCode) || other.pinCode == pinCode)&&(identical(other.senderName, senderName) || other.senderName == senderName)&&(identical(other.robotId, robotId) || other.robotId == robotId)&&(identical(other.robotName, robotName) || other.robotName == robotName)&&(identical(other.status, status) || other.status == status)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,orderId,customer,recipient,recipientPhone,streamLat,streamLng,deliveryLat,deliveryLng,pinCode,senderName,robotId,robotName,status,createdAt);

@override
String toString() {
  return 'OrderResponse(id: $id, orderId: $orderId, customer: $customer, recipient: $recipient, recipientPhone: $recipientPhone, streamLat: $streamLat, streamLng: $streamLng, deliveryLat: $deliveryLat, deliveryLng: $deliveryLng, pinCode: $pinCode, senderName: $senderName, robotId: $robotId, robotName: $robotName, status: $status, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$OrderResponseCopyWith<$Res> implements $OrderResponseCopyWith<$Res> {
  factory _$OrderResponseCopyWith(_OrderResponse value, $Res Function(_OrderResponse) _then) = __$OrderResponseCopyWithImpl;
@override @useResult
$Res call({
 int id, String orderId, Customer customer, Customer recipient, String recipientPhone, double streamLat, double streamLng, double deliveryLat, double deliveryLng, String pinCode, String senderName, int robotId, String robotName, String status, DateTime createdAt
});


@override $CustomerCopyWith<$Res> get customer;@override $CustomerCopyWith<$Res> get recipient;

}
/// @nodoc
class __$OrderResponseCopyWithImpl<$Res>
    implements _$OrderResponseCopyWith<$Res> {
  __$OrderResponseCopyWithImpl(this._self, this._then);

  final _OrderResponse _self;
  final $Res Function(_OrderResponse) _then;

/// Create a copy of OrderResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? orderId = null,Object? customer = null,Object? recipient = null,Object? recipientPhone = null,Object? streamLat = null,Object? streamLng = null,Object? deliveryLat = null,Object? deliveryLng = null,Object? pinCode = null,Object? senderName = null,Object? robotId = null,Object? robotName = null,Object? status = null,Object? createdAt = null,}) {
  return _then(_OrderResponse(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,orderId: null == orderId ? _self.orderId : orderId // ignore: cast_nullable_to_non_nullable
as String,customer: null == customer ? _self.customer : customer // ignore: cast_nullable_to_non_nullable
as Customer,recipient: null == recipient ? _self.recipient : recipient // ignore: cast_nullable_to_non_nullable
as Customer,recipientPhone: null == recipientPhone ? _self.recipientPhone : recipientPhone // ignore: cast_nullable_to_non_nullable
as String,streamLat: null == streamLat ? _self.streamLat : streamLat // ignore: cast_nullable_to_non_nullable
as double,streamLng: null == streamLng ? _self.streamLng : streamLng // ignore: cast_nullable_to_non_nullable
as double,deliveryLat: null == deliveryLat ? _self.deliveryLat : deliveryLat // ignore: cast_nullable_to_non_nullable
as double,deliveryLng: null == deliveryLng ? _self.deliveryLng : deliveryLng // ignore: cast_nullable_to_non_nullable
as double,pinCode: null == pinCode ? _self.pinCode : pinCode // ignore: cast_nullable_to_non_nullable
as String,senderName: null == senderName ? _self.senderName : senderName // ignore: cast_nullable_to_non_nullable
as String,robotId: null == robotId ? _self.robotId : robotId // ignore: cast_nullable_to_non_nullable
as int,robotName: null == robotName ? _self.robotName : robotName // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

/// Create a copy of OrderResponse
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CustomerCopyWith<$Res> get customer {
  
  return $CustomerCopyWith<$Res>(_self.customer, (value) {
    return _then(_self.copyWith(customer: value));
  });
}/// Create a copy of OrderResponse
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CustomerCopyWith<$Res> get recipient {
  
  return $CustomerCopyWith<$Res>(_self.recipient, (value) {
    return _then(_self.copyWith(recipient: value));
  });
}
}


/// @nodoc
mixin _$Customer {

 int get id; String get username; String get fullName; String get phoneNumber;
/// Create a copy of Customer
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CustomerCopyWith<Customer> get copyWith => _$CustomerCopyWithImpl<Customer>(this as Customer, _$identity);

  /// Serializes this Customer to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Customer&&(identical(other.id, id) || other.id == id)&&(identical(other.username, username) || other.username == username)&&(identical(other.fullName, fullName) || other.fullName == fullName)&&(identical(other.phoneNumber, phoneNumber) || other.phoneNumber == phoneNumber));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,username,fullName,phoneNumber);

@override
String toString() {
  return 'Customer(id: $id, username: $username, fullName: $fullName, phoneNumber: $phoneNumber)';
}


}

/// @nodoc
abstract mixin class $CustomerCopyWith<$Res>  {
  factory $CustomerCopyWith(Customer value, $Res Function(Customer) _then) = _$CustomerCopyWithImpl;
@useResult
$Res call({
 int id, String username, String fullName, String phoneNumber
});




}
/// @nodoc
class _$CustomerCopyWithImpl<$Res>
    implements $CustomerCopyWith<$Res> {
  _$CustomerCopyWithImpl(this._self, this._then);

  final Customer _self;
  final $Res Function(Customer) _then;

/// Create a copy of Customer
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? username = null,Object? fullName = null,Object? phoneNumber = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,username: null == username ? _self.username : username // ignore: cast_nullable_to_non_nullable
as String,fullName: null == fullName ? _self.fullName : fullName // ignore: cast_nullable_to_non_nullable
as String,phoneNumber: null == phoneNumber ? _self.phoneNumber : phoneNumber // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [Customer].
extension CustomerPatterns on Customer {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Customer value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Customer() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Customer value)  $default,){
final _that = this;
switch (_that) {
case _Customer():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Customer value)?  $default,){
final _that = this;
switch (_that) {
case _Customer() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String username,  String fullName,  String phoneNumber)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Customer() when $default != null:
return $default(_that.id,_that.username,_that.fullName,_that.phoneNumber);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String username,  String fullName,  String phoneNumber)  $default,) {final _that = this;
switch (_that) {
case _Customer():
return $default(_that.id,_that.username,_that.fullName,_that.phoneNumber);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String username,  String fullName,  String phoneNumber)?  $default,) {final _that = this;
switch (_that) {
case _Customer() when $default != null:
return $default(_that.id,_that.username,_that.fullName,_that.phoneNumber);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Customer implements Customer {
  const _Customer({required this.id, required this.username, required this.fullName, required this.phoneNumber});
  factory _Customer.fromJson(Map<String, dynamic> json) => _$CustomerFromJson(json);

@override final  int id;
@override final  String username;
@override final  String fullName;
@override final  String phoneNumber;

/// Create a copy of Customer
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CustomerCopyWith<_Customer> get copyWith => __$CustomerCopyWithImpl<_Customer>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CustomerToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Customer&&(identical(other.id, id) || other.id == id)&&(identical(other.username, username) || other.username == username)&&(identical(other.fullName, fullName) || other.fullName == fullName)&&(identical(other.phoneNumber, phoneNumber) || other.phoneNumber == phoneNumber));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,username,fullName,phoneNumber);

@override
String toString() {
  return 'Customer(id: $id, username: $username, fullName: $fullName, phoneNumber: $phoneNumber)';
}


}

/// @nodoc
abstract mixin class _$CustomerCopyWith<$Res> implements $CustomerCopyWith<$Res> {
  factory _$CustomerCopyWith(_Customer value, $Res Function(_Customer) _then) = __$CustomerCopyWithImpl;
@override @useResult
$Res call({
 int id, String username, String fullName, String phoneNumber
});




}
/// @nodoc
class __$CustomerCopyWithImpl<$Res>
    implements _$CustomerCopyWith<$Res> {
  __$CustomerCopyWithImpl(this._self, this._then);

  final _Customer _self;
  final $Res Function(_Customer) _then;

/// Create a copy of Customer
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? username = null,Object? fullName = null,Object? phoneNumber = null,}) {
  return _then(_Customer(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,username: null == username ? _self.username : username // ignore: cast_nullable_to_non_nullable
as String,fullName: null == fullName ? _self.fullName : fullName // ignore: cast_nullable_to_non_nullable
as String,phoneNumber: null == phoneNumber ? _self.phoneNumber : phoneNumber // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
