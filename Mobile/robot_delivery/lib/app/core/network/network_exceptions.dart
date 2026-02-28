import 'package:dio/dio.dart';

class NetworkException implements Exception {
  NetworkException(this.message, {this.statusCode, this.originalException});

  final String message;
  final int? statusCode;
  final Object? originalException;

  factory NetworkException.fromDioException(DioException exception) {
    final statusCode = exception.response?.statusCode;

    switch (exception.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return NetworkException('Kết nối bị timeout. Vui lòng thử lại.',
            statusCode: statusCode, originalException: exception);

      case DioExceptionType.badCertificate:
        return NetworkException('Chứng chỉ không hợp lệ.',
            statusCode: statusCode, originalException: exception);

      case DioExceptionType.connectionError:
        return NetworkException('Không có kết nối mạng.',
            statusCode: statusCode, originalException: exception);

      case DioExceptionType.cancel:
        return NetworkException('Yêu cầu đã bị huỷ.',
            statusCode: statusCode, originalException: exception);

      case DioExceptionType.badResponse:
        final msg = _extractServerMessage(exception.response) ??
            'Có lỗi xảy ra. Vui lòng thử lại.';
        return NetworkException(msg,
            statusCode: statusCode, originalException: exception);

      case DioExceptionType.unknown:
        return NetworkException('Có lỗi xảy ra. Vui lòng thử lại.',
            statusCode: statusCode, originalException: exception);
    }
  }

  static String? _extractServerMessage(Response? response) {
    final data = response?.data;

    if (data is Map) {
      final message = data['message'] ?? data['error'] ?? data['msg'];
      if (message is String && message.trim().isNotEmpty) {
        return message;
      }
    }

    if (data is String && data.trim().isNotEmpty) {
      return data;
    }

    return null;
  }

  @override
  String toString() => message;
}
