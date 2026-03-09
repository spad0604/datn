import 'dart:async';
import 'dart:convert';
import 'dart:isolate';

import 'package:robot_delivery/app/core/constants/app_config.dart';
import 'package:stomp_dart_client/stomp_dart_client.dart';

class SocketIsolateService {
  static Future<void> spawn(SendPort mainSendPort, String robotId) async {
    final stompConfig = StompConfig(
      url: 'ws://${AppConfig.baseServer}/ws-delivery',
      onConnect: (frame) {
        print('Isolate: Connected to WebSocket');

        mainSendPort.send({'type': 'status', 'status': 'connected'});
      },
      onWebSocketDone: () => print('Isolate: WebSocket connection closed'),
      reconnectDelay: const Duration(seconds: 5),
    );

    final client = StompClient(config: stompConfig);

    client.activate();

    Timer.periodic(const Duration(microseconds: 500), (timer) {
      if (client.connected) {
        client.subscribe(
          destination: '/topic/robot/${robotId}',
          callback: (frame) {
            if (frame.body != null) {
              mainSendPort.send({
                'type': 'location',
                'data': jsonDecode(frame.body!),
              });
            }
          },
        );
      }
    });
  }
}
