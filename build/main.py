import gc
import json
import machine
import utime as time

# Import essential modules first
from microdot import Microdot, Response, send_file
from microdot.utemplate import Template
import constants


# Initialize managers with lazy loading
class ManagerFactory:
    _instances = {}

    @staticmethod
    def get_manager(manager_type):
        if manager_type not in ManagerFactory._instances:
            if manager_type == 'helpers':
                from helpers import Helpers
                ManagerFactory._instances[manager_type] = Helpers()
            elif manager_type == 'config':
                from configManager import ConfigManager
                ManagerFactory._instances[manager_type] = ConfigManager()
            elif manager_type == 'detect':
                from detectManager import DetectManager
                ManagerFactory._instances[manager_type] = DetectManager()
            # Add other managers as needed
        return ManagerFactory._instances[manager_type]


# Essential startup configuration
device_id = ManagerFactory.get_manager('helpers').device_name
networkSetting = 'AP'
bootupTime = time.ticks_ms()

# Initialize core managers
configManager = ManagerFactory.get_manager('config')
if configManager.configData['apPassword'] == 'password':
    print("Generating Random password")
    configManager.update_config('apPassword', ManagerFactory.get_manager('helpers').generate_password(8))

# Initialize essential managers for boot sequence
detectManager = ManagerFactory.get_manager('detect')
from screenManager import ScreenManager
from ledManager import LEDManager
from sensorManager import SensorManager

screenManager = ScreenManager(f" Booting as {networkSetting}", device_id, configManager, detectManager)
ledManager = LEDManager(configManager.configData['startupColor'])
testmode = False
sensorManager = SensorManager(ledManager, screenManager)
gc.collect()

# Boot sequence
bootPin = machine.Pin(constants.INTERRUPT_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
if bootPin.value() == 0:
    testmode = True

if detectManager.read_v_usb() > 4.0 or testmode:
    print("Starting up due to External Power")
    screenManager.showConnectedScreen()
    buttonUnPressed = True

    while buttonUnPressed:
        if testmode:
            screenManager.bhvScreen()
            ledManager.prettyRainbow(60, 0.25)
        else:
            sensorManager.enable_sensor_voltage()
            sensorEnabled = True
            time.sleep_ms(250)
            screenManager.showConnectedScreen()

        if bootPin.value() == 0:
            buttonUnPressed = False
            print("Button Pressed")
            sensorManager.disable_sensor_voltage()
            sensorEnabled = False
        elif sensorEnabled and time.ticks_diff(time.ticks_ms(), bootupTime) > 300000:
            sensorManager.disable_sensor_voltage()
            sensorEnabled = False
            print("Turning Off Sensor")
    gc.collect()

# Button check sequence
buttonUnPressed = True
while buttonUnPressed:
    screenManager.bhvScreen()
    ledManager.prettyRainbow(2.5, 0.25)
    if bootPin.value() == 0:
        buttonUnPressed = False

# Initialize remaining managers only after boot sequence
from interruptManager import InterruptManager
from flagManager import FlagManager
from networkManager import NetworkManager
from scanManager import ScanManager
from gpioManager import GPIOManager
from serialManager import SerialManager

interruptManager = InterruptManager(screenManager, sensorManager, configManager)
flagManager = FlagManager(device_id)
networkManager = NetworkManager(device_id, configManager.configData['apPassword'], networkSetting)
scanManager = ScanManager(networkManager.wlan, flagManager)
gpioManager = GPIOManager()
serialManager = SerialManager()

screenManager.updateAll(device_id, flagManager.get_captured_flag_count(),
                        f"IP: {networkManager.ip}", "Badge by SolaSec")

# Initialize web server
app = Microdot()
Response.default_content_type = 'text/html'
ledManager.override_color("Green")

gc.collect()


# Route handlers (simplified for memory efficiency)
@app.route('/')
async def index(request):
    gc.collect()
    flag = flagManager.retrieve_flag('easy')
    return await Template('index.html').render_async(device_id=device_id, flag=flag)


@app.route('/get_sensor')
async def get_sensor(request):
    gc.collect()
    sensorManager.bac_algorithm_wait()
    sensor_value = sensorManager.bac_algorithm_run()
    return json.dumps({"sensor_value": sensor_value})


@app.route('/capture_flag/<flag>')
async def captureFlag(request, flag):
    gc.collect()
    flag_value = request.args.get('value', 'default_value')
    flag_captured = flagManager.check_flag(flag.lower(), flag_value)

    if flag_captured:
        flagManager.set_flag_status(flag.lower(), True)
        screenManager.updateFlagCount(flagManager.get_captured_flag_count())
        ledManager.siren()
        ledManager.override_color()
    return json.dumps({'captured': flag_captured})


# Static file handling
@app.route('/static/<path:path>')
async def static(request, path):
    if '..' in path:
        return 'Not found', 404
    return send_file('images/' + path)


# Main application
if __name__ == '__main__':
    try:
        app.run(debug=False, port=configManager.configData['port'])
    except Exception as e:
        print(f"Error: {e}")
