import ujson
from umqtt.simple import MQTTClient

class MQTTHandler:
    def __init__(self, host, port, sensor):
        self.__host = host
        self.__port = port
        self.__sensor = sensor
        self.__client = None
        
    # Connect to MQTT broker
    def connect(self):
        self.__client = MQTTClient(self.__sensor, self.__host, port=self.__port)
        try:
            self.__client.connect()
            print(f"Sensor with mac:{self.__sensor} connected to MQTT broker")
        except Exception as e:
            print("Connection to MQTT Failed")
            import sys
            sys.exit()
            
    # Publish sensor data
    def publish(self, data, topic):
        print(''*100, end='\r')
        # Convert the data to JSON format
        message = ujson.dumps(data)
        try:
            # Publish the message to the broker
            self.__client.publish(topic, message)
            print(f"Published:{message}" end="\r")
        except Exception as e:
            print(e)
            
    def disconnect(self):
        self.__client.disconnect()

