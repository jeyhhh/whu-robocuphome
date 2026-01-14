#include "uart.h"
#include "motor.h"
#include "encoder.h"
#include <stdio.h>
#include <stdarg.h>

extern UART_HandleTypeDef huart1;

// 串口接收缓冲区
#define UART_RX_BUFFER_SIZE 128
uint8_t uart_rx_buffer[UART_RX_BUFFER_SIZE];
uint16_t uart_rx_index = 0;

// 重定向printf到串口
#ifdef __GNUC__
#define PUTCHAR_PROTOTYPE int __io_putchar(int ch)
#else
#define PUTCHAR_PROTOTYPE int fputc(int ch, FILE *f)
#endif

PUTCHAR_PROTOTYPE
{
    HAL_UART_Transmit(&huart1, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
    return ch;
}

void UART_Init(void)
{
    // 启动串口接收中断
    HAL_UART_Receive_IT(&huart1, &uart_rx_buffer[uart_rx_index], 1);

    printf("\r\n===== 电机控制系统启动 =====\r\n");
    printf("波特率: 115200\r\n");
    printf("命令格式: [命令][数据]\r\n");
    printf("s[速度] - 设置速度(-1000~1000)\r\n");
    printf("p[位置] - 设置目标位置\r\n");
    printf("g - 获取状态\r\n");
    printf("x - 停止\r\n");
    printf("============================\r\n");
}

// 发送状态数据
void UART_Send_Status(int32_t position, int32_t speed)
{
    // 简单文本格式
    printf("POS:%ld,SPD:%ld\r\n", position, speed);

    // 或者二进制格式（更高效）
    uint8_t buffer[12];
    buffer[0] = 0xAA; // 帧头
    buffer[1] = 0x01; // 状态帧标识

    // 位置（4字节）
    buffer[2] = (position >> 24) & 0xFF;
    buffer[3] = (position >> 16) & 0xFF;
    buffer[4] = (position >> 8) & 0xFF;
    buffer[5] = position & 0xFF;

    // 速度（4字节）
    buffer[6] = (speed >> 24) & 0xFF;
    buffer[7] = (speed >> 16) & 0xFF;
    buffer[8] = (speed >> 8) & 0xFF;
    buffer[9] = speed & 0xFF;

    // 校验和
    buffer[10] = 0;
    for (int i = 0; i < 10; i++)
        buffer[10] += buffer[i];

    buffer[11] = 0x55; // 帧尾

    HAL_UART_Transmit(&huart1, buffer, 12, HAL_MAX_DELAY);
}

// 发送原始数据（printf风格）
void UART_Send_Raw(const char *format, ...)
{
    char buffer[128];
    va_list args;
    va_start(args, format);
    int len = vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);

    if (len > 0)
    {
        HAL_UART_Transmit(&huart1, (uint8_t *)buffer, len, HAL_MAX_DELAY);
    }
}

// 串口接收中断回调
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART1)
    {
        uint8_t received = uart_rx_buffer[uart_rx_index];

        // 简单命令解析（ASCII字符）
        switch (received)
        {
        case 's': // 设置速度
        case 'S':
            // 后面应该跟数字
            break;

        case 'p': // 设置位置
        case 'P':
            // 后面应该跟数字
            break;

        case 'g': // 获取状态
        case 'G':
            UART_Send_Status(
                Encoder_GetPosition(),
                Encoder_GetSpeed());
            break;

        case 'x': // 停止
        case 'X':
            Motor_Stop();
            printf("电机停止\r\n");
            break;

        case '\r': // 回车
        case '\n':
            // 处理完整命令
            if (uart_rx_index > 0)
            {
                uart_rx_buffer[uart_rx_index] = '\0';
                printf("收到: %s\r\n", uart_rx_buffer);

                // 解析命令
                Parse_Command((char *)uart_rx_buffer);
            }
            uart_rx_index = 0;
            break;

        default:
            if (uart_rx_index < UART_RX_BUFFER_SIZE - 1)
            {
                uart_rx_index++;
            }
            break;
        }

        // 重新启动接收
        HAL_UART_Receive_IT(&huart1, &uart_rx_buffer[uart_rx_index], 1);
    }
}

// 解析命令
void Parse_Command(char *cmd)
{
    if (cmd[0] == 's' || cmd[0] == 'S')
    {
        // 设置速度，格式: s500 或 s-300
        int speed = atoi(&cmd[1]);
        if (speed >= -1000 && speed <= 1000)
        {
            Motor_Speed(speed, 0);
            printf("设置速度: %d\r\n", speed);
        }
    }
    else if (cmd[0] == 'p' || cmd[0] == 'P')
    {
        // 设置位置
        int position = atoi(&cmd[1]);
        Encoder_SetTarget(position);
        printf("设置目标位置: %d\r\n", position);
    }
}