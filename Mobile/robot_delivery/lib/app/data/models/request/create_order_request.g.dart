// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'create_order_request.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_CreateOrderRequest _$CreateOrderRequestFromJson(Map<String, dynamic> json) =>
    _CreateOrderRequest(
      recipientPhone: json['recipientPhone'] as String,
      startLat: (json['startLat'] as num).toDouble(),
      startLng: (json['startLng'] as num).toDouble(),
      deliveryLat: (json['deliveryLat'] as num).toDouble(),
      deliveryLng: (json['deliveryLng'] as num).toDouble(),
      senderAddress: json['senderAddress'] as String?,
      deliveryAddress: json['deliveryAddress'] as String?,
    );

Map<String, dynamic> _$CreateOrderRequestToJson(_CreateOrderRequest instance) =>
    <String, dynamic>{
      'recipientPhone': instance.recipientPhone,
      'startLat': instance.startLat,
      'startLng': instance.startLng,
      'deliveryLat': instance.deliveryLat,
      'deliveryLng': instance.deliveryLng,
      'senderAddress': instance.senderAddress,
      'deliveryAddress': instance.deliveryAddress,
    };
