// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'create_order_request.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_CreateOrderRequest _$CreateOrderRequestFromJson(Map<String, dynamic> json) =>
    _CreateOrderRequest(
      recipientPhone: json['recipientPhone'] as String,
      startLat: json['startLat'] as String,
      startLng: json['startLng'] as String,
      deliveryLat: json['deliveryLat'] as String,
      deliveryLng: json['deliveryLng'] as String,
    );

Map<String, dynamic> _$CreateOrderRequestToJson(_CreateOrderRequest instance) =>
    <String, dynamic>{
      'recipientPhone': instance.recipientPhone,
      'startLat': instance.startLat,
      'startLng': instance.startLng,
      'deliveryLat': instance.deliveryLat,
      'deliveryLng': instance.deliveryLng,
    };
