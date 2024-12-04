import machine
import neopixel
import time
import math

# Configure the GPIO pin and number of pixels
PIN = 21  # GPIO pin connected to the NeoPixel strip (change to your desired pin)
NUM_PIXELS = 1  # Number of NeoPixel LEDs

# Set up NeoPixel object
np = neopixel.NeoPixel(machine.Pin(PIN), NUM_PIXELS)

# Function to create a smooth rainbow effect
def smooth_rainbow():
    # Create smooth color transitions using HSL color space
    for hue in range(0, 360, 1):  # Loop through hues (0-360)
        for i in range(NUM_PIXELS):
            # Calculate the RGB value for this hue
            color = hsl_to_rgb(hue + (i * 360 // NUM_PIXELS), 1.0, 0.5)
            np[i] = color
        np.write()  # Update the NeoPixel strip
        time.sleep(0.01)  # Adjust for smoothness, lower time for faster transition
        
    np[0] = (0,0,0)
    np.write()

# Function to convert HSL to RGB
def hsl_to_rgb(h, s, l):
    # Convert HSL to RGB (values are normalized 0-1)
    h = h / 360.0
    s = s / 1.0
    l = l / 1.0
    r, g, b = hsl_to_rgb_conversion(h, s, l)
    # Convert RGB to 8-bit values (0-255)
    return (int(r * 255), int(g * 255), int(b * 255))

# Function to convert HSL to RGB
def hsl_to_rgb_conversion(h, s, l):
    if s == 0:
        return (l, l, l)
    else:
        if l < 0.5:
            temp2 = l * (1 + s)
        else:
            temp2 = (l + s) - (l * s)
        temp1 = 2 * l - temp2
        r = hue_to_rgb(temp1, temp2, h + 1/3)
        g = hue_to_rgb(temp1, temp2, h)
        b = hue_to_rgb(temp1, temp2, h - 1/3)
        return (r, g, b)

# Helper function for RGB calculation
def hue_to_rgb(t1, t2, t3):
    if t3 < 0:
        t3 += 1
    if t3 > 1:
        t3 -= 1
    if t3 < 1/6:
        return t1 + (t2 - t1) * 6 * t3
    if t3 < 1/2:
        return t2
    if t3 < 2/3:
        return t1 + (t2 - t1) * (2/3 - t3) * 6
    return t1


if __name__ == "__main__":
    # Main loop to run the smooth rainbow effect
    smooth_rainbow()
#     while True:
#         smooth_rainbow()  # Run the smooth rainbow transition


