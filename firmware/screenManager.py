from machine import Pin, I2C

import constants
from ssd1306 import SSD1306_I2C
from uQR import QRCode


class ScreenManager:
    def __init__(self, bootMsg="Booting...", deviceName="Badge", configManger=None, detectManager=None):
        sda_pin = Pin(constants.I2C_SDA_PIN)
        scl_pin = Pin(constants.I2C_SCL_PIN)
        self.i2c = I2C(constants.I2C_INSTANCE, sda=sda_pin, scl=scl_pin)
        self.oled = SSD1306_I2C(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, self.i2c)
        self.batteryPercent = 0
        self.detectManager = detectManager
        self.configManager = configManger
        self.password = "null"
        self.stringArray = [
            '',
            '',
            bootMsg,
            '',
            f'    Ver. {self.configManager.configData['version']}',
            ''
        ]
        self.ssid = deviceName
        # TODO Clear Screen
        self.updateScreen()
        self.addBattery()
        self.oled.show()

    def updateScreen(self):
        self.oled.fill(0)
        for row, string in enumerate(self.stringArray):
            row = row * 10
            self.oled.text(string, 0, row)
        self.addBattery()
        self.oled.show()

    def bhvScreen(self, bac=None, message=None):
        self.oled.fill(0)
        # self.oled.text("o-LIT-oscope", 0, 0)
        self.addBattery()
        self.oled.large_text("WINNER", 20, 22, 2)
        self.oled.show()

    def updateBACScreen(self, bac=None, message=None):
        self.oled.fill(0)
        self.oled.text("     BAC    ", 0, 0)
        # self.oled.text("o-LIT-oscope", 0, 0)
        self.addBattery()

        if message is not None:
            BACText = message
            self.oled.large_text(BACText, 16, 24, 1)
        else:
            if bac is None:
                BACText = "  --  "
            else:
                BACText = f"{float(bac):.3f}%"
            self.oled.large_text(BACText, 16, 24, 2)
        self.oled.show()

        # def showStatsScreen(self, battVoltage=0.0, usbVoltage=0.0, batteryPercent=0.0):
        #     self.oled.fill(0)

        #     self.stringArray = [
        #         '<   Stats   >',
        #         '',
        #         f'Batt %: {batteryPercent:.2f}%',
        #         f'Batt V: {battVoltage:.2f}V',
        #         f'USB  V: {usbVoltage:.2f}V',
        #         '',
        #     ]
        #     self.updateScreen()

    def showConnectedScreen(self):
        self.oled.fill(0)

        self.stringArray = [
            'Ext. Power-->',
            '',
            '',
            'Charging Battery',
            '',
        ]
        self.updateScreen()

    def updateAll(self, deviceName, flagCount=0, ipAddress="IP: X.X.X.X", personalizedMsg="Badge by SolaSec"):
        self.oled.fill(0)
        self.stringArray = [
            'Biohacking',
            'Village',
            deviceName,
            f"Flags: {flagCount}/8",
            ipAddress,
            personalizedMsg
        ]
        self.updateScreen()

    def addBattery(self, inverted=False):
        if inverted:
            bit = 0
        else:
            bit = 1

        self.oled.rect(110, 1, 14, 8, bit)
        self.oled.rect(125, 3, 1, 4, bit)
        self.oled.rect(110, 1, int(14 * self.detectManager.read_batt_life() / 100), 8, bit, 1)

    def connectQRCode(self):
        self.oled.fill(1)
        self.password = self.configManager.configData['apPassword']
        qr = QRCode()
        print(f"WIFI:T:WPA;S:{self.ssid};P:{self.password};;")
        qr.add_data(f"WIFI:T:WPA;S:{self.ssid};P:{self.password};;")
        qr.border = 2
        matrix = qr.get_matrix()
        # print(matrix)
        for y in range(len(matrix) * 2):  # Scaling the bitmap by 2
            for x in range(len(matrix[0]) * 2):  # because my screen is tiny.
                value = not matrix[int(y / 2)][int(x / 2)]  # Inverting the values because
                self.oled.pixel(x + 10, y - 2, value)  # black is `True` in the matrix.

        self.oled.text("WiFi", 80, 15, 0)
        self.oled.text("Pass:", 80, 25, 0)
        # next Print the first 4 charachters of the password
        self.oled.text(self.password[:4], 80, 35, 0)
        self.oled.text(self.password[-4:], 80, 45, 0)
        self.oled.text

        self.addBattery(inverted=True)
        self.oled.show()

    def updateDeviceName(self, deviceName):
        self.stringArray[2] = deviceName
        self.updateScreen()

    def updateFlagCount(self, flagCount):
        self.stringArray[3] = f"Flags: {flagCount}/8"
        self.updateScreen()

    def updateIPAddress(self, ipAddress):
        self.stringArray[4] = ipAddress
        self.updateScreen()

    def updatePersonalizedMsg(self, personalizedMsg):
        self.stringArray[5] = personalizedMsg  # TODO: Check max length
        self.updateScreen()
