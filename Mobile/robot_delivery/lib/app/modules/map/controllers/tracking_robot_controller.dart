import 'dart:isolate';

import 'package:get/get.dart';
import 'package:robot_delivery/app/service/socket_isolate_service.dart';

class TrackingRobotController extends GetxController {
  RxDouble robotLat = 0.0.obs;
  RxDouble robotLng = 0.0.obs;

  Isolate? _isolate;

  final ReceivePort _receivePort = ReceivePort();

  void startTracking(String robotId) async {
    stopTracking();

    _isolate = await Isolate.spawn(_isolateEntry, [
      _receivePort.sendPort,
      robotId,
    ]);

    _receivePort.listen((message) {
      if (message['type'] == 'location') {
        final data = message['data'];
        robotLat.value = data['latitude'];
        robotLng.value = data['longitude'];
      }
    });
  }

  static void _isolateEntry(List<dynamic> args) {
    SendPort sendPort = args[0];
    String rId = args[1];
    SocketIsolateService.spawn(sendPort, rId);
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
