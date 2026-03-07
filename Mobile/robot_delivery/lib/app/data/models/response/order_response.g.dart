// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'order_response.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_OrderResponse _$OrderResponseFromJson(Map<String, dynamic> json) =>
    _OrderResponse(
      id: (json['id'] as num).toInt(),
      orderId: json['orderId'] as String,
      customer: Customer.fromJson(json['customer'] as Map<String, dynamic>),
      recipient: Customer.fromJson(json['recipient'] as Map<String, dynamic>),
      recipientPhone: json['recipientPhone'] as String,
      streamLat: (json['streamLat'] as num).toDouble(),
      streamLng: (json['streamLng'] as num).toDouble(),
      deliveryLat: (json['deliveryLat'] as num).toDouble(),
      deliveryLng: (json['deliveryLng'] as num).toDouble(),
      pinCode: json['pinCode'] as String,
      senderName: json['senderName'] as String,
      robotId: (json['robotId'] as num).toInt(),
      robotName: json['robotName'] as String,
      status: json['status'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$OrderResponseToJson(_OrderResponse instance) =>
    <String, dynamic>{
      'id': instance.id,
      'orderId': instance.orderId,
      'customer': instance.customer,
      'recipient': instance.recipient,
      'recipientPhone': instance.recipientPhone,
      'streamLat': instance.streamLat,
      'streamLng': instance.streamLng,
      'deliveryLat': instance.deliveryLat,
      'deliveryLng': instance.deliveryLng,
      'pinCode': instance.pinCode,
      'senderName': instance.senderName,
      'robotId': instance.robotId,
      'robotName': instance.robotName,
      'status': instance.status,
      'createdAt': instance.createdAt.toIso8601String(),
    };

_Customer _$CustomerFromJson(Map<String, dynamic> json) => _Customer(
  id: (json['id'] as num).toInt(),
  username: json['username'] as String,
  fullName: json['fullName'] as String,
  phoneNumber: json['phoneNumber'] as String,
);

Map<String, dynamic> _$CustomerToJson(_Customer instance) => <String, dynamic>{
  'id': instance.id,
  'username': instance.username,
  'fullName': instance.fullName,
  'phoneNumber': instance.phoneNumber,
};
