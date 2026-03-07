class AppConfig {
  const AppConfig._();

  static const String baseUrl = 'https://192.168.1.1:8080/api/v1';

  static const Duration connectTimeout = Duration(seconds: 60);
  static const Duration receiveTimeout = Duration(seconds: 60);
  static const Duration sendTimeout = Duration(seconds: 60);
}
