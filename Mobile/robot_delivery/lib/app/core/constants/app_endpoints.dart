class AppEndpoints {
  const AppEndpoints._();

  static const String todo = '/todos/1';

  // Auth
  static const String refreshToken = '/auth/refresh-token';

  static const String register = '/auth/register';
  static const String login = '/auth/login';
  static const String changePassword = '/auth/change-password';

  static const String createOrder = '/orders/create';
  static const String myOrder = '/orders/my-created';
  static const String myReceivedOrder = '/orders/my-received';
  static const String updateOrder = '/orders/update/{orderId}';
}
