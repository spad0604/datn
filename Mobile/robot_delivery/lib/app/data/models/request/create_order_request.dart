import 'package:freezed_annotation/freezed_annotation.dart';
part 'create_order_request.freezed.dart';
part 'create_order_request.g.dart';

@freezed
abstract class CreateOrderRequest with _$CreateOrderRequest {
  const factory CreateOrderRequest({
    required String recipientPhone,
    required double startLat,
    required double startLng,
    required double deliveryLat,
    required double deliveryLng,
    String? senderAddress,
    String? deliveryAddress,
  }) = _CreateOrderRequest;



  factory CreateOrderRequest.fromJson(Map<String, dynamic> json) =>
      _$CreateOrderRequestFromJson(json);
}