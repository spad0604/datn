# Robot Delivery System - DATN (Do An Tot Nghiep)

An autonomous delivery robot system consisting of 4 main components: Backend server, Flutter mobile app, ROS1 robot workspace, and ESP32 microcontroller firmware.

## Architecture Overview

```
Mobile App (Flutter) <--REST/WS--> Backend (Spring Boot) <--WS/REST--> ROS (Raspberry Pi) <--UART--> MCU (ESP32)
```

### Communication Flow
1. **User** creates order via Mobile App -> Backend assigns nearest idle robot
2. **Backend** pushes order to robot via WebSocket STOMP (`/topic/robot-order/{robotId}`)
3. **Robot (ROS)** receives order, converts GPS waypoints to map frame, navigates autonomously
4. **Robot** sends location updates back to Backend via STOMP (`/app/update-location`)
5. **Mobile App** receives real-time robot location via WebSocket (`/topic/robot{robotId}`)
6. **MCU (ESP32)** handles low-level motor control with PID, communicates with ROS via UART

### Order Lifecycle
```
WAIT_ROBOT -> PENDING (robot assigned) -> DELIVERING -> DELIVERED
```

## Project Structure

| Directory       | Component              | Tech Stack                        |
|-----------------|------------------------|-----------------------------------|
| `BE/`           | Backend server         | Spring Boot 4, Java 17, PostgreSQL |
| `Mobile/`       | Mobile app             | Flutter, GetX, Dio                |
| `new_robot_ws/` | ROS workspace (active) | ROS1 Noetic, Python 3             |
| `MCU/ESP32/`    | Motor controller       | Arduino/ESP32, C++                |
| `robot_ws/`     | Legacy ROS workspace   | (deprecated, reference only)      |
| `Altium/`       | PCB design             | Altium Designer                   |
| `documents/`    | Thesis document        | LaTeX                             |

## Key Configuration

- **Shared Secret**: `DATN_2025_2_GIAP` (used for robot<->BE auth, not JWT)
- **WebSocket endpoints**:
  - `/ws-delivery` (SockJS, for browser/mobile)
  - `/ws-delivery-native` (native WS, for Python/robot)
- **STOMP destinations**:
  - `/topic/robot-order/{robotId}` - order events to robot
  - `/topic/robot{robotId}` - location updates to mobile
  - `/app/update-location` - robot sends location to BE
- **Database**: PostgreSQL on Supabase (cloud)

## Development Notes

- Backend runs on port 8080 by default
- Robot connects to BE using IP configured in `server.launch` args or `config_ws.py` fallback
- Mobile app's base URL is configured in `Mobile/robot_delivery/lib/app/core/constants/app_config.dart`
- ESP32 communicates with ROS via UART at 57600 baud
- Robot is differential drive with 2 motors, PID speed control at 100Hz
