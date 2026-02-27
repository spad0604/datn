#include "message/error_message.h"
#include "msg_queue.h"

#include "FreeRTOS.h"
#include "task.h"

#include "../led_signal/led_signal.h"

static void task_led_signal(void *params)
{
    msg_t rx;
    (void)params;

    for (;;)
    {
        if (msg_queue_receive(MSG_QUE_LED, &rx, portMAX_DELAY) == pdPASS)
        {
            /* TODO: handle LED messages (rx.p_msg) */
        }
    }
}

ErrorMessage init_task_led_signal()
{
    if (xTaskCreate(task_led_signal, "LED Task", 256, NULL, 2, NULL) != pdPASS)
    {
        return E_INIT_ERROR;
    }

    /* set initial LED state */
    // led_signal_all_off();

    return E_SUCCESS;
}
