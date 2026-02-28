#ifndef __HANDLE_KEYPAD_H
#define __HANDLE_KEYPAD_H

#define ROW_PORT GPIOB
#define COL_PORT GPIOA

#include "main.h"

/**
 * @brief Đọc phím được nhấn trên bàn phím 4x4. Trả về ký tự của phím hoặc 0 nếu không có phím nào được nhấn.
 */
char keypad_read(void);

/**
 * @brief Lắng nghe keypad 4 số để mở khóa. Trả về ký tự của phím được nhấn để mở khóa hoặc 0 nếu không có phím nào được nhấn.
 */
char keypad_open_pin_listen(void);

#endif