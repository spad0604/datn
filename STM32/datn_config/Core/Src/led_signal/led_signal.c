#include "led_signal.h"
#include "stm32f1xx_hal.h"

void led_signal_init(void)
{
	/* Giữ mặc định: tắt tất cả khi khởi tạo. Cấu hình chân GPIO nên được thực hiện
	   trong MX_GPIO_Init() (CubeMX) hoặc nơi khởi tạo phần cứng khác. */
	led_signal_all_off();
}

void led_signal_left_on(void)
{
	HAL_GPIO_WritePin(LED_SIGNAL_PORT, LEFT_LED_SIGNAL, GPIO_PIN_SET);

    HAL_Delay(LED_BLINK_TIME); // Giữ tín hiệu trong khoảng thời gian định nghĩa

    HAL_GPIO_WritePin(LED_SIGNAL_PORT, LEFT_LED_SIGNAL, GPIO_PIN_RESET);
}

void led_signal_left_off(void)
{
	HAL_GPIO_WritePin(LED_SIGNAL_PORT, LEFT_LED_SIGNAL, GPIO_PIN_RESET);
}

void led_signal_right_on(void)
{
	HAL_GPIO_WritePin(LED_SIGNAL_PORT, RIGHT_LED_SIGNAL, GPIO_PIN_SET);

    HAL_Delay(LED_BLINK_TIME); // Giữ tín hiệu trong khoảng thời gian định nghĩa

    HAL_GPIO_WritePin(LED_SIGNAL_PORT, RIGHT_LED_SIGNAL, GPIO_PIN_RESET);
}

void led_signal_right_off(void)
{
	HAL_GPIO_WritePin(LED_SIGNAL_PORT, RIGHT_LED_SIGNAL, GPIO_PIN_RESET);
}

void led_signal_blink(void)
{
	/* Nhấp nháy đồng thời cả 2 xi nhan: bật -> chờ -> tắt */
	HAL_GPIO_TogglePin(LED_SIGNAL_PORT, LEFT_LED_SIGNAL | RIGHT_LED_SIGNAL);
	HAL_Delay(LED_BLINK_TIME);
	HAL_GPIO_TogglePin(LED_SIGNAL_PORT, LEFT_LED_SIGNAL | RIGHT_LED_SIGNAL);
}

void led_signal_all_off(void)
{
	HAL_GPIO_WritePin(LED_SIGNAL_PORT, LEFT_LED_SIGNAL | RIGHT_LED_SIGNAL, GPIO_PIN_RESET);
}

void lock_12v_on(void)
{
	HAL_GPIO_WritePin(LOCK_12V_PORT, LOCK_12_PIN, GPIO_PIN_SET);
}

void lock_12v_off(void)
{
	HAL_GPIO_WritePin(LOCK_12V_PORT, LOCK_12_PIN, GPIO_PIN_RESET);
}

