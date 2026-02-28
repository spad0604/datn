#include "message/error_message.h"
#include "msg_queue.h"

#include "FreeRTOS.h"
#include "task.h"

#include "../keypad/handle_keypad.h"

static void task_keypad(void *params)
{
    msg_t rx;
    (void)params;

    for (;;)
    {
        if (msg_queue_receive(MSG_QUE_KEYPAD, &rx, portMAX_DELAY) == pdPASS)
        {
            // Process the received message
        }
    }
}

ErrorMessage init_task_keypad(void)
{
    if (xTaskCreate(task_keypad, "Keypad Task", 256, NULL, 2, NULL) != pdPASS)
    {
        return E_INIT_ERROR;
    }

    return E_SUCCESS;
}