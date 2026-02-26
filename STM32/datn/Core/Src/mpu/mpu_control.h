#ifndef __MPU_CONTROL_H
#define __MPU_CONTROL_H

#include "main.h"

extern I2C_HandleTypeDef hi2c1;

#define MPU6050_ADDR         0xD0
#define SMPLRT_DIV_REG       0x19
#define GYRO_CONFIG_REG      0x1B
#define ACCEL_CONFIG_REG     0x1C
#define ACCEL_XOUT_H_REG     0x3B
#define TEMP_OUT_H_REG       0x41
#define GYRO_XOUT_H_REG      0x43
#define PWR_MGMT_1_REG       0x6B
#define WHO_AM_I_REG         0x75

typedef struct {
    int16_t Accel_X_RAW;
    int16_t Accel_Y_RAW;
    int16_t Accel_Z_RAW;
    double Ax;
    double Ay;
    double Az;

    int16_t Gyro_X_RAW;
    int16_t Gyro_Y_RAW;
    int16_t Gyro_Z_RAW;
    double Gx;
    double Gyce;
    double Gz;

    float Temperature;
} MPU6050_t;

/**
 * @brief Khởi tạo MPU
 */
uint8_t mpu_init();

/**
 * @brief Đọc toàn bộ dữ liệu MPU
 * @param[out] Dữ liệu đọc ra
 */
void mpu_read_data(MPU6050_t *data);
#endif