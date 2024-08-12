import machine 
import constants
import utime as time


class SensorManager:
    def __init__(self, ledManager, screenManager):
        self.adc_pin = machine.Pin(constants.V_SENSE_PIN)
        self.sensor_enable_pin = machine.Pin(constants.SENSOR_ENABLE_PIN, machine.Pin.OUT)
        self.adc = machine.ADC(self.adc_pin)
        self.sensorValue = 0.0
        self.supplyVoltage = 4.6
        self.ledManager = ledManager
        self.screenManager = screenManager
        self.bac_readings = []
        
    def enable_sensor_voltage(self):
        self.sensor_enable_pin.on()
    
    def disable_sensor_voltage(self):
        self.sensor_enable_pin.off()        

    def read_adc(self):
         return self.adc.read_u16()

    def adc_to_voltage(self, adc_value):
        v_out = (adc_value / constants.ADC_RESOLUTION) * constants.ADC_VREF
        return v_out

    def calculate_sensor_resistance(self, adc_voltage):
        rs = (constants.SUPPLY_VOLTAGE - adc_voltage) * constants.LOAD_RESISTOR / adc_voltage
        return rs

    def get_bac(self, rs):
        ratio = rs / constants.R0
        # Logarithmic relationship derived from experimental data
        mgl = (0.5605 / ratio) ** (1 / 0.654)
        # Simple/Crude Conversion from air mg/L to BAC
        bac = 0.21 * mgl
        return bac
    
    def average_array(self, array):
        arraySum = 0.0
        arrayCnt = 0
        for index, value in enumerate(array):
            arraySum = value + arraySum
            arrayCnt = arrayCnt+1
        return ( arraySum / arrayCnt )

    def bac_algorithm_wait(self):
        self.enable_sensor_voltage()

        # Wait For Ready
        self.ledManager.flash_logo('RED')
        time.sleep(3)
        self.ledManager.flash_logo('YELLOW')
        time.sleep(2)

    def bac_clear_readings(self):
        # In case it has not been enabled outside this function
        self.enable_sensor_voltage()

        # BLUE LOGO INDICATES CLEANING SENSOR
        self.ledManager.flash_logo('BLUE')
        
        # for 10 sec, print the bac and toggle sensor heater
        self.bac_readings.clear()
        startTime = time.ticks_ms()
        while( time.ticks_diff(time.ticks_ms(), startTime) < 10*1000):
            adc_value = self.adc.read_u16()
            
            adc_voltage = self.adc_to_voltage(adc_value)
            
            sensor_resistance = self.calculate_sensor_resistance(adc_voltage)
            
            bac = self.get_bac(sensor_resistance)
            self.bac_readings.append(bac)
            print(f"ADC {adc_value} / V: {adc_voltage:.6f} / R: {sensor_resistance:.2f} / BAC: {bac:.4f}")

            time.sleep(0.1)
        self.ledManager.turn_off_leds()
        self.disable_sensor_voltage()
        return self.bac_readings
    
    def bac_algorithm_run(self):
        self.ledManager.flash_logo('GREEN')
        time.sleep(1)               
        self.bac_readings.clear() 

        # Collect BAC Data for Three Seconds
        startTime = time.ticks_ms()
        while( time.ticks_diff(time.ticks_ms(), startTime) < 3*1000):  
            adc_value = self.adc.read_u16()
            
            # Calculate the output voltage
            adc_voltage = self.adc_to_voltage(adc_value)
            
            # Calculate the sensor resistance
            sensor_resistance = self.calculate_sensor_resistance(adc_voltage)
            
            # Calculate BAC
            bac = self.get_bac(sensor_resistance)
            #print(f"BAC: {bac}")
            self.bac_readings.append(bac)

            print(f"ADC: {adc_value} / V: {adc_voltage:.6f} / R: {sensor_resistance:.2f} / BAC: {bac:.4f}")
            
            time.sleep(0.1)
            
        # Return BAC
        # Cut data in half just to take the last samples for a better reading of lungs
        midpoint = int(len(self.bac_readings)/2)
        self.bac_readings = self.bac_readings[midpoint:]
        self.bac = self.average_array(self.bac_readings)

        self.ledManager.turn_off_leds()
        self.disable_sensor_voltage()

        return f"{self.bac:.4f}"