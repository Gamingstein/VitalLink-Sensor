import network
import ubinascii
from health_monitor import HealthMonitor
from mqtt_handler import MQTTHandler
from wifi_handler import WIFI_Handler
from credentials import SSID, PASSWORD
import time

wlan = network.WLAN(network.STA_IF)

# MQTT broker details
BROKER = "broker.hivemq.com"  # Replace with your Raspberry Pi's IP address
PORT = 1883  # Default MQTT port
TOPIC = "gamingstein/sensordata"
SENSOR_ID = ubinascii.hexlify(wlan.config("mac"),":").decode().upper()  # Unique sensor identifier

mqtt = MQTTHandler(BROKER, PORT, SENSOR_ID)
mqtt.connect()

health_monitor = HealthMonitor()

while True:
    try:
        # Read all sensor data
        health_monitor.read_all()
        print("\r", end="")
        print(f"Number of readings: {health_monitor.get_buffer_len()}", end="")
        # Only display data if heart rate calculation is ready
        if health_monitor.get_buffer_len() >= health_monitor.buffer_size:
            data = health_monitor.get_data()
            if data is not None:
                print("\n")
                payload = {
                    "timestamp": data["timestamp"],
                    "sensorData":{
                        "spo2": data["spo2"]["SpO2"],
                        "temperature": data["temperature"]["Object_F"],
                        "heartrate": data["heartrate"]
                    },
                    "sensorID": SENSOR_ID
                }
                mqtt.publish(payload, TOPIC)
                mqtt.disconnect()
                health_monitor.shutdown()
                break
                    
        # Delay to match sample rate
        time.sleep(1 / health_monitor.sample_rate)
    
    except KeyboardInterrupt:
        mqtt.disconnect()
        health_monitor.shutdown()
        print("Exiting program...")
