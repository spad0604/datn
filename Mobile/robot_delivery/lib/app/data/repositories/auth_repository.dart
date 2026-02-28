import 'package:dio/dio.dart';

import '../../core/constants/app_config.dart';
import '../../core/constants/app_endpoints.dart';
import '../../core/network/network_exceptions.dart';
import '../models/auth_tokens.dart';

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

  /// Calls refresh token endpoint.
  /// Expected response json keys (configurable per backend):
  /// - accessToken / access_token
  /// - refreshToken / refresh_token
  Future<AuthTokens> refreshToken({required String refreshToken}) async {
    try {
      final response = await _dio.post<dynamic>(
        AppEndpoints.refreshToken,
        data: {
          'refreshToken': refreshToken,
        },
      );

      final data = response.data;
      if (data is Map) {
        final access = (data['accessToken'] ?? data['access_token']) as String?;
        final refresh = (data['refreshToken'] ?? data['refresh_token']) as String?;
        if (access != null && access.isNotEmpty && refresh != null && refresh.isNotEmpty) {
          return AuthTokens(accessToken: access, refreshToken: refresh);
        }
      }

      throw NetworkException('Refresh token response không hợp lệ.',
          statusCode: response.statusCode);
    } on DioException catch (e) {
      throw NetworkException.fromDioException(e);
    }
  }
}
