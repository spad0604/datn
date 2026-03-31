/* task_cmd.h - UART command router for Pi<->MCU protocol */
#ifndef INC_TASK_TASK_CMD_H_
#define INC_TASK_TASK_CMD_H_

#include "message/error_message.h"

#ifdef __cplusplus
extern "C" {
#endif

ErrorMessage init_task_cmd(void);

#ifdef __cplusplus
}
#endif

#endif /* INC_TASK_TASK_CMD_H_ */
