class AppConfig {
  const AppConfig._();

  static const String baseServer = 'https://192.168.1.1:8080';

  static const String baseUrl = '${AppConfig.baseServer}/api/v1';

  static const Duration connectTimeout = Duration(seconds: 60);
  static const Duration receiveTimeout = Duration(seconds: 60);
  static const Duration sendTimeout = Duration(seconds: 60);
}
