import 'package:robot_delivery/app/core/constants/app_endpoints.dart';
import 'package:robot_delivery/app/core/network/api_client.dart';
import 'package:robot_delivery/app/data/models/request/create_order_request.dart';
import 'package:robot_delivery/app/data/models/response/order_response.dart';
import 'package:robot_delivery/app/data/models/response_data.dart';

abstract class OrderRepository {
  OrderRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<ResponseData<OrderResponse>> createOrder(
    CreateOrderRequest request,
  ) async {
    try {
      final response = await _apiClient.post(
        AppEndpoints.createOrder,
        data: request.toJson(),
      );

      return response;
    } catch (e) {
      print('Create order error: $e');
      return ResponseData(message: 'Failed to create order: $e', data: null);
    }
  }

  Future<ResponseData<List<OrderResponse>>> getMyOrders() async {
    try {
      final response = await _apiClient.get(AppEndpoints.myOrder);

      return response;
    } catch (e) {
      print('Get my orders error: $e');
      return ResponseData(message: 'Failed to fetch my orders: $e', data: null);
    }
  }

  Future<ResponseData<List<OrderResponse>>> getMyReceivedOrders() async {
    try {
      final response = await _apiClient.get(AppEndpoints.myReceivedOrder);

      return response;
    } catch (e) {
      print('Get my received orders error: $e');
      return ResponseData(
        message: 'Failed to fetch my received orders: $e',
        data: null,
      );
    }
  }
}
