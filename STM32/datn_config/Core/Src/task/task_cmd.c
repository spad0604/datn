/* task_cmd.c - UART command router for Pi<->MCU protocol */

#include "message/error_message.h"
#include "msg_queue.h"

#include "FreeRTOS.h"
#include "task.h"

#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include "main.h"

#include "../motor/motor_control.h"
#include "../mpu/mpu_control.h"

/* Protocol: RD1;CMD;NAME;K=V;... (line delimited by \n) */

#ifndef CMD_TX_MAX
#define CMD_TX_MAX 192u
#endif

#define SIGNAL_RELAY_PORT GPIOB
#define SIGNAL_LEFT_RELAY GPIO_PIN_12
#define SIGNAL_RIGHT_RELAY GPIO_PIN_13
#define SIGNAL_HAZARD_RELAY GPIO_PIN_14
#define SIGNAL_RELAY_ALL (SIGNAL_LEFT_RELAY | SIGNAL_RIGHT_RELAY | SIGNAL_HAZARD_RELAY)

#define LOCK_PULSE_DEFAULT_MS 5000u
#define LOCK_PULSE_MIN_MS 100u
#define LOCK_PULSE_MAX_MS 10000u

static char s_current_pin[8] = {0}; /* 6 digits + null */

static void uart_send_line(const char *line)
{
    if (line == NULL)
    {
        return;
    }

    size_t len = strlen(line);
    char *copy = (char *)pvPortMalloc(len + 1u);
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

static const char *kv_get(const char *token)
{
    const char *eq = strchr(token, '=');
    if (eq == NULL)
    {
        return NULL;
    }
    return eq + 1;
}

static int kv_key_is(const char *token, const char *key)
{
    size_t klen;
    const char *eq;

    if ((token == NULL) || (key == NULL))
    {
        return 0;
    }
    eq = strchr(token, '=');
    if (eq == NULL)
    {
        return 0;
    }
    klen = (size_t)(eq - token);
    return (strlen(key) == klen) && (strncmp(token, key, klen) == 0);
}

static int16_t clamp_i16(int v, int16_t lo, int16_t hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return (int16_t)v;
}

static uint32_t clamp_u32(uint32_t v, uint32_t lo, uint32_t hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static void signal_set_mode_off(void)
{
    HAL_GPIO_WritePin(SIGNAL_RELAY_PORT, SIGNAL_RELAY_ALL, GPIO_PIN_RESET);
}

static void signal_set_mode_left(void)
{
    HAL_GPIO_WritePin(SIGNAL_RELAY_PORT, SIGNAL_RELAY_ALL, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(SIGNAL_RELAY_PORT, SIGNAL_LEFT_RELAY, GPIO_PIN_SET);
}

static void signal_set_mode_right(void)
{
    HAL_GPIO_WritePin(SIGNAL_RELAY_PORT, SIGNAL_RELAY_ALL, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(SIGNAL_RELAY_PORT, SIGNAL_RIGHT_RELAY, GPIO_PIN_SET);
}

static void signal_set_mode_hazard(void)
{
    HAL_GPIO_WritePin(SIGNAL_RELAY_PORT, SIGNAL_RELAY_ALL, GPIO_PIN_SET);
}

static void handle_cmd_motor(char *saveptr)
{
    int l = 0;
    int r = 0;
    char *tok;

    while ((tok = strtok_r(NULL, ";", &saveptr)) != NULL)
    {
        if (kv_key_is(tok, "L"))
        {
            l = atoi(kv_get(tok));
        }
        else if (kv_key_is(tok, "R"))
        {
            r = atoi(kv_get(tok));
        }
    }

    motor_left_drive(clamp_i16(l, -1000, 1000));
    motor_right_drive(clamp_i16(r, -1000, 1000));

    uart_send_line("RD1;ACK;MOTOR;OK=1\n");
}

static void handle_cmd_mpu_read(void)
{
    MPU6050_t data;
    char out[CMD_TX_MAX];

    memset(&data, 0, sizeof(data));
    mpu_read_data(&data);

    (void)snprintf(
        out,
        sizeof(out),
        "RD1;EVT;MPU;AXR=%d;AYR=%d;AZR=%d;GXR=%d;GYR=%d;GZR=%d;T=%d\n",
        (int)data.Accel_X_RAW,
        (int)data.Accel_Y_RAW,
        (int)data.Accel_Z_RAW,
        (int)data.Gyro_X_RAW,
        (int)data.Gyro_Y_RAW,
        (int)data.Gyro_Z_RAW,
        (int)(data.Temperature * 100.0f)
    );

    uart_send_line(out);
}

static void handle_cmd_pin_set(char *saveptr)
{
    char *tok;
    const char *pin = NULL;

    while ((tok = strtok_r(NULL, ";", &saveptr)) != NULL)
    {
        if (kv_key_is(tok, "PIN"))
        {
            pin = kv_get(tok);
        }
    }

    if ((pin != NULL) && (strlen(pin) >= 4u) && (strlen(pin) <= 6u))
    {
        memset(s_current_pin, 0, sizeof(s_current_pin));
        strncpy(s_current_pin, pin, sizeof(s_current_pin) - 1u);
        uart_send_line("RD1;ACK;PIN_SET;OK=1\n");
    }
    else
    {
        uart_send_line("RD1;ERR;PIN_SET;OK=0;ERR=BAD_PIN\n");
    }
}

static void handle_cmd_pin_clear(void)
{
    memset(s_current_pin, 0, sizeof(s_current_pin));
    uart_send_line("RD1;ACK;PIN_CLEAR;OK=1\n");
}

static void lock_pulse_open(uint32_t pulse_ms)
{
    /* Assumption: GPIO_PIN_SET opens the lock. Adjust if wiring is inverted. */
    HAL_GPIO_WritePin(Lock_GPIO_Port, Lock_Pin, GPIO_PIN_SET);
    vTaskDelay(pdMS_TO_TICKS(pulse_ms));
    HAL_GPIO_WritePin(Lock_GPIO_Port, Lock_Pin, GPIO_PIN_RESET);
}

static void handle_cmd_signal(char *saveptr)
{
    char *tok;
    const char *mode = NULL;

    while ((tok = strtok_r(NULL, ";", &saveptr)) != NULL)
    {
        if (kv_key_is(tok, "MODE"))
        {
            mode = kv_get(tok);
        }
    }

    if (mode == NULL)
    {
        uart_send_line("RD1;ERR;SIGNAL;OK=0;ERR=NO_MODE\n");
        return;
    }

    if (strcmp(mode, "OFF") == 0)
    {
        signal_set_mode_off();
    }
    else if (strcmp(mode, "LEFT") == 0)
    {
        signal_set_mode_left();
    }
    else if (strcmp(mode, "RIGHT") == 0)
    {
        signal_set_mode_right();
    }
    else if (strcmp(mode, "HAZARD") == 0)
    {
        signal_set_mode_hazard();
    }
    else
    {
        uart_send_line("RD1;ERR;SIGNAL;OK=0;ERR=BAD_MODE\n");
        return;
    }

    {
        char out[48];
        (void)snprintf(out, sizeof(out), "RD1;ACK;SIGNAL;OK=1;MODE=%s\n", mode);
        uart_send_line(out);
    }
}

static void handle_cmd_lock_pulse(char *saveptr)
{
    char *tok;
    uint32_t pulse_ms = LOCK_PULSE_DEFAULT_MS;

    while ((tok = strtok_r(NULL, ";", &saveptr)) != NULL)
    {
        if (kv_key_is(tok, "MS"))
        {
            pulse_ms = (uint32_t)atoi(kv_get(tok));
        }
    }

    pulse_ms = clamp_u32(pulse_ms, LOCK_PULSE_MIN_MS, LOCK_PULSE_MAX_MS);
    lock_pulse_open(pulse_ms);

    {
        char out[64];
        (void)snprintf(out, sizeof(out), "RD1;ACK;LOCK_PULSE;OK=1;MS=%lu\n", (unsigned long)pulse_ms);
        uart_send_line(out);
    }
}

static void handle_cmd_unlock(char *saveptr)
{
    char *tok;
    const char *pin = NULL;

    while ((tok = strtok_r(NULL, ";", &saveptr)) != NULL)
    {
        if (kv_key_is(tok, "PIN"))
        {
            pin = kv_get(tok);
        }
    }

    if ((pin == NULL) || (s_current_pin[0] == '\0'))
    {
        uart_send_line("RD1;EVT;UNLOCKED;OK=0;ERR=NO_PIN\n");
        return;
    }

    if (strncmp(pin, s_current_pin, sizeof(s_current_pin)) == 0)
    {
        lock_pulse_open(LOCK_PULSE_DEFAULT_MS);
        uart_send_line("RD1;EVT;UNLOCKED;OK=1\n");
    }
    else
    {
        uart_send_line("RD1;EVT;UNLOCKED;OK=0;ERR=BAD_PIN\n");
    }
}

static void handle_line(char *line)
{
    char *saveptr = NULL;
    char *p;
    char *kind;
    char *name;

    if (line == NULL)
    {
        return;
    }

    /* token0: RD1 */
    p = strtok_r(line, ";", &saveptr);
    if ((p == NULL) || (strncmp(p, "RD1", 3) != 0))
    {
        return;
    }

    kind = strtok_r(NULL, ";", &saveptr);
    name = strtok_r(NULL, ";", &saveptr);
    if ((kind == NULL) || (name == NULL))
    {
        return;
    }

    if (strcmp(kind, "CMD") != 0)
    {
        return;
    }

    if (strcmp(name, "MOTOR") == 0)
    {
        handle_cmd_motor(saveptr);
    }
    else if (strcmp(name, "MOTOR_STOP") == 0)
    {
        motor_stop();
        uart_send_line("RD1;ACK;MOTOR_STOP;OK=1\n");
    }
    else if (strcmp(name, "MPU_READ") == 0)
    {
        handle_cmd_mpu_read();
    }
    else if (strcmp(name, "PIN_SET") == 0)
    {
        handle_cmd_pin_set(saveptr);
    }
    else if (strcmp(name, "PIN_CLEAR") == 0)
    {
        handle_cmd_pin_clear();
    }
    else if (strcmp(name, "UNLOCK") == 0)
    {
        handle_cmd_unlock(saveptr);
    }
    else if (strcmp(name, "SIGNAL") == 0)
    {
        handle_cmd_signal(saveptr);
    }
    else if (strcmp(name, "LOCK_PULSE") == 0)
    {
        handle_cmd_lock_pulse(saveptr);
    }
    else if (strcmp(name, "PING") == 0)
    {
        uart_send_line("RD1;ACK;PING;OK=1\n");
    }
    else
    {
        uart_send_line("RD1;ERR;UNKNOWN;OK=0\n");
    }
}

static void task_cmd(void *params)
{
    msg_t rx;
    char *line;

    (void)params;

    for (;;)
    {
        if (msg_queue_receive(MSG_QUE_UART_RX, &rx, portMAX_DELAY) == pdPASS)
        {
            line = (char *)rx;
            if (line != NULL)
            {
                handle_line(line);
                vPortFree(line);
            }
        }
    }
}

ErrorMessage init_task_cmd(void)
{
    if (xTaskCreate(task_cmd, "CMD Task", 256, NULL, 2, NULL) != pdPASS)
    {
        return E_INIT_ERROR;
    }
    return E_SUCCESS;
}
