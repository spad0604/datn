import 'package:dio/dio.dart';
import 'package:robot_delivery/app/data/models/response_data.dart';

import '../../core/constants/app_config.dart';
import '../../core/constants/app_endpoints.dart';
import '../../core/network/network_exceptions.dart';
import '../models/request/login_request.dart';
import '../models/request/register_request.dart';
import '../models/response/login_response.dart';

class AuthRepository {
  AuthRepository({Dio? dio}) : _dio = dio ?? Dio() {
    _dio.options = BaseOptions(
      baseUrl: AppConfig.baseUrl,
      connectTimeout: AppConfig.connectTimeout,
      receiveTimeout: AppConfig.receiveTimeout,
      sendTimeout: AppConfig.sendTimeout,
      headers: const {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    );
  }

  final Dio _dio;

  Future<ResponseData<LoginResponse>> login(LoginRequest request) async {
    try {
      final response = await _dio.post<dynamic>(
        AppEndpoints.login,
        data: request.toJson(),
      );
      final data = response.data;
      if (data is Map<String, dynamic>) {
        return ResponseData.fromJson(
          data,
          (json) => LoginResponse.fromJson(json as Map<String, dynamic>),
        );
      }

      print('Login error: Invalid response format.');
      return ResponseData(message: 'Login failed: Invalid response format.', data: null);
    } on DioException catch (e) {
      print('Login error: ${e.message}');
      return ResponseData(message: 'Login failed: ${e.message}', data: null);
    }
  }

  Future<ResponseData<LoginResponse>> register(RegisterRequest request) async {
    try {
      final response = await _dio.post<dynamic>(
        AppEndpoints.register,
        data: request.toJson(),
      );

      final data = response.data;
      if (data is Map<String, dynamic>) {
        return ResponseData(message: 'Registration successful.', data: LoginResponse.fromJson(data));
      }

      print('Register error: Invalid response format.');
      return ResponseData(message: 'Registration failed: Invalid response format.', data: null);
    } on DioException catch (e) {
      print('Register error: ${e.message}');
      return ResponseData(message: 'Registration failed: ${e.message}', data: null);
    }
  }

  /// Calls refresh token endpoint.
  /// Input: refreshToken
  /// Output: LoginRequest
  Future<ResponseData<LoginResponse>> refreshToken({required String refreshToken}) async {
    try {
      final response = await _dio.post<dynamic>(
        AppEndpoints.refreshToken,
        data: {
          'refreshToken': refreshToken,
        },
      );

      final data = response.data;
      if (data is Map<String, dynamic>) {
        return ResponseData(message: 'Token refreshed successfully.', data: LoginResponse.fromJson(data));
      }

      throw NetworkException('Refresh token response không hợp lệ.',
          statusCode: response.statusCode);
    } on DioException catch (e) {
      throw NetworkException.fromDioException(e);
    }
  }
}
