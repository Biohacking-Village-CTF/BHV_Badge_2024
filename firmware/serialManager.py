from machine import Pin, UART
import time
import constants

class SerialManager:
    def __init__(self):
        self.uart_tx = Pin(constants.SERIAL_TX_PIN)  # GPIO 12 Pin 16
        self.uart_rx = Pin(constants.SERIAL_RX_PIN)  # GPIO 13 Pin 17
        self.uart = UART(0, baudrate=constants.BAUD_RATE, tx=self.uart_tx, rx=self.uart_rx)

    def transmit_comms(self, payload):
        for i in range(constants.COMMS_TRANSMISSION_COUNT):
            self.uart.write(payload)
            time.sleep(1)


    
