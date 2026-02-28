/* msg_queue.h - lightweight message queue API built on FreeRTOS queues */
#ifndef MSG_QUEUE_H
#define MSG_QUEUE_H

#include "stdint.h"
#include "stddef.h"
#include "FreeRTOS.h"
#include "queue.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Queue payload is a raw pointer.
 * Sender allocates/owns the object and receiver casts it back.
 */
typedef void * msg_t;

typedef enum {
    MSG_QUE_LED = 0,
    MSG_QUE_MOTOR,
    MSG_QUE_MPU,
    /* TX/commands sent to UART task */
    MSG_QUE_UART,
    /* RX lines received from UART task */
    MSG_QUE_UART_RX,
    MSG_QUE_KEYPAD,
    MSG_QUE_COUNT
} msg_queue_id_t;

/**
 * Initialize all message queues. Call before using send/receive.
 * queue_length: number of messages each queue can hold.
 */
void msg_queue_init(size_t queue_length);

/** Send a pointer to a specific queue. Returns pdTRUE on success. */
BaseType_t msg_queue_send(msg_queue_id_t dst, msg_t msg, TickType_t ticks_to_wait);

/** Send from ISR. Use xHigherPriorityTaskWoken if needed. */
BaseType_t msg_queue_send_from_isr(msg_queue_id_t dst, msg_t msg, BaseType_t *pxHigherPriorityTaskWoken);

/** Receive a pointer from a specific queue. Use 0 for non-blocking poll. */
BaseType_t msg_queue_receive(msg_queue_id_t src, msg_t *msg, TickType_t ticks_to_wait);

/** Get underlying queue handle (read-only). */
QueueHandle_t msg_queue_get_handle(msg_queue_id_t id);

#ifdef __cplusplus
}
#endif

#endif
