from machine import Pin, ADC
import constants

class DetectManager:
    def __init__(self):
        self.v_batt_detect_pin = Pin(constants.V_BATT_DETECT_PIN)
        self.v_usb_detect_pin = Pin(constants.V_USB_DETECT_PIN)
        self.v_batt_adc = ADC(self.v_batt_detect_pin)
        self.v_usb_adc = ADC(self.v_usb_detect_pin)

    def read_v_usb(self):
        return self.v_usb_adc.read_u16() / constants.ADC_RESOLUTION * constants.ADC_VREF * 1.5
    
    def read_v_batt(self):
        return self.v_batt_adc.read_u16() / constants.ADC_RESOLUTION * constants.ADC_VREF * 1.5 + 0.1
    
    def read_batt_life( self):
        voltage = self.read_v_batt()
        return self.estimate_battery_percentage(voltage)
    
    def estimate_battery_percentage(self, voltage):
        #based on a quatric equation
        # percentage = (-2.281e+02 * voltage **2 + 2.066e+03 * voltage + 4.576e+03)/100
        percentage = 123 - 123/(1+((voltage/3.7)**80)**0.165)
        if(percentage < 0):
            return 0
        if(percentage > 100):
            return 100
        
        return percentage