#include "message/error_message.h"
#include "msg_queue.h"

#include "FreeRTOS.h"
#include "task.h"

#include "../mpu/mpu_control.h"

static void task_mpu(void *params)
{
    msg_t rx;

    (void)params;

    for (;;)
    {
        if (msg_queue_receive(MSG_QUE_MPU, &rx, portMAX_DELAY) == pdPASS)
        {
            /* TODO: process message (rx.p_msg) */
        }
    }
}

ErrorMessage init_task_mpu()
{
    if (xTaskCreate(task_mpu, "MPU Task", 256, NULL, 2, NULL) != pdPASS)
    {
        return E_INIT_ERROR;
    }
    mpu_init();

    return E_SUCCESS;
}
