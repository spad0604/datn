#include "message/error_message.h"
#include "msg_queue.h"

#include "FreeRTOS.h"
#include "task.h"

#include "../mpu/mpu_control.h"

#include <stdio.h>
#include <string.h>

#ifndef MPU_SAMPLE_PERIOD_MS
#define MPU_SAMPLE_PERIOD_MS 100u
#endif

#ifndef MPU_LINE_MAX
#define MPU_LINE_MAX 160u
#endif

static void uart_send_line(const char *line)
{
    size_t len;
    char *copy;

    if (line == NULL)
    {
        return;
    }

    len = strlen(line);
    copy = (char *)pvPortMalloc(len + 1u);
    if (copy == NULL)
    {
        return;
    }

    memcpy(copy, line, len + 1u);
    if (msg_queue_send(MSG_QUE_UART, (msg_t)copy, 0) != pdPASS)
    {
        vPortFree(copy);
    }
}

static void task_mpu(void *params)
{
    MPU6050_t data;
    char out[MPU_LINE_MAX];

    (void)params;

    for (;;)
    {
        memset(&data, 0, sizeof(data));
        mpu_read_data(&data);

        (void)snprintf(
            out,
            sizeof(out),
            "RD1;EVT;MPU;AXR=%d;AYR=%d;AZR=%d;GXR=%d;GYR=%d;GZR=%d;T=%d\\n",
            (int)data.Accel_X_RAW,
            (int)data.Accel_Y_RAW,
            (int)data.Accel_Z_RAW,
            (int)data.Gyro_X_RAW,
            (int)data.Gyro_Y_RAW,
            (int)data.Gyro_Z_RAW,
            (int)(data.Temperature * 100.0f)
        );

        uart_send_line(out);
        vTaskDelay(pdMS_TO_TICKS(MPU_SAMPLE_PERIOD_MS));
    }
}

ErrorMessage init_task_mpu()
{
    if (mpu_init() != 0u)
    {
        return E_INIT_ERROR;
    }

    if (xTaskCreate(task_mpu, "MPU Task", 256, NULL, 2, NULL) != pdPASS)
    {
        return E_INIT_ERROR;
    }

    return E_SUCCESS;
}
