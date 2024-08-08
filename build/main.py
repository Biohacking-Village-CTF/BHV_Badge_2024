from microdot import Microdot, Response, send_file
from microdot.utemplate import Template
import gc
import json
import machine
from helpers import Helpers
from flagManager import FlagManager
from screenManager import ScreenManager
from scanManager import ScanManager
from sensorManager import SensorManager
from serialManager import SerialManager
from interruptManager import InterruptManager
from networkManager import NetworkManager
from configManager import ConfigManager
from gpioManager import GPIOManager
from ledManager import LEDManager
from detectManager import DetectManager
import utime as time
# import _thread
import constants
import _asyncio as asyncio

#Loading badge Configuration
helpers = Helpers()
device_id = helpers.device_name
networkSetting = 'AP'
bootupTime = time.ticks_ms()

configManager = ConfigManager()
# Generate random psk and store in database
if configManager.configData['apPassword'] == 'password':
	print("Generating Random password")
	configManager.update_config('apPassword', helpers.generate_password(8))

	
# Waking up Managers needed for charging and calibrating sensor...
# If USB power is present, we will go into a charging mode and burn off the residual alcohol.
detectManager = DetectManager()
screenManager = ScreenManager(f" Booting as {networkSetting}", device_id, configManager, detectManager)
ledManager = LEDManager(configManager.configData['startupColor'])
testmode = False
sensorManager = SensorManager(ledManager, screenManager)
# print("Battery Voltage", detectManager.read_v_batt())
# print("USB Voltage", detectManager.read_v_usb())
# print("Starting Up Sensor Manager")
gc.collect()

