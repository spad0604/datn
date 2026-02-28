#ifndef __LED_SIGNAL_H
#define __LED_SIGNAL_H

#define LED_SIGNAL_PORT GPIOA
#define LEFT_LED_SIGNAL GPIO_PIN_11
#define RIGHT_LED_SIGNAL GPIO_PIN_10

#define LOCK_12V_PORT GPIOA
#define LOCK_12_PIN GPIO_PIN_1

#define LED_BLINK_TIME 500

/**
 * @brief Bật tín hiệu đèn xi nhan bên trái
 */
void led_signal_left_on(void);

/**
 * @brief Tắt tín hiệu đèn xi nhan bên trái
 */
void led_signal_left_off(void);

/**
 * @brief Bật tín hiệu đèn xi nhan bên phải
 */
void led_signal_right_on(void);

/**
 * @brief Tắt tín hiệu đèn xi nhan bên phải
 */
void led_signal_right_off(void);

/**
 * @brief Nhấp nháy tín hiệu xi nhan cả hai bên (một lần)
 */
void led_signal_blink(void);

/**
 * @brief Tắt tất cả tín hiệu xi nhan
 */
void led_signal_all_off(void);

/**
 * @brief Bật khóa 12V
 */
void lock_12v_on(void);

/**
 * @brief Tắt khóa 12V
 */
void lock_12v_off(void);

/**
 * @brief Khởi tạo trạng thái đèn xi nhan (gọi một lần tại khởi động)
 */
void led_signal_init(void);

#endif