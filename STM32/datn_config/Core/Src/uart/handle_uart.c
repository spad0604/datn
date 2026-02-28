/*
 * handle_uart.c
 *
 *  Created on: Feb 28, 2026
 *      Author: LENOVO
 */

#include "handle_uart.h"

#include <string.h>

#ifndef UART_RX_RING_SIZE
#define UART_RX_RING_SIZE 512u
#endif

static UART_HandleTypeDef *s_listen_huart = NULL;
static TaskHandle_t s_rx_task = NULL;

static uint8_t s_rx_byte = 0;
static volatile uint16_t s_rx_head = 0;
static volatile uint16_t s_rx_tail = 0;
static uint8_t s_rx_ring[UART_RX_RING_SIZE];

static uint16_t ring_next(uint16_t idx)
{
	return (uint16_t)((idx + 1u) % (uint16_t)UART_RX_RING_SIZE);
}

static void ring_push_from_isr(uint8_t b)
{
	uint16_t next = ring_next(s_rx_head);
	if (next == s_rx_tail)
	{
		/* overflow: drop byte */
		return;
	}
	s_rx_ring[s_rx_head] = b;
	s_rx_head = next;
}

ErrorMessage uart_send_message(UART_HandleTypeDef *huart, const void *msg)
{
	if ((huart == NULL) || (msg == NULL))
	{
		return E_UART_FAILED;
	}

	/* Treat msg as a null-terminated string */
	if (HAL_UART_Transmit(huart, (uint8_t *)msg, (uint16_t)strlen((const char *)msg), 100) != HAL_OK)
	{
		return E_UART_FAILED;
	}

	return E_SUCCESS;
}

HAL_StatusTypeDef uart_receive_message(UART_HandleTypeDef *huart, uint8_t *buffer, uint16_t size)
{
	return HAL_UART_Receive(huart, buffer, size, 1000);
}

ErrorMessage uart_listen_start(UART_HandleTypeDef *huart)
{
	if (huart == NULL)
	{
		return E_UART_FAILED;
	}

	s_listen_huart = huart;
	s_rx_head = 0;
	s_rx_tail = 0;

	if (HAL_UART_Receive_IT(huart, &s_rx_byte, 1) != HAL_OK)
	{
		return E_UART_FAILED;
	}

	return E_SUCCESS;
}

void uart_listen_set_rx_task(TaskHandle_t task)
{
	s_rx_task = task;
}

size_t uart_listen_available(void)
{
	uint16_t head = s_rx_head;
	uint16_t tail = s_rx_tail;
	if (head >= tail)
	{
		return (size_t)(head - tail);
	}
	return (size_t)((uint16_t)UART_RX_RING_SIZE - (tail - head));
}

size_t uart_listen_read(uint8_t *dst, size_t len)
{
	size_t count = 0;
	if ((dst == NULL) || (len == 0u))
	{
		return 0u;
	}

	while ((count < len) && (s_rx_tail != s_rx_head))
	{
		dst[count++] = s_rx_ring[s_rx_tail];
		s_rx_tail = ring_next(s_rx_tail);
	}

	return count;
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
	BaseType_t higherPriorityTaskWoken = pdFALSE;
	uint8_t byte;

	if ((s_listen_huart == NULL) || (huart != s_listen_huart))
	{
		return;
	}

	byte = s_rx_byte;
	ring_push_from_isr(byte);

	/* Notify only on end-of-line to reduce wakeups */
	if ((s_rx_task != NULL) && ((byte == '\n') || (byte == '\r')))
	{
		vTaskNotifyGiveFromISR(s_rx_task, &higherPriorityTaskWoken);
		portYIELD_FROM_ISR(higherPriorityTaskWoken);
	}

	(void)HAL_UART_Receive_IT(huart, &s_rx_byte, 1);
}

void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart)
{
	if ((s_listen_huart == NULL) || (huart != s_listen_huart))
	{
		return;
	}

	/* Try to recover RX after error */
	(void)HAL_UART_AbortReceive_IT(huart);
	(void)HAL_UART_Receive_IT(huart, &s_rx_byte, 1);
}
