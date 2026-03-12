class AppConfig {
  const AppConfig._();

  static const String baseServer = '192.168.100.153:8080';

  static const String baseUrl = 'http://${AppConfig.baseServer}/api/v1';

  static const Duration connectTimeout = Duration(seconds: 60);
  static const Duration receiveTimeout = Duration(seconds: 60);
  static const Duration sendTimeout = Duration(seconds: 60);
}
