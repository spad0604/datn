#include "message/error_message.h"
#include "msg_queue.h"

#include "FreeRTOS.h"
#include "task.h"

#include "../motor/motor_control.h"

static void task_motor(void *params)
{
    msg_t rx;
    (void)params;

    for (;;)
    {
        if (msg_queue_receive(MSG_QUE_MOTOR, &rx, portMAX_DELAY) == pdPASS)
        {
            /* TODO: handle motor messages (rx.p_msg) */
        }
    }
}

ErrorMessage init_task_motor()
{
    if (xTaskCreate(task_motor, "MOTOR Task", 256, NULL, 2, NULL) != pdPASS)
    {
        return E_INIT_ERROR;
    }

    motor_init();

    return E_SUCCESS;
}
