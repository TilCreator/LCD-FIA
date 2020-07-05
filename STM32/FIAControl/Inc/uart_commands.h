#pragma once

/*
  uart_commands.h / uart_commands.c - List of commands and parameters
  for the UART protocol as well as the command handler logic
*/

#include <stdint.h>

// Commands
// System
#define UART_CMD_NULL 0x00
#define UART_CMD_MCU_RESET 0x01

// Lights
#define UART_CMD_SET_BACKLIGHT_STATE 0x10
#define UART_CMD_GET_BACKLIGHT_STATE 0x11
#define UART_CMD_SET_BACKLIGHT_BASE_BRIGHTNESS 0x12
#define UART_CMD_GET_BACKLIGHT_BASE_BRIGHTNESS 0x13
#define UART_CMD_GET_BACKLIGHT_BRIGHTNESS 0x14

// Heat Management
#define UART_CMD_SET_HEATERS_STATE 0x20
#define UART_CMD_GET_HEATERS_STATE 0x21
#define UART_CMD_SET_CIRCULATION_FANS_STATE 0x22
#define UART_CMD_GET_CIRCULATION_FANS_STATE 0x23
#define UART_CMD_SET_HEAT_EXCHANGER_FAN_STATE 0x24
#define UART_CMD_GET_HEAT_EXCHANGER_FAN_STATE 0x25
#define UART_CMD_SET_BACKLIGHT_BALLAST_FANS_STATE 0x26
#define UART_CMD_GET_BACKLIGHT_BALLAST_FANS_STATE 0x27

// Doors
#define UART_CMD_GET_DOOR_STATES 0x30

// Sensors
#define UART_CMD_GET_TEMPERATURES 0x40
#define UART_CMD_GET_HUMIDITY 0x41
#define UART_CMD_GET_ENV_BRIGHTNESS 0x42

// LCDs
#define UART_CMD_SET_LCD_CONTRAST 0x50
#define UART_CMD_GET_LCD_CONTRAST 0x51

// Display Data
#define UART_CMD_CREATE_SCROLL_BUFFER 0x60
#define UART_CMD_DELETE_SCROLL_BUFFER 0x61
#define UART_CMD_SET_DESTINATION_BUFFER 0x62
#define UART_CMD_UPDATE_SCROLL_BUFFER 0x63

// Function prototypes
void UART_ProcessCommand(uint8_t command, uint8_t* parameters, uint8_t parameterLength);