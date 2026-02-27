#include "msg_queue.h"

static QueueHandle_t s_msg_queues[MSG_QUE_COUNT] = { NULL };

static BaseType_t msg_queue_is_valid(msg_queue_id_t id)
{
	return (id >= 0) && (id < MSG_QUE_COUNT);
}

void msg_queue_init(size_t queue_length)
{
	size_t i;

	for (i = 0; i < MSG_QUE_COUNT; ++i)
	{
		if (s_msg_queues[i] == NULL)
		{
			 s_msg_queues[i] = xQueueCreate(queue_length, sizeof(void *));
		}
	}
}

BaseType_t msg_queue_send(msg_queue_id_t dst, msg_t msg, TickType_t ticks_to_wait)
{
	if (!msg_queue_is_valid(dst) || (s_msg_queues[dst] == NULL))
	{
		return pdFALSE;
	}

	return xQueueSend(s_msg_queues[dst], &msg, ticks_to_wait);
}

BaseType_t msg_queue_send_from_isr(msg_queue_id_t dst, msg_t msg, BaseType_t *pxHigherPriorityTaskWoken)
{
	if (!msg_queue_is_valid(dst) || (s_msg_queues[dst] == NULL))
	{
		return pdFALSE;
	}

	return xQueueSendFromISR(s_msg_queues[dst], &msg, pxHigherPriorityTaskWoken);
}

BaseType_t msg_queue_receive(msg_queue_id_t src, msg_t *msg, TickType_t ticks_to_wait)
{
	if (!msg_queue_is_valid(src) || (s_msg_queues[src] == NULL))
	{
		return pdFALSE;
	}

	return xQueueReceive(s_msg_queues[src], msg, ticks_to_wait);
}

QueueHandle_t msg_queue_get_handle(msg_queue_id_t id)
{
	if (!msg_queue_is_valid(id))
	{
		return NULL;
	}

	return s_msg_queues[id];
}


