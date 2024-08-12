from machine import Pin
import time
from neopixel import NeoPixel
import constants
import utime

class LEDManager:
	def __init__(self, startupColor):
		self.ledPin = Pin(constants.LED_PIN, Pin.OUT)
		self.ledEnablePin = Pin(constants.LED_ENABLE_PIN, Pin.OUT)
		self.strand = NeoPixel(self.ledPin, constants.LED_COUNT)
		self.sirenColor1 = constants.LED_COLORS['RED']
		self.sirenColor2 = constants.LED_COLORS['WHITE']
		if startupColor.upper() in constants.LED_COLORS:
			self.bootColor = constants.LED_COLORS[startupColor.upper()]
		else:
			self.bootColor = constants.LED_COLORS['BHV']
		# LED Configuration - Actual LED Numbers (Subtraction for indexing happens in code below)
		self.frontSiren = [2,4,6,8,10]
		self.backSiren  = [3,5,7,9,11]
		self.logo       = [12,13,14]
		self.solasec    = [15,16,17]
		self.window     = [1]


	def enable_led_voltage(self):
		self.ledEnablePin.on()   

	def disable_led_voltage(self):
		self.ledEnablePin.off()

	def update_siren_colors(self, siren1Color, siren2Color):
		if( siren1Color in constants.LED_COLORS ):
			self.sirenColor1 = constants.LED_COLORS[siren1Color]

		if( siren2Color in constants.LED_COLORS ):
			self.sirenColor2 = constants.LED_COLORS[siren2Color]

	def update_boot_color(self, bootColor):
		if( bootColor in constants.LED_COLORS ):
			self.bootColor = constants.LED_COLORS[bootColor]

	def turn_off_leds(self):
		for led in range(constants.LED_COUNT):
			self.strand[led] = tuple(constants.LED_COLORS['OFF'])
		self.strand.write()

	def boot(self):
		self.enable_led_voltage()
		self.turn_off_leds()
		total_frames = constants.LED_BOOT_TIME_S * constants.LED_FRAME_RATE

		# Calculate increments per frame
		increments = [
			(self.bootColor[i] - constants.LED_COLORS['OFF'][i]) / total_frames for i in range(3)
		]

		current_color = constants.LED_COLORS['OFF'][:]
		i = 20
		brightness = 1
		# Function to update the color
		def update_color():
			for i in range(3):
				current_color[i] += increments[i]

		# Animation loop
		for frame in range(total_frames):
			update_color()
			for led in self.logo:
				self.strand[led-1] = tuple([int(current_color[0]), int(current_color[1]), int(current_color[2])])
				# self.strand[led-1] = tuple([int(color * brightness) for color in (self.wheel((i+led*20) & 255) )])
			i = i+1
			for led in self.solasec:
				self.strand[led-1] = tuple([int(color * brightness) for color in (self.wheel((i+led*20) & 255) )])
			self.strand.write()
			time.sleep(1 / constants.LED_FRAME_RATE)

			self.strand[0] = tuple([int(color * brightness) for color in (self.wheel((i) & 255) )])
			self.strand.write()
			time.sleep(1 / constants.LED_FRAME_RATE)
		self.turn_off_leds()
		self.turn_off_leds()
		self.disable_led_voltage()


	def siren(self, duration=5):
		self.enable_led_voltage()
		self.turn_off_leds()
		startTime = utime.ticks_ms()
		pattern_shift = 0  # Shift between 0 and 1 to alternate the pattern
		while( utime.ticks_diff(utime.ticks_ms(), startTime) < duration*1000):  
			for led in self.window:
				if( pattern_shift == 0 ):
					self.strand[led-1] = tuple(constants.LED_COLORS['WHITE']) 
				else:
					self.strand[led-1] = tuple(constants.LED_COLORS['OFF']) 
			for index, led in enumerate(self.frontSiren):
				# Check led index plus the pattern_shift modulo 2 to alternate colors every cycle
				if (index + pattern_shift) % 2 == 0:
					self.strand[led-1] = tuple(self.sirenColor1)
				else:
					self.strand[led-1] = tuple(self.sirenColor2)
			for index, led in enumerate(self.backSiren):
				# Check led index plus the pattern_shift modulo 2 to alternate colors every cycle
				if (index + pattern_shift) % 2 == 0:
					self.strand[led-1] = tuple(self.sirenColor1)
				else:
					self.strand[led-1] = tuple(self.sirenColor2)                                     
			for index, led in enumerate(self.logo):
				# Set Logo
				self.strand[led-1] = tuple(self.bootColor)
			self.strand.write()  # Update LED display
			time.sleep(constants.LED_SIREN_DELAY)  # Brief pause to visualize the effect

			# Change pattern shift from 0 to 1 or from 1 to 0, effectively shifting the whole pattern
			pattern_shift = 1 - pattern_shift

		self.turn_off_leds()
		self.disable_led_voltage()

	#function to take a value of 0-255 to return a color value tuple
	def wheel(self, pos, brightness = 1.0):
		if pos < 85:
			return (pos * 3, 255 - pos * 3, 0)
		elif pos < 170:
			pos -= 85
			return (255 - pos * 3, 0, pos * 3)
		else:
			pos -= 170
			return (0, pos * 3, 255 - pos * 3)

	def prettyRainbow(self, duration=3, brightness = 1.0):
		self.enable_led_voltage()
		self.turn_off_leds()
		startTime = utime.ticks_ms()
		while( utime.ticks_diff(utime.ticks_ms(), startTime) < duration*1000):  
			for i in range(190,255):
				for led in range(constants.LED_COUNT):
					self.strand[led] = tuple([int(color * brightness) for color in (self.wheel((i+led*10) & 255) )])
				self.strand.write()
				time.sleep(.01)

			for i in range(255,190,-1):
				for led in range(constants.LED_COUNT):
					self.strand[led] = tuple([int(color * brightness) for color in (self.wheel((i+led*10) & 255) )])
				self.strand.write()
				time.sleep(.01)
	
		self.turn_off_leds()
		self.disable_led_voltage()

	def flash_logo(self, color):
		self.enable_led_voltage()
		self.turn_off_leds()        
		for index, led in enumerate(self.logo):
			self.strand[led-1] = tuple(constants.LED_COLORS[color])
		self.strand.write()

	def override_color(self, color):
		for led in range(17):
			self.strand[led] = tuple(constants.LED_COLORS[color])
		self.strand.write()
		
	def flash_section(self, section, colorWheel, brightness = 1.0):
		self.enable_led_voltage()
		for led in section:
			self.strand[led-1] = tuple([int(color * brightness) for color in (self.wheel(colorWheel&255))])
			self.strand.write()
		time.sleep(3)
		self.turn_off_leds()
		self.disable_led_voltage()