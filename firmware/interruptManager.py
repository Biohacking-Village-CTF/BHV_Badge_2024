import machine 
from machine import Pin, Timer
import utime as time
import constants

class InterruptManager:
	def __init__(self, screenManager, sensorManager, configManager):
		self.interruptPin = Pin(constants.INTERRUPT_PIN, Pin.IN)  
		self.screenManager = screenManager
		self.sensorManager = sensorManager
		self.interruptPin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,handler=self.irq_handler)
		self.irqReady = True
		self.buttonTimer = 0
		self.showingQrCode = False
		# self.timer = Timer(period=2000, callback=self.irq_unified_handler)
		self.irq_source = 0
		self.irq_state = 0

	# def irq_unified_handler(self, source):
	#     try:
	#         if( self.irqReady ):
	#             self.irqReady = False
	#             if isinstance(source, Pin):
	#                 self.irq_source = source.irq().flags()
	#                 if self.irq_source == Pin.IRQ_FALLING:
	#                     # When Pressed, we will update the button timer to current ticks. 
	#                     print(f"Falling edge detected on pin {source}")
	#                     self.buttonTimer = time.ticks_ms()
	#                 elif self.irq_source == Pin.IRQ_RISING:
	#                     print(f"Rising edge detected on pin {source}")
	#                     if self.buttonTimer != 0:
	#                         if time.ticks_diff(time.ticks_ms(), self.buttonTimer) < 250:
	#                             print("Short Press Detected")
	#                             self.ShortButtonPress()
	#                             self.buttonTimer = 0
	#                         else:
	#                             print("Long Press Detected")
	#                             self.buttonTimer = 0
	#                             self.LongButtonPress()
	#                 else:
	#                     print("Unknown IRQ Source")
	#             # elif isinstance(source, Timer):
	#             #     print("Timer interrupt occurred")
	#             #     # a few periodic activites, 
	#             #     #Clear the timer interrupt
	#             #     #[TODO] Manually unmask the irq... 
	#             #     # If the button has been pressed, then we can go ahead and process the long press after 2 sec.
	#             #     if self.buttonTimer != 0:
	#             #         if time.ticks_diff(time.ticks_ms(), self.buttonTimer) > 2000:
	#             #             print("Long Press Detected")
	#             #             self.buttonTimer = 0
	#             #             # self.LongButtonPress()
	#             # # Set up the timer and attach the IRQ handler
	#             self.irqReady = True
	#     except Exception as e:
	#         print(f"Error: {e}") 
	#         self.screenManager.updatePersonalizedMsg("Error")
	#         self.irq_ready = True
		
	# #TODO:  Add a Timer to get back to the main screen after a certain amount of time
	def irq_handler(self, pin):
		try:
			if( self.irqReady ):
				self.irqReady = False
				if pin.value() == 0:
					print("Interrupt Detected: Falling Edge")
					self.buttonTimer = time.ticks_ms()
				else:
					print("Interrupt Detected: Rising Edge")
					if( self.buttonTimer == 0 ):
						print("Error: Button Timer Not Set")
					else:
						if( time.ticks_diff(time.ticks_ms(), self.buttonTimer) < 250 ):
							print("Short Press Detected")
							self.ShortButtonPress()
							self.buttonTimer = 0
						else:
							print("Long Press Detected")
							self.LongButtonPress()
							self.buttonTimer = 0
				self.irqReady = True
		except Exception as e:
			print(f"Error: {e}") 
			self.screenManager.updatePersonalizedMsg("Error")
		


	def ShortButtonPress(self):
		try: 
			if self.showingQrCode:
				self.showingQrCode = False
				self.screenManager.updatePersonalizedMsg("Badge by SolaSec")
				return
			else:
				self.screenManager.updateBACScreen( message="Warmin' Up")
				self.sensorManager.bac_algorithm_wait()
				self.screenManager.updateBACScreen( message="Blow Now!")
				bac = self.sensorManager.bac_algorithm_run()
				self.screenManager.updateBACScreen( bac = bac )

			time.sleep(5)

			# Reload Screen / Might Need Config Manager Here
			self.screenManager.updatePersonalizedMsg(configManager.configDatea)
		except Exception as e:
			print(f"Error: {e}") 
			self.screenManager.updatePersonalizedMsg("Error")
	

	def LongButtonPress(self):
		try:
			if( self.showingQrCode ):
				self.screenManager.updatePersonalizedMsg("Badge by SolaSec")
				self.showingQrCode = False
			else:
				self.screenManager.connectQRCode()
				#TODO Simply Cycle Screens! 
				self.showingQrCode = True

		except Exception as e:
			print(f"Error: {e}") 
			self.screenManager.updatePersonalizedMsg("Error")