import 'package:get/get.dart';
import 'package:robot_delivery/app/core/network/api_client.dart';
import 'package:robot_delivery/app/data/repositories/notification_repository.dart';

import '../controllers/notifications_controller.dart';

class NotificationsBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<NotificationRepository>(() => NotificationRepository(Get.find<ApiClient>()));
    Get.lazyPut<NotificationsController>(() => NotificationsController());
  }
}
