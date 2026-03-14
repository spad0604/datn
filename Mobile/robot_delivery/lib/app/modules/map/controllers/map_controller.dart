import 'package:flutter_map/flutter_map.dart' as fm;
import 'package:get/get.dart';
import 'package:latlong2/latlong.dart';
import 'package:robot_delivery/app/data/models/response/order_response.dart';
import 'package:robot_delivery/app/modules/main/controllers/main_controller.dart';

enum MarkerType { pickup, dropoff }

class OrderMarkerData {
  final OrderResponse order;
  final LatLng position;
  final MarkerType type;

  OrderMarkerData({required this.order, required this.position, required this.type});
}

class MapController extends GetxController {
  final fm.MapController mapController = fm.MapController();
  final MainController mainController = Get.find<MainController>();

  final LatLng defaultCenter = const LatLng(21.0286, 105.8352); // Hanoi default

  List<OrderMarkerData> get markersData {
    final list = <OrderMarkerData>[];
    
    // Đơn mình gửi
    for (var o in mainController.myOrders) {
      if (o.status == 'DELIVERED') continue;
      
      final startLat = double.tryParse(o.startLat.toString());
      final startLng = double.tryParse(o.startLng.toString());
      if (startLat != null && startLng != null) {
        list.add(OrderMarkerData(
          order: o,
          position: LatLng(startLat, startLng),
          type: MarkerType.pickup,
        ));
      }

      final deliveryLat = double.tryParse(o.deliveryLat.toString());
      final deliveryLng = double.tryParse(o.deliveryLng.toString());
      if (deliveryLat != null && deliveryLng != null) {
        list.add(OrderMarkerData(
          order: o,
          position: LatLng(deliveryLat, deliveryLng),
          type: MarkerType.dropoff,
        ));
      }
    }

    // Đơn mình nhận
    for (var o in mainController.myReceivedOrders) {
      if (o.status == 'DELIVERED') continue;

      final deliveryLat = double.tryParse(o.deliveryLat.toString());
      final deliveryLng = double.tryParse(o.deliveryLng.toString());
      if (deliveryLat != null && deliveryLng != null) {
        list.add(OrderMarkerData(
          order: o,
          position: LatLng(deliveryLat, deliveryLng),
          type: MarkerType.dropoff,
        ));
      }
    }

    return list;
  }

  void recenter() {
    final m = markersData;
    if (m.isNotEmpty) {
      mapController.move(m.first.position, 13);
    } else {
      mapController.move(defaultCenter, 13);
    }
  }
}
