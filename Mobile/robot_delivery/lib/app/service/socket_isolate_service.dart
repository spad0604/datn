import 'dart:convert';
import 'dart:isolate';

import 'package:robot_delivery/app/core/constants/app_config.dart';
import 'package:stomp_dart_client/stomp_dart_client.dart';

class SocketIsolateService {
  /// Entry point for Isolate.spawn (must be a top-level or static function).
  /// args[0] = SendPort, args[1] = robotId (String)
  static void spawnIsolateEntry(List<dynamic> args) {
    final sendPort = args[0] as SendPort;
    final robotId = args[1] as String;

    StompClient? clientRef;

    clientRef = StompClient(
      config: StompConfig(
        url: AppConfig.wsUrl,
        onConnect: (frame) {
          sendPort.send({'type': 'status', 'status': 'connected'});

          clientRef?.subscribe(
            destination: '/topic/robot/$robotId',
            callback: (StompFrame frame) {
              if (frame.body != null) {
                try {
                  sendPort.send({
                    'type': 'location',
                    'data': jsonDecode(frame.body!),
                  });
                } catch (_) {}
              }
            },
          );
        },
        onWebSocketError: (error) => print('Isolate WS error: $error'),
        onWebSocketDone: () => print('Isolate WS closed'),
        reconnectDelay: const Duration(seconds: 5),
      ),
    );

    clientRef.activate();
  }
}
