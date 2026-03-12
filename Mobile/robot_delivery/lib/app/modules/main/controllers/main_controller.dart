import 'package:get/get.dart';
import 'package:robot_delivery/app/common/widget/app_bottom_nav_bar.dart';
import 'package:robot_delivery/app/data/models/response/order_response.dart';
import 'package:robot_delivery/app/data/repositories/order_repository.dart';

class MainController extends GetxController {
  final RxInt tabIndex = 0.obs;

  final OrderRepository orderRepository = Get.find<OrderRepository>();

  final RxList<OrderResponse> myOrders = <OrderResponse>[].obs;

  final RxList<OrderResponse> myReceivedOrders = <OrderResponse>[].obs;

  bool _didSetInitialTab = false;

  @override
  void onInit() {
    super.onInit();
    fetchMyReceivedOrders();
    fetchMyOrders();
  }

  Future<void> fetchMyReceivedOrders() async {
    final response = await orderRepository.getMyReceivedOrders();
    if (response.data != null) {
      myReceivedOrders.value = response.data!;
    } else {
      print('Failed to fetch my received orders: ${response.message}');
    }
  }

  Future<void> fetchMyOrders() async {
    final response = await orderRepository.getMyOrders();
    if (response.data != null) {
      myOrders.value = response.data!;
    } else {
      print('Failed to fetch my orders: ${response.message}');
    }
  }

  void setInitialTab(AppNavTab tab) {
    if (_didSetInitialTab) return;
    _didSetInitialTab = true;
    tabIndex.value = AppNavTab.values.indexOf(tab);
  }

  void setTabIndex(int index) {
    if (index < 0 || index >= AppNavTab.values.length) return;
    tabIndex.value = index;
  }

  AppNavTab get currentTab => AppNavTab.values[tabIndex.value];
}
