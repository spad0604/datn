#ifndef __LED_SIGNAL_H
#define _LED_SIGNAL_H

#define LED_SIGNAL_PORT GPIOA
#define LEFT_LED_SIGNAL GPIO_PIN_11
#define RIGHT_LED_SIGNAL GPIO_PIN_10

#define LOCK_12V_PORT GPIOA
#define LOCK_12_PIN GPIO_PIN_1

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

/**
 * @brief Bật khoá
 */
void lock_12v_on();

/**
 * @brief Tắt khoá
 */
void lock_12v_off();

#endif