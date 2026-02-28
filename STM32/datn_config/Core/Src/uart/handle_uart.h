/*
 * handle_uart.h
 *
 *  Created on: Feb 28, 2026
 *      Author: LENOVO
 */

#ifndef SRC_UART_HANDLE_UART_H_
#define SRC_UART_HANDLE_UART_H_

#include "stm32f1xx_hal.h"
#include "message/error_message.h"

#include "FreeRTOS.h"
#include "task.h"

#include <stddef.h>
#include <stdint.h>

ErrorMessage uart_send_message(UART_HandleTypeDef *huart, const void *msg);

/**
 * @brief Nhận dữ liệu UART (Chế độ chờ - Polling)
 * @param huart: Pointer trỏ đến UART handle
 * @param buffer: Nơi lưu dữ liệu nhận được
 * @param size: Số lượng byte muốn nhận
 */
HAL_StatusTypeDef uart_receive_message(UART_HandleTypeDef *huart, uint8_t *buffer, uint16_t size);

/**
 * @brief Start listening UART RX in interrupt mode and store bytes into a ring buffer.
 *        Call once after UART is initialized.
 */
ErrorMessage uart_listen_start(UART_HandleTypeDef *huart);

/**
 * @brief Optional: set a task to be notified when RX activity happens.
 *        The task will be notified (give) on line-end ('\n' or '\r') and on overflow.
 */
void uart_listen_set_rx_task(TaskHandle_t task);

/**
 * @brief Read bytes from internal RX ring buffer (non-blocking).
 * @return number of bytes copied to dst.
 */
size_t uart_listen_read(uint8_t *dst, size_t len);

/**
 * @brief Get number of bytes currently buffered in RX ring.
 */
size_t uart_listen_available(void);

#endif /* SRC_UART_HANDLE_UART_H_ */
