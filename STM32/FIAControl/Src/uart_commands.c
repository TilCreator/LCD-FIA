#include "uart_commands.h"
#include "fia.h"
#include "uart_protocol.h"
#include <string.h>

void UART_ProcessCommand(uint8_t command, uint8_t* parameters, uint8_t parameterLength) {
    uint8_t responseLength = 0;

    switch (command) {
        case UART_CMD_NULL: {
            uartTxPayload[0] = 0xFF;
            responseLength = 1;
            break;
        }

        case UART_CMD_SET_BACKLIGHT_STATE: {
            FIA_SetBacklight(parameters[0]);
            responseLength = 0;
            break;
        }

        case UART_CMD_GET_BACKLIGHT_STATE: {
            uartTxPayload[0] = FIA_GetBacklight();
            responseLength = 1;
            break;
        }

        case UART_CMD_SET_BACKLIGHT_BASE_BRIGHTNESS: {
            memcpy(FIA_BacklightBaseBrightness, parameters, 4);
            responseLength = 0;
            break;
        }

        case UART_CMD_GET_BACKLIGHT_BASE_BRIGHTNESS: {
            memcpy(uartTxPayload, FIA_BacklightBaseBrightness, 4);
            responseLength = 4;
            break;
        }

        case UART_CMD_SET_HEATERS_STATE: {
            FIA_SetHeaters(parameters[0]);
            responseLength = 0;
            break;
        }

        case UART_CMD_GET_HEATERS_STATE: {
            uartTxPayload[0] = FIA_GetHeaters();
            responseLength = 1;
            break;
        }

        case UART_CMD_SET_CIRCULATION_FANS_STATE: {
            FIA_SetCirculationFans(parameters[0]);
            responseLength = 0;
            break;
        }

        case UART_CMD_GET_CIRCULATION_FANS_STATE: {
            uartTxPayload[0] = FIA_GetCirculationFans();
            responseLength = 1;
            break;
        }

        case UART_CMD_SET_HEAT_EXCHANGER_FAN_STATE: {
            FIA_SetHeatExchangerFan(parameters[0]);
            responseLength = 0;
            break;
        }

        case UART_CMD_GET_HEAT_EXCHANGER_FAN_STATE: {
            uartTxPayload[0] = FIA_GetHeatExchangerFan();
            responseLength = 1;
            break;
        }

        case UART_CMD_SET_BACKLIGHT_BALLAST_FANS_STATE: {
            FIA_SetBacklightBallastFans(parameters[0]);
            responseLength = 0;
            break;
        }

        case UART_CMD_GET_BACKLIGHT_BALLAST_FANS_STATE: {
            uartTxPayload[0] = FIA_GetBacklightBallastFans();
            responseLength = 1;
            break;
        }

        case UART_CMD_GET_DOOR_STATES: {
            uartTxPayload[0] = FIA_GetDoors();
            responseLength = 1;
            break;
        }

        case UART_CMD_GET_TEMPERATURES: {
            int16_t tempExt1 = FIA_GetTemperature(EXT_1) * 100;
            int16_t tempExt2 = FIA_GetTemperature(EXT_2) * 100;
            uartTxPayload[0] = tempExt1 >> 8;
            uartTxPayload[1] = tempExt1 & 0xFF;
            uartTxPayload[2] = tempExt2 >> 8;
            uartTxPayload[3] = tempExt2 & 0xFF;
            responseLength = 4;
            break;
        }
    }

    UART_TransmitResponse(uartTxPayload, responseLength);
}