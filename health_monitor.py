import time
from machine import Pin, I2C
from max30102 import MAX30102
from mlx90614 import MLX90614
from utime import time
from collections import deque

class HealthMonitor:
    def __init__(self, scl=Pin(34), sda=Pin(33), freq=100000, sample_rate=400, buffer_size=512, moving_avg_window=5):
        # Initialize I2C and sensors
        self.__i2c = I2C(1, scl=scl, sda=sda, freq=freq)
        self.__max30102 = MAX30102(i2c=self.__i2c)
        self.__mlx90614 = MLX90614(self.__i2c)
        self.sample_rate = sample_rate  # Sampling frequency in Hz
        self.buffer_size = buffer_size  # Number of samples for heart rate calculation

        self.__moving_avg_window = moving_avg_window  # Window size for moving average

        self.__ir_buffer = deque([], self.buffer_size)  # Buffer to store IR values
        self.__red_buffer = deque([], self.buffer_size)  # Buffer to store Red values
        self.__temp_buffer = deque([], self.buffer_size)  # Buffer to store temperature values

        self.heart_rate = None
        self.spo2 = None
        self.temperature = None

        self.__max30102.setup_sensor()
        print("Sensors initialized successfully.")

    def get_buffer_len(self):
        return len(self.__ir_buffer)

    def __get_timestamp(self):
        # Get current timestamp
        return 946684800+time()

    def __read_temperature(self):
        # Read ambient and object temperatures from MLX90614
        try:
            ambient_temp = self.__mlx90614.ambient_temp
            object_temp = self.__mlx90614.object_temp

            self.__temp_buffer.append(object_temp)
            data = list(self.__temp_buffer)

            if len(data) < self.buffer_size:
                return None

            avg_temp = sum(data)/len(data)
            return {
                "Ambient_C": ambient_temp,
                "Object_C": avg_temp,
                "Ambient_F": ambient_temp*1.8+32,
                "Object_F" : avg_temp*1.8+32
            }

        except Exception as e:
            print("Error reading temperature:", e)
            return None

    def __calculate_spo2(self, ir_data, red_data):
        """
        Calculate SpO2 based on the AC and DC components of the IR and Red signals.
        Formula: SpO2 = 110 - 25 * (red_ac / red_dc) / (ir_ac / ir_dc)
        """
        # Calculate AC and DC components
        ir_ac = max(ir_data) - min(ir_data)
        ir_dc = sum(ir_data) / len(ir_data)
        red_ac = max(red_data) - min(red_data)
        red_dc = sum(red_data) / len(red_data)

        # Calculate the ratio and SpO2 if both DC components are non-zero
        if ir_dc > 0 and red_dc > 0:
            ror = (red_ac / red_dc) / (ir_ac / ir_dc)
            spo2 = 110 - 25 * ror  # Approximation formula
            return max(0, min(100, spo2))  # Ensure valid SpO2 range (0-100%)
        return None

    def __read_spo2(self):
        self.__max30102.check()
        if self.__max30102.available():
            # Read the red and IR light intensities from the MAX30102 sensor
            red = self.__max30102.pop_red_from_storage()
            ir = self.__max30102.pop_ir_from_storage()

            # Add the new readings to their respective buffers
            self.__red_buffer.append(red)
            self.__ir_buffer.append(ir)

            # If we have enough data, calculate SpO2
            if len(self.__ir_buffer) >= self.buffer_size:
                spo2 = self.__calculate_spo2(list(self.__ir_buffer), list(self.__red_buffer))
                return {"SpO2": spo2, "Red": red, "IR": ir}
            return None
        return None

    # Moving Average Filter
    def __moving_average(self, data):
        smoothed = []
        for i in range(len(data) - self.__moving_avg_window + 1):
            smoothed.append(sum(data[i:i+self.__moving_avg_window]) / self.__moving_avg_window)
        return smoothed

    # Peak Detection
    def __find_peaks(self, data, min_distance):
        peaks = []
        for i in range(1, len(data) - 1):
            if data[i] > data[i - 1] and data[i] > data[i + 1]:
                if len(peaks) == 0 or (i - peaks[-1]) >= min_distance:
                    peaks.append(i)
        return peaks

    def __calculate_heart_rate(self):
        """
        Detect peaks in the IR signal and calculate the heart rate.
        Heart rate is estimated based on the time difference between consecutive peaks.
        """
        self.__max30102.check()
        if self.__max30102.available():
            ir_smoothed = self.__moving_average(list(self.__ir_buffer))
            min_distance = int(self.sample_rate * 0.6)  # Minimum distance between peaks
            peaks = self.__find_peaks(ir_smoothed, min_distance)
            if len(peaks) > 1:
                intervals = [(peaks[i] - peaks[i - 1]) / self.sample_rate for i in range(1, len(peaks))]
                heart_rate = 60 / (sum(intervals) / len(intervals))  # Convert intervals to bpm
        return heart_rate

    def read_all(self):
            # Read all data and set the values in the class attributes
            try:
                self.spo2 = self.__read_spo2()
                self.temperature = self.__read_temperature()
                self.heart_rate = self.__calculate_heart_rate()
            except Exception as e:
                print("Error reading data:", e)

    def get_data(self):
        if self.heart_rate is None or self.spo2 is None or self.temperature is None:
            return None
        return {"spo2": self.spo2, "heartrate": self.heart_rate, "temperature": self.temperature, "timestamp": self.__get_timestamp()}

    def shutdown(self):
        self.__max30102.shutdown()


