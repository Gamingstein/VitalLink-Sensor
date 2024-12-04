import network
import time

class WIFI_Handler:
    def __init__(self, ssid, password, mode = network.STA_IF):
        self.ssid = ssid
        self.password = password
        self.mode = mode
        self.__wlan = network.WLAN(self.mode)
        
    def connect(self):
        self.__wlan.active(True)
        self.__wlan.connect(self.ssid, self.password)
        while not self.__wlan.isconnected():
            print("Connecting to Wi-Fi...")
            time.sleep(1)
        print("Connected to Wi-Fi:", self.__wlan.ifconfig())
    
    def disconnect(self):
        self.__wlan.active(False)
