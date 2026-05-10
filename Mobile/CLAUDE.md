# Mobile App - Robot Delivery

Flutter mobile application for managing delivery orders and tracking robots in real-time.

## Tech Stack
- **Flutter** 3.10.7+, Dart
- **State Management**: GetX 4.7.3 (controllers, bindings, reactive state)
- **HTTP Client**: Dio 5.9.1 with auth interceptor
- **WebSocket**: STOMP (stomp_dart_client) in isolate
- **Maps**: flutter_map 8.2.2 (OpenStreetMap)
- **Notifications**: Firebase Cloud Messaging + flutter_local_notifications
- **Code Gen**: Freezed (models), json_serializable
- **Storage**: flutter_secure_storage (tokens)

## Project Layout
```
lib/
├── main.dart                              # Firebase init, app entry
└── app/
    ├── core/
    │   ├── constants/
    │   │   ├── app_config.dart            # Base URL, WS URL, timeouts
    │   │   └── app_endpoints.dart         # All API paths
    │   ├── network/
    │   │   ├── api_client.dart            # Dio wrapper (get/post/put/delete)
    │   │   ├── auth_interceptor.dart      # JWT injection + refresh on 401
    │   │   └── network_exceptions.dart    # Error mapping (Vietnamese messages)
    │   ├── storage/
    │   │   └── secure_token_storage.dart  # Token persistence
    │   ├── theme/ and i18n/
    ├── data/
    │   ├── models/
    │   │   ├── request/  (login, register, create_order)
    │   │   └── response/ (order_response, login_response, notification_response)
    │   └── repositories/
    │       ├── auth_repository.dart
    │       ├── order_repository.dart
    │       ├── user_repository.dart
    │       ├── notification_repository.dart
    │       └── geocoding_repository.dart
    ├── modules/
    │   ├── main/          # Tab navigation (home, orders, map, profile)
    │   ├── home/          # Dashboard
    │   ├── orders/        # Order list + detail + create
    │   ├── map/           # Robot tracking map
    │   ├── login/         # Authentication
    │   ├── register/      # Registration
    │   ├── profile/       # User settings
    │   ├── notifications/ # Notification center
    │   └── splash/        # Splash screen
    ├── service/
    │   └── socket_isolate_service.dart  # WebSocket in isolate
    └── routes/            # GetX routing (app_pages, app_routes)
```

## Architecture Pattern

**GetX MVC+S**:
- **Views** (`GetView<T>`) - UI with reactive `Obx()` widgets
- **Controllers** (`GetxController`) - Business logic, reactive state (`Rx<T>`, `RxList<T>`)
- **Bindings** - Dependency injection per route
- **Repositories** - Data access layer (API calls)

## Key Features

### Order Management
- Create orders: sender picks recipient, sets pickup/delivery locations
- Track order status: WAIT_ROBOT -> PENDING -> DELIVERING -> DELIVERED
- Confirm sender/receiver actions with PIN verification
- View sent and received order lists

### Real-Time Robot Tracking
- WebSocket STOMP connection in a separate Dart isolate
- Subscribes to `/topic/robot/{robotId}` for location updates
- Map displays robot position, pickup/dropoff markers
- Auto-updates via reactive `TrackingRobotController`

### Authentication
- JWT login with token refresh on 401
- Secure token storage
- Auto-logout on refresh failure
- Concurrent refresh protection (prevents multiple refresh calls)

## Configuration
- Base URL: `http://3.27.122.108:9090/api/v1` (in `app_config.dart`)
- WS URL: `ws://3.27.122.108:9090/ws-delivery/websocket`
- Timeouts: 60 seconds
- Map center default: Hanoi (21.0286, 105.8352)

## Running
```bash
cd Mobile/robot_delivery
flutter pub get
flutter run
```

## Code Generation
After modifying Freezed models:
```bash
dart run build_runner build --delete-conflicting-outputs
```
