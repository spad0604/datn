#ifndef __MOTOR_CONTROL_H
#define __MOTOR_CONTROL_H

#include "main.h"

extern TIM_HandleTypeDef htim3;

#define MOTOR_L_PWM1_CH TIM_CHANNEL_1 // PA6
#define MOTOR_L_PWM2_CH TIM_CHANNEL_3 // PB0
#define MOTOR_R_PWM1_CH TIM_CHANNEL_2 // PA7
#define MOTOR_R_PWM2_CH TIM_CHANNEL_4 // PB1

/**
 * @brief Khởi tạo mô tơ
 */
void motor_init();

/**
 * @brief Điều khiển tốc độ, chiều động cơ bên trái
 * @param[in] speeds Tốc độ truyền vào
 */
void motor_left_drive(int16_t speeds);

/**
 * @brief Điều khiển tốc độ, chiều động cơ phải
 * @param[in] speeds Tốc độ truyền vào
 */
void motor_right_drive(int16_t speeds);

/**
 * @brief Dừng 2 động cơ
 */
void motor_stop();

#endif
