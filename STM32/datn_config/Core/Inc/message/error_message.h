#ifndef MESSAGE_ERROR_MESSAGE_H
#define MESSAGE_ERROR_MESSAGE_H

typedef enum
{
    E_SUCCESS = 0,
    E_NOT_PROCESSED,
    E_FAILED,
    E_INIT_ERROR,
	E_UART_FAILED,
	E_MAX
} ErrorMessage;

#endif
