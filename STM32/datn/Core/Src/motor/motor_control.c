#include "motor_control.h"

void motor_init(void) {
    HAL_TIM_PWM_Start(&htim3, MOTOR_L_PWM1_CH);
    HAL_TIM_PWM_Start(&htim3, MOTOR_L_PWM2_CH);
    HAL_TIM_PWM_Start(&htim3, MOTOR_R_PWM1_CH);
    HAL_TIM_PWM_Start(&htim3, MOTOR_R_PWM2_CH);
}

void motor_left_drive(int16_t speeds)
{
	if(speeds > 0)
	{
		__HAL_TIM_SET_COMPARE(&htim3, MOTOR_L_PWM1_CH, speeds);
		__HAL_TIM_SET_COMPARE(&htim3, MOTOR_R_PWM1_CH, 0);
	}
	else
	{
		__HAL_TIM_SET_COMPARE(&htim3, MOTOR_L_PWM1_CH, 0);
		__HAL_TIM_SET_COMAPRE(&htim3, MOTOR_R_PWM1_CH, -speeds);
	}
}

void motor_right_drive(int16_t speeds)
{
	if(speeds > 0)
	{
		__HAL_TIM_SET_COMPARE(&htim3, MOTOR_L_PWM2_CH, speeds);
		__HAL_TIM_SET_COMPARE(&htim3, MOTOR_R_PWM2_CH, 0);
	}
	else
	{
		__HAL_TIM_SET_COMPARE(&htim3, MOTOR_L_PWM2_CH, 0);
		__HAL_TIM_SET_COMAPRE(&htim3, MOTOR_R_PWM2_CH, -speeds);
	}
}

void motor_stop(int16_t speeds)
{
    motor_left_drive(0);
    motor_right_drive(0);
}