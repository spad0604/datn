import '../../core/constants/app_endpoints.dart';
import '../../core/network/api_client.dart';

class SampleRepository {
  SampleRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<Map<String, dynamic>> fetchTodo() async {
    final data = await _apiClient.get<dynamic>(AppEndpoints.todo);
    if (data is Map<String, dynamic>) {
      return data;
    }
    return <String, dynamic>{};
  }
}