bootPin = machine.Pin(constants.INTERRUPT_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
#if bootpin is low on startup, enter test mode...
if( bootPin.value() == 0 ):
	testmode = True

if( detectManager.read_v_usb() > 4.0  or testmode ):  
	print("Starting up due to External Power")
	screenManager.showConnectedScreen()
	sensorManager.enable_sensor_voltage()
	sensorEnabled = True
	buttonUnPressed = True
	
	while( buttonUnPressed):
		if(testmode):
			ledManager.siren(10)
		else:
			time.sleep_ms(250)
			screenManager.showConnectedScreen()
			
		if bootPin.value() == 0:
			buttonUnPressed = False
			print("Button Pressed")
			sensorManager.disable_sensor_voltage()
			sensorEnabled = False
		elif(sensorEnabled):
			if(time.ticks_diff(time.ticks_ms(), bootupTime) > 300000):
				#Only leave the sensor for up to 5 minutes, then turn it off.
				sensorManager.disable_sensor_voltage()
				sensorEnabled = False
				print("Turning Off Sensor")
		if(testmode):
			ledManager.prettyRainbow(4, 0.25)
		else:
			time.sleep_ms(250)
		screenManager.showConnectedScreen()
	gc.collect()

interruptManager = InterruptManager(screenManager, sensorManager)
flagManager = FlagManager(device_id)
networkManager = NetworkManager(device_id, configManager.configData['apPassword'], networkSetting) 
scanManager = ScanManager(networkManager.wlan, flagManager)
gpioManager = GPIOManager()
serialManager = SerialManager()
screenManager.updateAll(device_id, flagManager.get_captured_flag_count(), f"IP: {networkManager.ip}", "Badge by SolaSec")
app = Microdot()
Response.default_content_type = 'text/html'
ledManager.boot()

interruptManager = InterruptManager(screenManager, sensorManager)

gc.collect()

# Page Routes
@app.route('/')
async def index(request):
	gc.collect()
	flag = flagManager.retrieve_flag('easy')
	return await Template('index.html').render_async(device_id=device_id, flag=flag)

@app.route('/admin')
async def admin(request):
	gc.collect()
	flag = flagManager.retrieve_flag('authorized')
	return await Template('admin.html').render_async(device_id=device_id, flag=flag)

@app.route('/flags')
async def flags(request):
	gc.collect()
	return await Template('flags.html').render_async(device_id=device_id)

@app.route('/test')
async def test(request):
	gc.collect()
	return await Template('test.html').render_async(device_id=device_id)

@app.route('/comms')
async def comms(request):
	gc.collect()
	return await Template('comms.html').render_async(device_id=device_id)

@app.route('/dial')
async def dial(request):
	global prompt
	prompt = "Waiting for GPIO activation..."
	return await Template('dial.html').render_async(device_id=device_id, prompt=prompt)

@app.route('/sensor')
async def sensor(request):
	gc.collect()
	sensor_value = '--'
	return await Template('sensor.html').render_async(device_id=device_id, sensor_value=sensor_value)

@app.route('/respond')
async def respond(request):
	gc.collect()
	return await Template('respond.html').render_async(device_id=device_id)

@app.route('/credits')
async def credits(request):
	return await Template('credits.html').render_async(device_id=device_id)

# Action Routes
@app.route('/start_sequence', methods=['GET'])
async def start_sequence(request):
	if( gpioManager.gpio_sequence() ):
		flag = flagManager.retrieve_flag('dial')
		prompt = f"Flag: {flag}\r\nMoss would be proud... "
	else:
		prompt = "Invalid Sequence. Try again..."
	return json.dumps({"prompt": prompt})

@app.route('/trigger_interface', methods=['GET'])
async def trigger_interface(request):
	flag = flagManager.retrieve_flag('comms')
	flag_payload = f"{flag}\r\n"

	serialManager.transmit_comms(flag_payload)

	# Update the prompt after the interface action is complete.
	prompt = "Comms action completed!"
	return json.dumps({"prompt": prompt})

@app.route('/get_ap_name', methods=['GET'])
async def get_ap_name(request):
	responseText = scanManager.get_ap_name()
	return json.dumps({"response": responseText})

@app.route('/get_scan_update', methods=['GET'])
async def get_scan_update(request):
	jsonData = scanManager.get_scan_update()
	gc.collect()
	return json.dumps(jsonData)

@app.route('/contributors')
async def contributors(request):
	with open('contributors.json', 'r') as file:
		jsonData = json.load(file)
	return json.dumps(jsonData)

@app.route('/get_config')
async def get_config(request):
	return json.dumps(configManager.configData)

@app.route('/set_config', methods=['POST'])
async def set_config(request):
	jsonData = json.loads(request.body.decode('utf-8'))
	configManager.write_config(jsonData)
	return json.dumps({"success":True})

@app.route('/flags_status')
async def flags_status(request):
	gc.collect()
	flagStatus = flagManager.get_flags_status()
	return json.dumps(flagStatus)

@app.route('/get_sensor')
async def get_sensor(request):
	gc.collect()
	sensorManager.bac_algorithm_wait()
	sensor_value = sensorManager.bac_algorithm_run()
	return json.dumps({"sensor_value": sensor_value})

@app.route('/clean_sensor')
async def clean_sensor(request):
	sensorManager.bac_algorithm_wait()
	sensor_value = sensorManager.bac_clear_readings()
	gc.collect()
	return json.dumps({"sensor_value": json.dumps(sensor_value)})

@app.route('/capture_flag/<flag>')
async def captureFlag(request, flag):
	gc.collect()
	flag_value = request.args.get('value', 'default_value')

	flag_captured = flagManager.check_flag(flag.lower(), flag_value)

	if( True == flag_captured ):
		flagManager.set_flag_status( flag.lower(), True )
		screenManager.updateFlagCount(flagManager.get_captured_flag_count())
		ledManager.siren()
	response_data = json.dumps({'captured': flag_captured})

	return response_data


# Static Routes
@app.route('/style.css')
async def style(request):
   return send_file('static/style.css', content_type='text/css')  # Specify content type

# Dynamic Routes
@app.route('/js/<path:path>')
async def js(request, path):
	if '..' in path and 'js' in path:
		# directory traversal is not allowed
		# This is example code from the microdot GitHub.
		# I make no claims that this will prevent path traversal. :)
		return 'Not found', 404
	return send_file('js/' + path)

@app.route('/static/<path:path>')
async def static(request, path):
	print(f"PATH: {path}")
	if '..' in path and 'png' in path:
		# directory traversal is not allowed
		# This is example code from the microdot GitHub.
		# I make no claims that this will prevent path traversal. :)
		return 'Not found', 404
	return send_file('images/' + path)

async def main():
	print( "Starting server" )
	await app.start_server(debug=True)
	print( "start_server returned, look for errors!" )

if __name__ == '__main__':
	try: 
		app.run(debug=True, port=configManager.configData['port'])
	except Exception as e:
            print(f"Error: {e}")