import 'package:flutter_map/flutter_map.dart' as fm;
import 'package:get/get.dart';
import 'package:latlong2/latlong.dart';

class MapController extends GetxController {
  final fm.MapController mapController = fm.MapController();

  // Demo coordinates (Hà Nội) - replace with live robot/order coordinates later.
  final LatLng robot = const LatLng(21.0286, 105.8352);
  final LatLng pickup = const LatLng(21.0278, 105.8342);
  final LatLng dropoff = const LatLng(21.0249, 105.8412);

  LatLng get initialCenter => robot;

  List<LatLng> get routePoints => [pickup, robot, dropoff];

  void recenter() {
    mapController.move(initialCenter, 15);
  }
}
