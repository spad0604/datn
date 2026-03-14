import 'dart:isolate';

import 'package:get/get.dart';
import 'package:latlong2/latlong.dart';
import 'package:robot_delivery/app/service/socket_isolate_service.dart';

class TrackingRobotController extends GetxController {
  final Rx<LatLng?> robotLocation = Rx<LatLng?>(null);

  Isolate? _isolate;
  final ReceivePort _receivePort = ReceivePort();

  void startTracking(String robotId) async {
    stopTracking();

    _isolate = await Isolate.spawn(
      SocketIsolateService.spawnIsolateEntry,
      [_receivePort.sendPort, robotId],
    );

    _receivePort.listen((message) {
      if (message is Map && message['type'] == 'location') {
        final data = message['data'];
        if (data != null) {
          final lat = double.tryParse(data['lat']?.toString() ?? '');
          final lng = double.tryParse(data['lng']?.toString() ?? '');
          if (lat != null && lng != null) {
            robotLocation.value = LatLng(lat, lng);
          }
        }
      }
    });
  }

  void stopTracking() {
    _isolate?.kill(priority: Isolate.immediate);
    _isolate = null;
  }

  @override
  void onClose() {
    stopTracking();
    _receivePort.close();
    super.onClose();
  }
}
