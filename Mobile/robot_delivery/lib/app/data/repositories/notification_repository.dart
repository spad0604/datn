import 'package:robot_delivery/app/core/constants/app_endpoints.dart';
import 'package:robot_delivery/app/core/network/api_client.dart';
import 'package:robot_delivery/app/data/models/response/notification_response.dart';
import 'package:robot_delivery/app/data/models/response_data.dart';

class NotificationRepository {
  NotificationRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<ResponseData<List<NotificationResponse>>> getMyNotifications() async {
    try {
      final response = await _apiClient.get<dynamic>(AppEndpoints.myNotifications);

      if (response is Map<String, dynamic>) {
        return ResponseData.fromJson(
          response,
          (json) => (json as List<dynamic>)
              .map((e) => NotificationResponse.fromJson(e as Map<String, dynamic>))
              .toList(),
        );
      }

      return ResponseData(
        message: 'Failed to fetch my notifications: Invalid response format.',
        data: null,
      );
    } catch (e) {
      print('Get my notifications error: $e');
      return ResponseData(message: 'Failed to fetch my notifications: $e', data: null);
    }
  }

  Future<ResponseData<void>> markAsRead(int id) async {
    try {
      final response = await _apiClient.post<dynamic>(
        AppEndpoints.markNotificationRead.replaceAll('{id}', id.toString()),
      );

      return ResponseData(message: 'Success', data: null);
    } catch (e) {
      return ResponseData(message: 'Failed to mark as read: $e', data: null);
    }
  }
}
