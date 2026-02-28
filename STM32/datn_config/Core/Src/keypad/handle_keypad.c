#include "handle_keypad.h"

char keys[4][4] = {
    {'1', '2', '3', 'A'},
    {'4', '5', '6', 'B'},
    {'7', '8', '9', 'C'},
    {'*', '0', '#', 'D'}};

uint8_t pin_index = 0;

char correct_pin[4] = {'0', '0', '0', '0'}; // Mã PIN mặc định, có thể thay đổi theo nhu cầu

char input_pin[4] = {0}; // Mảng để lưu 4 số PIN nhập vào

uint16_t col_pins[4] = {GPIO_PIN_8, GPIO_PIN_9, GPIO_PIN_12, GPIO_PIN_15};

char keypad_read(void)
{
    for (int i = 0; i < 4; i++)
    {
        // 1. Quét hàng i: Kéo tất cả hàng HIGH, chỉ hàng i xuống LOW
        HAL_GPIO_WritePin(ROW_PORT, GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14 | GPIO_PIN_15, GPIO_PIN_SET);

        HAL_GPIO_WritePin(ROW_PORT, (GPIO_PIN_12 << i), GPIO_PIN_RESET);

        // 2. Duyệt qua 4 cột để kiểm tra xem có phím nào ở hàng i bị nhấn không
        for (int j = 0; j < 4; j++)
        {
            if (HAL_GPIO_ReadPin(COL_PORT, col_pins[j]) == GPIO_PIN_RESET)
            {
                // Phát hiện nhấn phím! -> Chống dội (Debounce)
                HAL_Delay(20);

                // Kiểm tra lại lần nữa xem có thực sự nhấn không
                if (HAL_GPIO_ReadPin(COL_PORT, col_pins[j]) == GPIO_PIN_RESET)
                {
                    char key_pressed = keys[i][j];

                    while (HAL_GPIO_ReadPin(COL_PORT, col_pins[j]) == GPIO_PIN_RESET)
                        ;

                    // Trả về phím duy nhất
                    return key_pressed;
                }
            }
        }
    }
    return 0; // Không có phím nào được nhấn
}

char keypad_open_pin_listen(void)
{
    if (keypad_read() != 0)
    {
        char key = keypad_read();

        if (key >= '0' && key <= '9')
        {
            input_pin[pin_index] = key;
            pin_index = (pin_index + 1) % 4; // Di chuyển đến vị trí tiếp theo, quay lại đầu nếu vượt quá 4

            // Kiểm tra nếu đã nhập đủ 4 số
            if (pin_index == 0)
            {
                // So sánh với mã PIN đã định nghĩa
                if (input_pin[0] == correct_pin[0] && input_pin[1] == correct_pin[1] && input_pin[2] == correct_pin[2] && input_pin[3] == correct_pin[3])
                {
                    return 'O'; // Mở khóa thành công
                }
                else
                {
                    return 'X'; // Mã PIN sai
                }
            }
        }
    }
}