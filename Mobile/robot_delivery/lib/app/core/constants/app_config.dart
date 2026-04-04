class AppConfig {
  const AppConfig._();

  static const String baseServer = 'sallie-quartziferous-shantelle.ngrok-free.dev';

  static const String baseUrl = 'https://${AppConfig.baseServer}/api/v1';
  static const String wsUrl = 'ws://${AppConfig.baseServer}/ws-delivery/websocket';

  static const Duration connectTimeout = Duration(seconds: 60);
  static const Duration receiveTimeout = Duration(seconds: 60);
  static const Duration sendTimeout = Duration(seconds: 60);
}
