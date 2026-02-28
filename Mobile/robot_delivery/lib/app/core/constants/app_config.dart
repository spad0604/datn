class AppConfig {
  const AppConfig._();

  static const String baseUrl = 'https://jsonplaceholder.typicode.com';

  static const Duration connectTimeout = Duration(seconds: 60);
  static const Duration receiveTimeout = Duration(seconds: 60);
  static const Duration sendTimeout = Duration(seconds: 60);
}
