// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'create_order_request.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_CreateOrderRequest _$CreateOrderRequestFromJson(Map<String, dynamic> json) =>
    _CreateOrderRequest(
      recipientPhone: json['recipientPhone'] as String,
      streamLat: json['streamLat'] as String,
      streamLng: json['streamLng'] as String,
      deliveryLat: json['deliveryLat'] as String,
      deliveryLng: json['deliveryLng'] as String,
    );

Map<String, dynamic> _$CreateOrderRequestToJson(_CreateOrderRequest instance) =>
    <String, dynamic>{
      'recipientPhone': instance.recipientPhone,
      'streamLat': instance.streamLat,
      'streamLng': instance.streamLng,
      'deliveryLat': instance.deliveryLat,
      'deliveryLng': instance.deliveryLng,
    };
