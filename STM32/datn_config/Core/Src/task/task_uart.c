/*
 * task_uart.c
 *
 *  Created on: Feb 28, 2026
 *      Author: LENOVO
 */

#include "message/error_message.h"
#include "msg_queue.h"
#include "FreeRTOS.h"
#include "task.h"

#include "../uart/handle_uart.h"

#include <string.h>

extern UART_HandleTypeDef huart2;

#ifndef UART_LINE_MAX
#define UART_LINE_MAX 128u
#endif

static void uart_forward_line(const char *line, size_t len)
{
    char *copy;

    if ((line == NULL) || (len == 0u))
    {
        return;
    }

    copy = (char *)pvPortMalloc(len + 1u);
    if (copy == NULL)
    {
        return;
    }

    memcpy(copy, line, len);
    copy[len] = '\0';

    if (msg_queue_send(MSG_QUE_UART_RX, (msg_t)copy, 0) != pdPASS)
    {
        vPortFree(copy);
    }
}

static void task_uart(void *params)
{
    msg_t tx;
    char line[UART_LINE_MAX];
    size_t idx = 0;
    TickType_t lastByteTick = 0;
    uint8_t b;

    (void)params;

    uart_listen_set_rx_task(xTaskGetCurrentTaskHandle());
    (void)uart_listen_start(&huart2);
    lastByteTick = xTaskGetTickCount();

    for (;;)
    {
        /* 1) TX: handle outbound messages (null-terminated strings) */
        if (msg_queue_receive(MSG_QUE_UART, &tx, 0) == pdPASS)
        {
            if (tx != NULL)
            {
                (void)uart_send_message(&huart2, tx);
                vPortFree(tx);
            }
        }

        /* 2) RX: wait for end-of-line notify or timeout */
        (void)ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(50));

        /* Drain all buffered bytes */
        while (uart_listen_read(&b, 1u) == 1u)
        {
            lastByteTick = xTaskGetTickCount();

            if ((b == '\n') || (b == '\r'))
            {
                if (idx > 0u)
                {
                    uart_forward_line(line, idx);
                    idx = 0u;
                }
                continue;
            }

            if (idx < (UART_LINE_MAX - 1u))
            {
                line[idx++] = (char)b;
            }
            else
            {
                /* overflow: forward what we have and reset */
                uart_forward_line(line, idx);
                idx = 0u;
            }
        }

        /* Inter-character timeout => treat as a complete message */
        if ((idx > 0u) && ((xTaskGetTickCount() - lastByteTick) >= pdMS_TO_TICKS(100)))
        {
            uart_forward_line(line, idx);
            idx = 0u;
        }
    }
}

ErrorMessage init_task_uart()
{
    if (xTaskCreate(task_uart, "task_uart", 256, NULL, 1, NULL) != pdPASS)
    {
        return E_INIT_ERROR;
    }
    return E_SUCCESS;
}
