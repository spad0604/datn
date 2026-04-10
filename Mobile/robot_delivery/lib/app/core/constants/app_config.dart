class AppConfig {
  const AppConfig._();

  static const String baseServer = '3.27.122.108:9090';

  static const String baseUrl = 'http://${AppConfig.baseServer}/api/v1';
  static const String wsUrl = 'ws://${AppConfig.baseServer}/ws-delivery/websocket';

  static const Duration connectTimeout = Duration(seconds: 60);
  static const Duration receiveTimeout = Duration(seconds: 60);
  static const Duration sendTimeout = Duration(seconds: 60);
}
