# datn (CubeMX/HAL) + FreeRTOS base

Mục tiêu: thêm “base FreeRTOS” vào project CubeMX/HAL mà **không sửa `datn.ioc`** (giữ nguyên config chân của bạn).

## 1) Bạn cần copy FreeRTOS kernel vào đâu?

Project đã có sẵn thư mục placeholder:
- `Middlewares/Third_Party/FreeRTOS/Source/`

Bạn tự copy FreeRTOS-Kernel vào đây (không commit vào git nếu bạn dùng `.gitignore`).

Tối thiểu cần các file:
- `Source/tasks.c`
- `Source/queue.c`
- `Source/list.c`
- `Source/portable/GCC/ARM_CM3/port.c`
- `Source/portable/MemMang/heap_4.c` (hoặc heap khác)

Và include:
- `Source/include/*`

## 2) Tích hợp vào code

- `Core/Inc/FreeRTOSConfig.h`: cấu hình cho STM32F1 + HAL.
- `Core/Src/freertos_app.c`: tạo task mẫu `heartbeat_task`.
- `Core/Src/main.c`: sẽ được patch để gọi `freertos_app_init()` và `vTaskStartScheduler()` khi có FreeRTOS.
- `Core/Src/stm32f1xx_it.c`: sẽ được patch để gọi handler của FreeRTOS trong `SVC_Handler`, `PendSV_Handler`, `SysTick_Handler`.

## 3) Heartbeat GPIO (tuỳ chọn)

Nếu bạn muốn task mẫu nháy 1 chân để nhìn thấy:
- Trong CubeMX, đặt tên 1 chân output là `HEARTBEAT`
- CubeMX sẽ sinh macro `HEARTBEAT_GPIO_Port` và `HEARTBEAT_Pin` trong `main.h`
- Task sẽ tự toggle chân đó mỗi 500ms.

## 4) Lưu ý HAL SysTick

HAL mặc định dùng SysTick để tăng `uwTick` (HAL_IncTick).
Base này giữ nguyên `HAL_IncTick()` trong `SysTick_Handler` và (khi FreeRTOS có mặt) gọi thêm `xPortSysTickHandler()`.

Nếu bạn dùng `HAL_Delay()` trong task: nên tránh (block theo tick HAL), ưu tiên `vTaskDelay()`.

