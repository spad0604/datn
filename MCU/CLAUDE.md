# MCU - ESP32 Motor Controller

ESP32 firmware for differential drive motor control with PID speed regulation. Communicates with ROS (Raspberry Pi) via UART.

## Hardware Configuration

### Pin Assignments
| Function | Left Motor | Right Motor |
|----------|-----------|-------------|
| PWM      | GPIO 17   | GPIO 22     |
| Direction| GPIO 18   | GPIO 23     |
| Encoder A| GPIO 27   | GPIO 5      |
| Encoder B| GPIO 26   | GPIO 15     |

### Motor Specs
- 2 DC motors (differential drive)
- Encoder: 1798 pulses/revolution
- Wheel diameter: 9.5 cm
- Wheelbase (robot_length): 52.89 cm

## UART Protocol (57600 baud)

### ROS -> ESP32 (Commands)
| Format | Description | Example |
|--------|-------------|---------|
| `LEFT/RIGHT;` | Speed setpoint (pulses/10ms) | `15/15;` |
| `KP:KI#KD;` | PID parameter update | `15.15:1.05#1.0;` |

### ESP32 -> ROS (Feedback)
| Format | Description | Example |
|--------|-------------|---------|
| `LEFT/RIGHT;` | Encoder delta counts | `12/13;` |

Encoder data is published at 20 Hz (every 50ms). Speed commands are received and applied each control cycle.

## PID Control

### Algorithm (Incremental PID)
```
delta_u = Kp*(e - e_prev) + Ki*e + Kd*(e - 2*e_prev + e_prev_prev)
u += delta_u  // clamped to [-255, 255]
```

### Default Parameters
- Kp = 15.15
- Ki = 1.05
- Kd = 1.0

### Runtime Tuning
PID parameters can be updated at runtime via ROS topic `/pid_config` (Twist message):
- `linear.x` = Kp
- `linear.y` = Ki
- `linear.z` = Kd

The ROS node (`pubVelEncoderDiff.py`) sends the `KP:KI#KD;` command to ESP32 when PID config changes.

## Control Loop
- **Frequency**: 100 Hz (10ms cycle)
- **Speed filtering**: Low-pass EMA (alpha=0.7 previous + 0.3 current)
- **PWM range**: 0-255
- **Direction control**: Forward (PWM=255-speed, DIR=1), Reverse (PWM=speed, DIR=0)

## Source Files
```
MCU/ESP32/src/
├── src.ino              # Main firmware (setup, loop, PID, serial parsing)
├── config.h             # Pin definitions, PID defaults
└── digitalWriteFast.h   # Fast GPIO macros for encoder reading
```

## Building & Flashing
Use Arduino IDE or PlatformIO with ESP32 board support. Upload via USB serial.
