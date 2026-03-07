import 'package:freezed_annotation/freezed_annotation.dart';

part 'order_response.freezed.dart';
part 'order_response.g.dart';

@freezed
abstract class OrderResponse with _$OrderResponse {
  const factory OrderResponse({
    required int id,
    required String orderId,
    required Customer customer,
    required Customer recipient,
    required String recipientPhone,
    required double streamLat,
    required double streamLng,
    required double deliveryLat,
    required double deliveryLng,
    required String pinCode,
    required String senderName,
    required int robotId,
    required String robotName,
    required String status,
    required DateTime createdAt,
  }) = _OrderResponse;

  factory OrderResponse.fromJson(Map<String, dynamic> json) => _$OrderResponseFromJson(json);
}

@freezed
abstract class Customer with _$Customer {
  const factory Customer({
    required int id,
    required String username,
    required String fullName,
    required String phoneNumber,
  }) = _Customer;

  factory Customer.fromJson(Map<String, dynamic> json) => _$CustomerFromJson(json);
}