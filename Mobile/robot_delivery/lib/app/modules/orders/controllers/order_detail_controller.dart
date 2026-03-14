import 'package:get/get.dart';
import 'package:latlong2/latlong.dart';
import 'package:robot_delivery/app/core/network/external_api_client.dart';
import 'package:robot_delivery/app/data/models/response/order_response.dart';
import 'package:robot_delivery/app/data/repositories/order_repository.dart';
import 'package:robot_delivery/app/core/utils/app_snackbar.dart';
import 'package:robot_delivery/app/modules/main/controllers/main_controller.dart';
import 'package:robot_delivery/app/modules/map/controllers/tracking_robot_controller.dart';

class OrderDetailController extends GetxController {
  OrderDetailController({required OrderRepository orderRepository})
    : _orderRepository = orderRepository;

  final OrderRepository _orderRepository;

  final Rx<OrderResponse?> currentOrder = Rx<OrderResponse?>(null);
  final RxBool isLoading = true.obs;
  final RxList<LatLng> routePoints = <LatLng>[].obs;

  late final TrackingRobotController _trackingController;

  bool isSender = false;

  Rx<LatLng?> get robotLocation => _trackingController.robotLocation;

  @override
  void onInit() {
    super.onInit();
    _trackingController = TrackingRobotController();

    final order = Get.arguments as OrderResponse?;
    if (order != null) {
      currentOrder.value = order;
      isLoading.value = false;

      try {
        final mainController = Get.find<MainController>();
        isSender = mainController.myOrders.any((o) => o.id == order.id);
      } catch (_) {}

      if (order.robotId != 0 &&
          (order.status == 'PENDING' ||
              order.status == 'DELIVERING' ||
              order.status == 'WAIT_ROBOT')) {
        _trackingController.startTracking(order.robotId.toString());
      }

      _fetchRoute(
        order.startLat,
        order.startLng,
        order.deliveryLat,
        order.deliveryLng,
      );
    }
  }

  Future<void> deleteOrder() async {
    try {
      final orderId = currentOrder.value?.id;

      if (orderId == null) return;

      await _orderRepository.deleteOrder(orderId);

      Get.back();

      return;
    } catch (e) {
      return;
    }
  }

  Future<void> _fetchRoute(
    double startLat,
    double startLng,
    double destLat,
    double destLng,
  ) async {
    try {
      final url =
          'https://router.project-osrm.org/route/v1/driving/$startLng,$startLat;$destLng,$destLat?geometries=geojson';
      final data = await ExternalApiClient.get(url);
      final routes = data['routes'] as List;
      if (routes.isNotEmpty) {
        final coordinates = routes[0]['geometry']['coordinates'] as List;
        routePoints.value = coordinates.map((c) {
          return LatLng((c[1] as num).toDouble(), (c[0] as num).toDouble());
        }).toList();
      }
    } catch (e) {
      print('Fetch route error: $e');
      routePoints.value = [
        LatLng(startLat, startLng),
        LatLng(destLat, destLng),
      ];
    }
  }

  @override
  void onClose() {
    _trackingController.onClose();
    super.onClose();
  }

  Future<void> confirmSender() async {
    final orderId = currentOrder.value?.id;
    if (orderId == null) return;

    try {
      final res = await _orderRepository.confirmSender(orderId);
      if (res.data != null) {
        currentOrder.value = res.data;
        AppSnackbar.success('Đã xác nhận gửi hàng!');
      } else {
        AppSnackbar.error(res.message ?? 'Lỗi xác nhận');
      }
    } catch (e) {
      AppSnackbar.error('Có lỗi xảy ra');
    }
  }

  Future<void> confirmReceiver() async {
    final orderId = currentOrder.value?.id;
    if (orderId == null) return;

    try {
      final res = await _orderRepository.confirmReceiver(orderId);
      if (res.data != null) {
        currentOrder.value = res.data;
        AppSnackbar.success('Đã xác nhận nhận hàng!');
      } else {
        AppSnackbar.error(res.message ?? 'Lỗi xác nhận');
      }
    } catch (e) {
      AppSnackbar.error('Có lỗi xảy ra');
    }
  }
}
