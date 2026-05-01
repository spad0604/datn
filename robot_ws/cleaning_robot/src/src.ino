#include <Arduino.h>
#include "soc/gpio_struct.h"

// Đưa typedef lên đầu để tránh lỗi biên dịch của Arduino IDE
typedef void (*CallbackFunction)();
void callFunctionPeriodically(CallbackFunction functionToCall, unsigned long intervalTime, unsigned long &previousMillis);

// ================= CẤU HÌNH CƠ BẢN =================
#define NMOTORS 2
#define M_L 0 // Động cơ Trái
#define M_R 1 // Động cơ Phải

#define LOOP_PUB 50     // Tần số gửi Odom (ms)
#define ros_serial 1    // Bật giao tiếp ROS qua UART

const float LOOP_FREQUENCY = 100.0; // Tần số vòng lặp PID (100 Hz)
const float delta_time = 1.0 / LOOP_FREQUENCY; // 0.01s
const float LOOP_MS = 1000.0 * delta_time; // 10ms

// ================= CẤU HÌNH CHÂN (PINS) =================
const int enca[NMOTORS] = {27, 5};
const int encb[NMOTORS] = {26, 15}; 
const int pwm[NMOTORS]  = {17, 22};  
const int dir[NMOTORS]  = {18, 23};

// ĐÃ SỬA: Đảo dấu bánh Phải từ -1 thành 1 để cùng tiến lên phía trước
const int dir_encod[NMOTORS] = {1, 1}; 
const int dir_motor[NMOTORS] = {1, 1};

// ================= BIẾN TOÀN CỤC =================
volatile float speed_desired[NMOTORS] = {0.0, 0.0}; // Đơn vị: Xung/10ms
volatile int encoder_count[NMOTORS]   = {0, 0};
long publish_encoder[NMOTORS]         = {0, 0};
float speed_filtered[NMOTORS]         = {0.0, 0.0}; // Lưu giá trị sau lọc

// Trả lại bộ thông số PID gốc của bạn
float p_gain_default = 15.15; 
float i_gain_default = 1.05;
float d_gain_default = 1.0;

// Spinlock bảo vệ ngắt (Tránh Race Condition)
portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;

// Macro đọc thanh ghi GPIO siêu tốc (~0.1µs) thay cho digitalRead (~1.5µs)
#define FAST_READ(pin) ((pin < 32) ? ((GPIO.in >> pin) & 1) : ((GPIO.in1.val >> (pin - 32)) & 1))

// ================= LỚP ĐIỀU KHIỂN PID (Dạng Vận Tốc - Incremental) =================
class SimplePID {
private:
  float kp, kd, ki, umax;
  float u, last_e_2, last_e;
public:
  SimplePID() : kp(1), kd(0), ki(0), umax(255), last_e(0.0), last_e_2(0.0), u(0) {}
  
  void reset_all() {
    last_e_2 = 0;
    last_e = 0;
    u = 0;
  }
  
  void setParams(float kpIn, float kiIn, float kdIn, float umaxIn) {
    kp = kpIn;
    ki = kiIn;
    kd = kdIn;
    umax = umaxIn;
    reset_all();
  }
  
  float compute(float value, float target) {
    if (target == 0) {
      reset_all(); // Cắt PID khi yều cầu dừng hẳn để tránh trôi
      return 0;
    }
    float e = target - value;
    // Phương trình Incremental PID
    float delta_u = kp * (e - last_e) + ki * e + kd * (e - 2 * last_e + last_e_2);
    
    u += delta_u;
    
    // Output Clamp
    if (u > umax) u = umax;
    else if (u < -umax) u = -umax;
    
    last_e_2 = last_e;
    last_e = e;
    return u;
  }
};

SimplePID pid[NMOTORS];

// ================= HÀM ĐIỀU KHIỂN PHẦN CỨNG =================
void control_motor(int motor, int speed) {
  speed = speed * dir_motor[motor]; 
  bool direct = speed > 0 ? 1 : 0;
  speed = constrain(speed, -255, 255);

  if (speed == 0) {
    analogWrite(pwm[motor], 0);
    digitalWrite(dir[motor], 0);
    return;
  }
  
  if (direct) {
    analogWrite(pwm[motor], 255 - abs(speed));
    digitalWrite(dir[motor], 1);
  } else {
    analogWrite(pwm[motor], abs(speed));
    digitalWrite(dir[motor], 0);
  }
}

// ================= NGẮT (INTERRUPTS) ENCODER SIÊU TỐC =================
void IRAM_ATTR encoderLeftMotor() {
  static bool old_a = false;
  bool newA = FAST_READ(enca[M_L]);
  bool newB = FAST_READ(encb[M_L]);
  
  int delta = (newA && !old_a) ? (newB ? dir_encod[M_L] : -dir_encod[M_L]) 
                               : (newB ? -dir_encod[M_L] : dir_encod[M_L]);
  
  portENTER_CRITICAL_ISR(&mux);
  encoder_count[M_L] -= delta;
  portEXIT_CRITICAL_ISR(&mux);
  old_a = newA;
}

