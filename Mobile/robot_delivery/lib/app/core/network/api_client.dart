import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../constants/app_config.dart';
import '../storage/secure_token_storage.dart';
import '../../data/repositories/auth_repository.dart';
import 'auth_interceptor.dart';
import 'network_exceptions.dart';

class ApiClient {
  ApiClient({
    Dio? dio,
    SecureTokenStorage? tokenStorage,
    AuthRepository? authRepository,
  })  : _dio = dio ?? Dio(),
        _tokenStorage = tokenStorage,
        _authRepository = authRepository {
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

    final tokenStorage = _tokenStorage;
    final authRepository = _authRepository;
    if (tokenStorage != null && authRepository != null) {
      _dio.interceptors.add(
        AuthInterceptor(
          dio: _dio,
          tokenStorage: tokenStorage,
          authRepository: authRepository,
        ),
      );
    }

    if (kDebugMode) {
      _dio.interceptors.add(
        LogInterceptor(
          requestHeader: false,
          requestBody: true,
          responseHeader: false,
          responseBody: true,
          error: true,
        ),
      );
    }
  }

  final Dio _dio;
  final SecureTokenStorage? _tokenStorage;
  final AuthRepository? _authRepository;

  Future<T> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.get<T>(
        path,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw NetworkException.fromDioException(e);
    }
  }

  Future<T> post<T>(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.post<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw NetworkException.fromDioException(e);
    }
  }

  Future<T> put<T>(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.put<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw NetworkException.fromDioException(e);
    }
  }

  Future<T> delete<T>(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.delete<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw NetworkException.fromDioException(e);
    }
  }
}
