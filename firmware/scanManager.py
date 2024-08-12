import json
import random
import rp2
import time
import ubinascii
import constants

class ScanManager:
    def __init__(self, wlan, flagManager):
        self.uncaptured_ap_length = 0
        self.targetAp = None
        self.flagManager = flagManager
        self.apData = None
        self.get_ap_data()
        self.total_aps = len(self.apData) 
        self.wlan = wlan # May move this to network manager
        rp2.country('US') 

    def get_ap_data(self):
        with open('apConfig.json', 'r') as file:
            self.apData = json.load(file)        

    def update_ap_status(self, ap_name):
        with open('apConfig.json', 'r') as file:
            jsonData = json.load(file)   
        jsonData[ap_name] = True
        with open('apConfig.json', 'w') as file:
            json.dump(jsonData,file)

    def get_ap_name(self):
        self.get_ap_data()
        uncaptured_aps = [ap for ap, status in self.apData.items() if not status]
        self.uncaptured_ap_length = len(uncaptured_aps)
        if( self.uncaptured_ap_length == 0 ):
            # Return the flag
            responseText = self.flagManager.retrieve_flag('respond')
        else:
            # Pick a Random AP
            self.targetAp = uncaptured_aps[random.randint(0, self.uncaptured_ap_length-1)]
            responseText = f"Beginning Scanning Procedure for {self.targetAp}. You have 10 minutes..." 
        return responseText
    
    def get_scan_update(self):
        scanning = True
        scanCount = constants.SCAN_COUNT

        responseText = f"Scanning for {self.targetAp}"
        statusValue = False
        while(scanning and scanCount > 0):
            accessPoints = self.wlan.scan() # list with tuples (ssid, bssid, channel, RSSI, security, hidden)
            for ap in accessPoints: #this loop prints each AP found in a single row on shell
                ssid = ap[0].decode()
                bssid =  ubinascii.hexlify(ap[1],":").decode()
                ch = ap[2]
                rssi = ap[3]
                auth = hex(ap[4])
                vis = hex(ap[5])
                print("{:30s} | {:s} | {:2d} | {:3d} | {:s} | {:s}".format(ssid, bssid, ch, rssi, auth, vis))
                if( ssid == self.targetAp ):                
                    if( self.total_aps-self.uncaptured_ap_length+1 == self.total_aps ):
                        flag = self.flagManager.retrieve_flag('respond')
                        responseText = f"Successfully responded to all! {flag}"
                        statusValue = True
                    else:
                        self.update_ap_status(self.targetAp)
                        responseText = f"Response in Time! Responded to {self.total_aps-self.uncaptured_ap_length+1} of {self.total_aps}"
                        statusValue = True
                    scanning = False
            scanCount = scanCount - 1
            time.sleep(0.25)

        return { 'update': responseText, 'status': statusValue }