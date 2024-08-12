import network 

class NetworkManager:
    def __init__(self, ssid, password, networkType='AP'):
        self.ip = None
        self.ssid = ssid
        self.password = password

        if( networkType == 'AP' ):
            self.wlan = network.WLAN(network.AP_IF)
            self.start_ap()
        elif( networkType == 'WIFI' ):
            self.wlan = network.WLAN(network.STA_IF)
            self.start_wifi()
    
    def start_wifi(self):
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print("Connecting to Wi-Fi...")
            print(self.wlan)
            self.wlan.connect(self.ssid, self.password)
            while not self.wlan.isconnected():
                pass
        print("Connected to Wi-Fi:", self.wlan.ifconfig())
        self.ip = self.wlan.ifconfig()[0]

    def start_ap(self):
        self.wlan.config(essid=self.ssid, password=self.password)
        self.wlan.active(True)
        
        while not self.wlan.active():
            pass
        self.ip = self.wlan.ifconfig()[0]
        print("AP Broadcasting:", self.wlan.ifconfig())
        print("SSID:", self.ssid)
        print("Password:", self.password)

    def get_ifconfig(self):
        print( self.wlan.config() )