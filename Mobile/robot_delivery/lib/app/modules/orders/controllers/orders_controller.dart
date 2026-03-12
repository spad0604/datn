import 'package:flutter/widgets.dart';
import 'package:get/get.dart';
import 'package:robot_delivery/app/data/models/response/order_response.dart';
import 'package:robot_delivery/app/modules/main/controllers/main_controller.dart';

class OrdersController extends GetxController {
  final TextEditingController recipientNameController = TextEditingController();
  final TextEditingController recipientAddressController = TextEditingController();
  final TextEditingController weightController = TextEditingController();

  final MainController _mainController = Get.find<MainController>();

  RxList<OrderResponse> get myOrders => _mainController.myOrders;

  Future<void> refresh() => _mainController.fetchMyOrders();
}
