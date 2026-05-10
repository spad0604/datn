# Backend - Robot Delivery Server

Spring Boot 4.0.3 REST + WebSocket server for the robot delivery system.

## Tech Stack
- **Java 17**, Spring Boot 4.0.3, Spring Data JPA
- **Database**: PostgreSQL (Supabase cloud - `aws-1-ap-northeast-1.pooler.supabase.com`)
- **Auth**: JWT (JJWT 0.13.0) for users, shared secret key for robots
- **WebSocket**: Spring STOMP for real-time communication
- **External**: Cloudinary (image storage), Firebase Admin SDK (push notifications)

## Project Layout
```
src/main/java/com/example/robot_delivery/
├── RobotDeliveryApplication.java     # Entry point (@EnableScheduling)
├── config/
│   ├── WebSocketConfig.java          # STOMP broker + endpoints
│   ├── CloudinaryConfig.java
│   └── FirebaseConfig.java
├── controller/
│   ├── AuthController.java           # /api/v1/auth/*
│   ├── OrderController.java          # /api/v1/orders/*
│   ├── RobotApiController.java       # /api/v1/robot/* (secret-key auth)
│   ├── RobotLocationController.java  # WebSocket /app/update-location
│   ├── UserController.java           # /api/v1/users/*
│   └── NotificationController.java   # /api/v1/notifications/*
├── service/
│   ├── RobotDispatchService.java     # Auto-assigns robots (scheduled @10s)
│   └── RobotOrderEventPublisher.java # Publishes order events via STOMP
├── impl/
│   ├── OrderServiceImpl.java
│   ├── RobotServiceImpl.java
│   └── UserServiceImpl.java
├── model/
│   ├── Order.java, Robot.java, User.java, Notification.java
│   ├── enums/ (OrderStatusEnum, RobotStatusEnum)
│   ├── request/ (DTOs)
│   └── responses/ (DTOs)
├── security/
│   ├── SecurityConfig.java           # Endpoint permissions
│   ├── JwtService.java               # Token generation/validation
│   └── JwtAuthenticationFilter.java
└── repositorys/                      # JPA repositories
```

## Key Endpoints

### REST API (JWT auth for users)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/login` | User login, returns JWT |
| POST | `/api/v1/auth/register` | User registration |
| POST | `/api/v1/orders/create` | Create order (auto-assigns nearest robot) |
| PUT | `/api/v1/orders/update/{id}` | Update order |
| GET | `/api/v1/orders/my-created` | User's sent orders |
| GET | `/api/v1/orders/my-received` | User's received orders |
| POST | `/api/v1/orders/{id}/confirm-sender` | Sender confirms pickup |
| POST | `/api/v1/orders/{id}/confirm-receiver` | Receiver confirms delivery |

### Robot API (shared secret auth via `X-Robot-Secret` header)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/robot/{robotId}/current-order` | Robot fetches its current order |

### WebSocket (STOMP)
| Direction | Destination | Description |
|-----------|-------------|-------------|
| Robot -> BE | `/app/update-location` | Robot sends GPS location |
| BE -> Robot | `/topic/robot-order/{robotId}` | Order events (assigned, cancelled, status changed) |
| BE -> Mobile | `/topic/robot{robotId}` | Robot location broadcasts |

## Business Logic

### Robot Dispatch (RobotDispatchService)
- Runs every 10 seconds (`@Scheduled`)
- Finds orders in `WAIT_ROBOT` status
- Finds all `IDLE` robots
- Assigns nearest robot using Haversine distance
- Updates: order status -> `PENDING`, robot status -> `PICKING_UP`
- Publishes `ORDER_ASSIGNED` event via WebSocket

### Order Status Flow
```
WAIT_ROBOT -> PENDING (robot assigned) -> DELIVERING -> DELIVERED
```

### Robot Status Flow
```
IDLE -> PICKING_UP -> DELIVERING -> IDLE
```

## Security
- Public endpoints: `/api/v1/auth/**`, `/api/v1/robot/**`, `/ws-delivery/**`, `/ws-delivery-native/**`
- All other endpoints require JWT Bearer token
- Robot auth uses shared secret: `DATN_2025_2_GIAP`
- JWT expiration: 30 minutes
- CSRF disabled (stateless API)

## Running
```bash
cd BE/robot_delivery
./mvnw spring-boot:run
```
Server starts on port 8080.
