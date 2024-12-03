from wifi_handler import WIFI_Handler
from machine import Pin, I2C
from credentials import SSID, PASSWORD
from rainbow import smooth_rainbow


i2c = I2C(1, scl=Pin(34), sda=Pin(33), freq=100000)

wifi = WIFI_Handler(SSID, PASSWORD)

print("\nInitialising...")
smooth_rainbow()
devices = i2c.scan()
if devices:
    print("I2C devices found:", [hex(device) for device in devices], f"on {i2c}")
    wifi.connect()
else :
    print(f"No Devices Found! on {i2c}")
    import sys
    sys.exit()
