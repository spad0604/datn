import 'dart:async';

import 'package:dio/dio.dart';

import '../../data/repositories/auth_repository.dart';
import '../constants/app_endpoints.dart';
import '../storage/secure_token_storage.dart';

class AuthInterceptor extends Interceptor {
  AuthInterceptor({
    required Dio dio,
    required SecureTokenStorage tokenStorage,
    required AuthRepository authRepository,
  })  : _dio = dio,
        _tokenStorage = tokenStorage,
        _authRepository = authRepository;

  final Dio _dio;
  final SecureTokenStorage _tokenStorage;
  final AuthRepository _authRepository;

  Completer<void>? _refreshCompleter;

  static const _kRetriedKey = '__retried';

  @override
  Future<void> onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final skipAuth = options.extra['skipAuth'] == true;
    if (skipAuth) {
      handler.next(options);
      return;
    }

    final accessToken = await _tokenStorage.readAccessToken();
    if (accessToken != null && accessToken.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }
    handler.next(options);
  }

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    final statusCode = err.response?.statusCode;
    final requestOptions = err.requestOptions;
    final skipAuth = requestOptions.extra['skipAuth'] == true;

    final isUnauthorized = statusCode == 401;
    final isRefreshRequest = requestOptions.path == AppEndpoints.refreshToken;
    final wasRetried = requestOptions.extra[_kRetriedKey] == true;

    if (skipAuth || !isUnauthorized || isRefreshRequest || wasRetried) {
      handler.next(err);
      return;
    }

    try {
      await _refreshTokensIfNeeded();

      final newAccessToken = await _tokenStorage.readAccessToken();
      if (newAccessToken == null || newAccessToken.isEmpty) {
        handler.next(err);
        return;
      }

      final response = await _retryWithNewToken(requestOptions, newAccessToken);
      handler.resolve(response);
    } catch (_) {
      // If refresh fails, clear tokens so app can force re-login.
      await _tokenStorage.clearTokens();
      handler.next(err);
    }
  }

  Future<void> _refreshTokensIfNeeded() async {
    // If a refresh is already in progress, await it.
    if (_refreshCompleter != null) {
      return _refreshCompleter!.future;
    }

    _refreshCompleter = Completer<void>();

    try {
      final refreshToken = await _tokenStorage.readRefreshToken();
      if (refreshToken == null || refreshToken.isEmpty) {
        throw StateError('Missing refresh token');
      }

      final tokens = await _authRepository.refreshToken(refreshToken: refreshToken);
      await _tokenStorage.writeTokens(
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
      );

      _refreshCompleter!.complete();
    } catch (e) {
      _refreshCompleter!.completeError(e);
      rethrow;
    } finally {
      _refreshCompleter = null;
    }
  }

  Future<Response<dynamic>> _retryWithNewToken(RequestOptions requestOptions, String accessToken) {
    final options = Options(
      method: requestOptions.method,
      headers: Map<String, dynamic>.from(requestOptions.headers)
        ..['Authorization'] = 'Bearer $accessToken',
      responseType: requestOptions.responseType,
      contentType: requestOptions.contentType,
      followRedirects: requestOptions.followRedirects,
      receiveDataWhenStatusError: requestOptions.receiveDataWhenStatusError,
      validateStatus: requestOptions.validateStatus,
      receiveTimeout: requestOptions.receiveTimeout,
      sendTimeout: requestOptions.sendTimeout,
    );

    requestOptions.extra[_kRetriedKey] = true;

    return _dio.request<dynamic>(
      requestOptions.path,
      data: requestOptions.data,
      queryParameters: requestOptions.queryParameters,
      options: options,
      cancelToken: requestOptions.cancelToken,
      onReceiveProgress: requestOptions.onReceiveProgress,
      onSendProgress: requestOptions.onSendProgress,
    );
  }
}
