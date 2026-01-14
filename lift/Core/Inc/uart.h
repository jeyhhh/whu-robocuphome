#ifndef __UART_H
#define __UART_H

#include "main.h"

// 命令类型
typedef enum {
    CMD_STOP = 0x00,
    CMD_SET_SPEED = 0x01,
    CMD_SET_POSITION = 0x02,
    CMD_GET_STATUS = 0x03,
    CMD_SET_PID = 0x04,
    CMD_RESET = 0xFF
} UART_Command;

// 协议帧结构
typedef struct {
    uint8_t header;      // 帧头 0xAA
    uint8_t cmd;         // 命令
    uint8_t length;      // 数据长度
    uint8_t data[8];     // 数据
    uint8_t checksum;    // 校验和
} UART_Frame;

// 函数声明
void UART_Init(void);
void UART_Send_Status(int32_t position, int32_t speed);
void UART_Send_Raw(const char* format, ...);
void UART_Receive_Handler(void);
void UART_Parse_Command(UART_Frame* frame);

#endif