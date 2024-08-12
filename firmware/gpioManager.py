from machine import Pin
import time
import utime

class GPIOManager:
    def __init__(self):
        self.pinArray = [None] * 10
        for gpio in range(10):
            self.pinArray[gpio] = Pin(gpio, Pin.IN, Pin.PULL_UP)
        self.gpioStatus = [False] * 10
        self.gpioLookup = [ 3, 1, 5, 4, 6, 0, 9, 2, 7, 8 ]

    def get_gpio_status(self):
        for gpio in range(10):
            # Need to map the GPIO status to the actual GPIO. This might work? 
            self.gpioStatus[gpio] = self.pinArray[self.gpioLookup[gpio]].value()

    def check_gpio(self, gpio):
        # This check prevents people from simply raising every sequence to 1
        self.get_gpio_status()
        for index, gpioStatus in enumerate(self.gpioStatus):
            if( index == gpio ):
                if( gpioStatus == 1 ):
                    return False
            else:
                if( gpioStatus == 0 ):
                    return False
        return True

    def read_gpio(self, gpio):
        startTime = utime.ticks_ms()
        while( utime.ticks_diff(utime.ticks_ms(), startTime) < 5*1000):
            if( self.check_gpio(gpio) ):
                return True
            time.sleep(0.25)
        return False
    
    def gpio_sequence(self):
        expectedSequence = '01189998819991197253'
        #expectedSequence = '2345'
        expectedSequenceArray = list(expectedSequence)
        for gpio in expectedSequenceArray:
            if( False == self.read_gpio(int(gpio)) ):
                return False
        return True