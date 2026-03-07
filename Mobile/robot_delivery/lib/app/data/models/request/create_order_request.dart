import 'package:freezed_annotation/freezed_annotation.dart';
part 'create_order_request.freezed.dart';
part 'create_order_request.g.dart';

@freezed
abstract class CreateOrderRequest with _$CreateOrderRequest {
  const factory CreateOrderRequest({
    required String recipientPhone,
    required String streamLat,
    required String streamLng,
    required String deliveryLat,
    required String deliveryLng,
    
  }) = _CreateOrderRequest;

  factory CreateOrderRequest.fromJson(Map<String, dynamic> json) =>
      _$CreateOrderRequestFromJson(json);
}