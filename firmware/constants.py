# Make sure you don't put sensitive information in comments...
STRING_FLAG = 'BHV_FIRMW4R3_5_56789'

# LEDS
LED_PIN = 10
LED_ENABLE_PIN = 20
LED_COUNT = 17
LED_BOOT_TIME_S = 7
LED_FRAME_RATE = 60
LED_SIREN_DELAY = 0.25
LED_MAX_INTENSITY = 0.25
LED_COLORS = {
    'OFF':      [  0,   0,   0],
    'BHV':      [  1, 62,  7],
    'RED':      [255,   0,   0],
    'WHITE':    [255, 255, 255],
    'BLUE':     [  0,   0, 255],
    'PINK':     [255, 192, 203],
    'ORANGE':   [255,  30,   0],
    'GOLD':     [255, 180,   0],
    'YELLOW':   [255, 255,   0],
    'TAN':      [255, 105,  50],
    'GREEN':    [  0, 50,   0],
    'MINT':     [  0, 255,  60],
    'CYAN':     [  0, 255, 140],
    'LIGHTBLUE':[  0, 140, 255],
    'PURPLE':   [115,   0, 255],
    'MAGENTA':  [220,   0, 255]
}

# SCAN 
SCAN_COUNT = 3

# SCREEN
I2C_SDA_PIN = 18
I2C_SCL_PIN = 19
I2C_INSTANCE = 1
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

# SENSOR
SENSOR_ENABLE_PIN = 21
V_SENSE_PIN = 26
ADC_SAMPLES = 100.0
ADC_RESOLUTION = 65535
ADC_VREF = 3.3
SUPPLY_VOLTAGE = 4.6
LOAD_RESISTOR = 1e3
R0 = 500
COEFF_1 = 0.1896 # Moving to configuration file
COEFF_2 = 8.6178 # Moving to configuration file
COEFF_3 = 1.0792 # Moving to configuration file

# SERIAL
SERIAL_TX_PIN = 12
SERIAL_RX_PIN = 13
BAUD_RATE = 115200
UART_INSTANCE = 0
COMMS_TRANSMISSION_COUNT = 5

# DETECT
V_BATT_DETECT_PIN = 27
V_USB_DETECT_PIN = 28

# INTERRUPT
INTERRUPT_PIN = 22