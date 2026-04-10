#include "mpu_control.h"

#include <string.h>

uint8_t mpu_init()
{
    uint8_t check;
    uint8_t data;

    // Kiểm tra sự hiện diện của cảm biến (Who Am I)
    if (HAL_I2C_Mem_Read(&hi2c1, MPU6050_ADDR, WHO_AM_I_REG, 1, &check, 1, 1000) != HAL_OK)
    {
        return 1;
    }

    if (check == 104) { // 0x68
        // Đánh thức cảm biến (Power Management)
        data = 0;
        if (HAL_I2C_Mem_Write(&hi2c1, MPU6050_ADDR, PWR_MGMT_1_REG, 1, &data, 1, 1000) != HAL_OK)
        {
            return 1;
        }

        // Cấu hình Sample Rate 1kHz
        data = 0x07;
        if (HAL_I2C_Mem_Write(&hi2c1, MPU6050_ADDR, SMPLRT_DIV_REG, 1, &data, 1, 1000) != HAL_OK)
        {
            return 1;
        }

        // Cấu hình Accel (+/- 2g) và Gyro (250 deg/s)
        data = 0x00;
        if (HAL_I2C_Mem_Write(&hi2c1, MPU6050_ADDR, ACCEL_CONFIG_REG, 1, &data, 1, 1000) != HAL_OK)
        {
            return 1;
        }
        if (HAL_I2C_Mem_Write(&hi2c1, MPU6050_ADDR, GYRO_CONFIG_REG, 1, &data, 1, 1000) != HAL_OK)
        {
            return 1;
        }
        return 0; // OK
    }
    return 1; // Lỗi
}

void mpu_read_data(MPU6050_t *data)
{
    uint8_t Rec_Data[14];

    if (data == NULL)
    {
        return;
    }

    // Đọc 14 byte dữ liệu liên tục (Accel, Temp, Gyro)
    if (HAL_I2C_Mem_Read(&hi2c1, MPU6050_ADDR, ACCEL_XOUT_H_REG, 1, Rec_Data, 14, 1000) != HAL_OK)
    {
        memset(data, 0, sizeof(*data));
        return;
    }

    data->Accel_X_RAW = (int16_t)(Rec_Data[0] << 8 | Rec_Data[1]);
    data->Accel_Y_RAW = (int16_t)(Rec_Data[2] << 8 | Rec_Data[3]);
    data->Accel_Z_RAW = (int16_t)(Rec_Data[4] << 8 | Rec_Data[5]);

    data->Temperature = ((int16_t)(Rec_Data[6] << 8 | Rec_Data[7])) / 340.0f + 36.53f;

    data->Gyro_X_RAW = (int16_t)(Rec_Data[8] << 8 | Rec_Data[9]);
    data->Gyro_Y_RAW = (int16_t)(Rec_Data[10] << 8 | Rec_Data[11]);
    data->Gyro_Z_RAW = (int16_t)(Rec_Data[12] << 8 | Rec_Data[13]);

    // Chuyển đổi sang đơn vị g (chia cho 16384 cho dải +/- 2g)
    data->Ax = data->Accel_X_RAW / 16384.0;
    data->Ay = data->Accel_Y_RAW / 16384.0;
    data->Az = data->Accel_Z_RAW / 16384.0;

    data->Gx = data->Gyro_X_RAW / 131.0;
    data->Gyce = data->Gyro_Y_RAW / 131.0;
    data->Gz = data->Gyro_Z_RAW / 131.0;
}
