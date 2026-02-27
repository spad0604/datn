#include "mpu_control.h"

uint8_t mpu_init()
{
    uint8_t check;
    uint8_t data;

    // Kiểm tra sự hiện diện của cảm biến (Who Am I)
    HAL_I2C_Mem_Read(&hi2c1, MPU6050_ADDR, WHO_AM_I_REG, 1, &check, 1, 1000);

    if (check == 104) { // 0x68
        // Đánh thức cảm biến (Power Management)
        data = 0;
        HAL_I2C_Mem_Write(&hi2c1, MPU6050_ADDR, PWR_MGMT_1_REG, 1, &data, 1, 1000);

        // Cấu hình Sample Rate 1kHz
        data = 0x07;
        HAL_I2C_Mem_Write(&hi2c1, MPU6050_ADDR, SMPLRT_DIV_REG, 1, &data, 1, 1000);

        // Cấu hình Accel (+/- 2g) và Gyro (250 deg/s)
        data = 0x00;
        HAL_I2C_Mem_Write(&hi2c1, MPU6050_ADDR, ACCEL_CONFIG_REG, 1, &data, 1, 1000);
        HAL_I2C_Mem_Write(&hi2c1, MPU6050_ADDR, GYRO_CONFIG_REG, 1, &data, 1, 1000);
        return 0; // OK
    }
    return 1; // Lỗi
}

void mpu_read_data(MPU6050_t *data)
{
    uint8_t Rec_Data[14];
    // Đọc 14 byte dữ liệu liên tục (Accel, Temp, Gyro)
    HAL_I2C_Mem_Read(&hi2c1, MPU6050_ADDR, ACCEL_XOUT_H_REG, 1, Rec_Data, 14, 1000);

    data->Accel_X_RAW = (int16_t)(Rec_Data[0] << 8 | Rec_Data[1]);
    data->Accel_Y_RAW = (int16_t)(Rec_Data[2] << 8 | Rec_Data[3]);
    data->Accel_Z_RAW = (int16_t)(Rec_Data[4] << 8 | Rec_Data[5]);

    // Chuyển đổi sang đơn vị g (chia cho 16384 cho dải +/- 2g)
    data->Ax = data->Accel_X_RAW / 16384.0;
    data->Ay = data->Accel_Y_RAW / 16384.0;
    data->Az = data->Accel_Z_RAW / 16384.0;
}
