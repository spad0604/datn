import 'package:robot_delivery/app/core/constants/app_endpoints.dart';
import 'package:robot_delivery/app/core/network/api_client.dart';
import 'package:robot_delivery/app/data/models/response/order_response.dart';
import 'package:robot_delivery/app/data/models/response_data.dart';

class UserRepository {
  UserRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<ResponseData<Customer>> searchUserByPhone(String phoneNumber) async {
    try {
      final response = await _apiClient.get<dynamic>(
        AppEndpoints.searchUser,
        queryParameters: {'phoneNumber': phoneNumber},
      );

      if (response is Map<String, dynamic>) {
        return ResponseData<Customer>.fromJson(
          response,
          (json) => json == null ? null as dynamic : Customer.fromJson(json as Map<String, dynamic>),
        );
      }

      return ResponseData(message: 'Failed to search user: Invalid response format.', data: null);
    } catch (e) {
      print('Search user error: $e');
      return ResponseData(message: 'Failed to search user: $e', data: null);
    }
  }

  Future<ResponseData<Customer>> getMyInfo() async {
    try {
      final response = await _apiClient.get<dynamic>(
        AppEndpoints.myInfo,
      );

      if (response is Map<String, dynamic>) {
        return ResponseData<Customer>.fromJson(
          response,
          (json) => json == null ? null as dynamic : Customer.fromJson(json as Map<String, dynamic>),
        );
      }

      return ResponseData(message: 'Failed to get profile: Invalid response format.', data: null);
    } catch (e) {
      print('Get profile error: $e');
      return ResponseData(message: 'Failed to get profile: $e', data: null);
    }
  }
}