void IRAM_ATTR encoderRightMotor() {
  static bool old_a = false;
  bool newA = FAST_READ(enca[M_R]);
  bool newB = FAST_READ(encb[M_R]);
  
  int delta = (newA && !old_a) ? (newB ? dir_encod[M_R] : -dir_encod[M_R]) 
                               : (newB ? -dir_encod[M_R] : dir_encod[M_R]);
  
  portENTER_CRITICAL_ISR(&mux);
  encoder_count[M_R] -= delta;
  portEXIT_CRITICAL_ISR(&mux);
  old_a = newA;
}

// ================= GIAO TIẾP VÀ XỬ LÝ (UART) =================
bool receive_uart() {
  if (Serial.available()) {
    String c = Serial.readStringUntil(';');
    int index_now = c.indexOf("/");
    int index_kp_desired = c.indexOf(":");
    
    // Nhận Vận Tốc: Trái/Phải; (Gửi từ Pi xuống bằng đơn vị Xung/10ms)
    if (index_now != -1) {
      portENTER_CRITICAL(&mux); 
      speed_desired[M_L] = c.substring(0, index_now).toFloat();
      speed_desired[M_R] = c.substring(index_now + 1).toFloat();
      portEXIT_CRITICAL(&mux);
      return 1;
    } 
    // Nhận PID: P:I#D;
    else if (index_kp_desired != -1) {
      int index_cal = c.indexOf("#");
      if (index_cal != -1) {
        float new_kp = c.substring(0, index_kp_desired).toFloat();
        float new_ki = c.substring(index_kp_desired + 1, index_cal).toFloat();
        float new_kd = c.substring(index_cal + 1).toFloat();

        for(int i = 0; i < NMOTORS; i++) {
          pid[i].setParams(new_kp, new_ki, new_kd, 255);
        }
      }
      return 1;
    }
  }
  return 0;
}

void send_odom() {
  Serial.print(publish_encoder[M_L]);
  Serial.print("/");
  Serial.print(publish_encoder[M_R]);
  Serial.println(";");
}

void control_speed() {
  int delta_encoder[NMOTORS] = {0, 0};
  float target_speed_local[NMOTORS] = {0.0, 0.0};
  
  portENTER_CRITICAL(&mux);
  for (int i = 0; i < NMOTORS; i++) {
    delta_encoder[i] = encoder_count[i];
    encoder_count[i] = 0;
    target_speed_local[i] = speed_desired[i];
  }
  portEXIT_CRITICAL(&mux);

  int m_pwm[NMOTORS] = {0, 0};

  for (int i = 0; i < NMOTORS; i++) {
    publish_encoder[i] += delta_encoder[i];
    
    // Vận tốc tính trực tiếp bằng số xung/chu kỳ để khớp với lệnh từ Pi
    float current_speed = (float)delta_encoder[i]; 
    
    // Bộ lọc Low-Pass (EMA) giảm nhiễu 
    speed_filtered[i] = 0.7 * speed_filtered[i] + 0.3 * current_speed;

    // Đưa vào PID
    m_pwm[i] = pid[i].compute(speed_filtered[i], target_speed_local[i]);
    
    if (ros_serial) {
      control_motor(i, m_pwm[i]);
    }
  }
}

// Hàm Scheduler đơn giản
void callFunctionPeriodically(CallbackFunction functionToCall, unsigned long intervalTime, unsigned long &previousMillis) {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= intervalTime) {
    functionToCall();
    previousMillis = currentMillis;
  }
}

// ================= HÀM MAIN =================
void setup() {
  Serial.begin(57600);
  
  for (int k = 0; k < NMOTORS; k++) {
    pinMode(enca[k], INPUT_PULLUP);
    pinMode(encb[k], INPUT_PULLUP);
    pinMode(pwm[k], OUTPUT);
    pinMode(dir[k], OUTPUT);
    pid[k].setParams(p_gain_default, i_gain_default, d_gain_default, 255);
    control_motor(k, 0);
  }

  attachInterrupt(digitalPinToInterrupt(enca[M_L]), encoderLeftMotor, CHANGE);
  attachInterrupt(digitalPinToInterrupt(enca[M_R]), encoderRightMotor, CHANGE);
}

void loop() {
  static unsigned long time_loop_pid = millis();
  static unsigned long time_publish = millis();

  if (ros_serial) {
    receive_uart();
  }

  callFunctionPeriodically(control_speed, LOOP_MS, time_loop_pid); // Chạy PID (100Hz)
  callFunctionPeriodically(send_odom, LOOP_PUB, time_publish);     // Gửi Odometry (20Hz)
}