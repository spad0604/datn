#ifndef __LED_SIGNAL_H
#define _LED_SIGNAL_H

#define LEFT_LED_SIGNAL B11
#define RIGHT_LED_SIGNAL B10
#define LED_BLINK_TIME 500

/**
 * @brief Bật tín hiệu đèn LED bên phải
 */
void led_signal_left_on();

/**
 * @brief Tắt tín hiệu đèn LED bên phải
 */
void led_signal_left_off();

/**
 * @brief Bật tín hiệu đèn LED bên trái
 */
void led_signal_right_on();

/**
 * @brief Tắt tín hiệu đèn LED bên trái
 */
void led_signal_right_off();

/**
 * @brief Nhấp nháy tín hiệu cả 2 đèn LED
 */
void led_signal_blink();

/**
 * @brief Tắt tất cả tín hiệu đèn LED
 */
void led_signal_all_off();

#endif