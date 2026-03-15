class AppEndpoints {
  const AppEndpoints._();

  static const String todo = '/todos/1';

  // Auth
  static const String refreshToken = '/auth/refresh-token';

  static const String register = '/auth/register';
  static const String login = '/auth/login';
  static const String changePassword = '/auth/change-password';

  static const String deleteOrder = '/orders/delete/{orderId}';
  static const String createOrder = '/orders/create';
  static const String myOrder = '/orders/my-created';
  static const String myReceivedOrder = '/orders/my-received';
  static const String updateOrder = '/orders/update/{orderId}';
  static const String confirmSender = '/orders/{orderId}/confirm-sender';
  static const String confirmReceiver = '/orders/{orderId}/confirm-receiver';
  static const String searchUser = '/users/search';
  static const String myInfo = '/users/my-info';

  static const String myNotifications = '/notifications';
  static const String markNotificationRead = '/notifications/{id}/read';

  static const String uploadAvatarUrl = '/users/upload_avatar';
}
