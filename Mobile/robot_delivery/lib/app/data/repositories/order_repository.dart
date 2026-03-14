import 'package:robot_delivery/app/core/constants/app_endpoints.dart';
import 'package:robot_delivery/app/core/network/api_client.dart';
import 'package:robot_delivery/app/data/models/request/create_order_request.dart';
import 'package:robot_delivery/app/data/models/response/order_response.dart';
import 'package:robot_delivery/app/data/models/response_data.dart';

class OrderRepository {
  OrderRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<ResponseData<OrderResponse>> createOrder(
    CreateOrderRequest request,
  ) async {
    try {
      final response = await _apiClient.post<dynamic>(
        AppEndpoints.createOrder,
        data: request.toJson(),
      );

      if (response is Map<String, dynamic>) {
        return ResponseData.fromJson(
          response,
          (json) => OrderResponse.fromJson(json as Map<String, dynamic>),
        );
      }

      return ResponseData(message: 'Failed to create order: Invalid response format.', data: null);
    } catch (e) {
      print('Create order error: $e');
      return ResponseData(message: 'Failed to create order: $e', data: null);
    }
  }

  Future<ResponseData<List<OrderResponse>>> getMyOrders() async {
    try {
      final response = await _apiClient.get<dynamic>(AppEndpoints.myOrder);

      if (response is Map<String, dynamic>) {
        return ResponseData.fromJson(
          response,
          (json) => (json as List<dynamic>)
              .map((e) => OrderResponse.fromJson(e as Map<String, dynamic>))
              .toList(),
        );
      }

      return ResponseData(message: 'Failed to fetch my orders: Invalid response format.', data: null);
    } catch (e) {
      print('Get my orders error: $e');
      return ResponseData(message: 'Failed to fetch my orders: $e', data: null);
    }
  }

  Future<ResponseData<List<OrderResponse>>> getMyReceivedOrders() async {
    try {
      final response = await _apiClient.get<dynamic>(AppEndpoints.myReceivedOrder);

      if (response is Map<String, dynamic>) {
        return ResponseData.fromJson(
          response,
          (json) => (json as List<dynamic>)
              .map((e) => OrderResponse.fromJson(e as Map<String, dynamic>))
              .toList(),
        );
      }

      return ResponseData(message: 'Failed to fetch my received orders: Invalid response format.', data: null);
    } catch (e) {
      print('Get my received orders error: $e');
      return ResponseData(
        message: 'Failed to fetch my received orders: $e',
        data: null,
      );
    }
  }

  Future<ResponseData<OrderResponse>> confirmSender(int orderId) async {
    try {
      final response = await _apiClient.post<dynamic>(
        AppEndpoints.confirmSender.replaceAll('{orderId}', orderId.toString()),
      );

      if (response is Map<String, dynamic>) {
        return ResponseData.fromJson(
          response,
          (json) => OrderResponse.fromJson(json as Map<String, dynamic>),
        );
      }

      return ResponseData(message: 'Failed to confirm sender: Invalid format.', data: null);
    } catch (e) {
      return ResponseData(message: 'Failed to confirm sender: $e', data: null);
    }
  }

  Future<ResponseData<OrderResponse>> confirmReceiver(int orderId) async {
    try {
      final response = await _apiClient.post<dynamic>(
        AppEndpoints.confirmReceiver.replaceAll('{orderId}', orderId.toString()),
      );

      if (response is Map<String, dynamic>) {
        return ResponseData.fromJson(
          response,
          (json) => OrderResponse.fromJson(json as Map<String, dynamic>),
        );
      }

      return ResponseData(message: 'Failed to confirm receiver: Invalid format.', data: null);
    } catch (e) {
      return ResponseData(message: 'Failed to confirm receiver: $e', data: null);
    }
  }
}
