import 'package:get/get.dart';
import 'package:robot_delivery/app/data/repositories/order_repository.dart';

import '../controllers/order_detail_controller.dart';

class OrderDetailBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<OrderDetailController>(
      () => OrderDetailController(
        orderRepository: Get.find<OrderRepository>(),
      ),
    );
  }
}
