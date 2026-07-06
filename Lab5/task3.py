from machine import Pin, I2C
import time
import neopixel
import tcs34725

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
sensor = tcs34725.TCS34725(i2c)

led = neopixel.NeoPixel(Pin(23), 32)

print("Place object in front of sensor")

while True:

    r, g, b, c = sensor.read_raw()

    print("R:", r, "G:", g, "B:", b)

    if r > g and r > b:
        color = "RED"
        rgb = (255, 0, 0)

    elif g > r and g > b:
        color = "GREEN"
        rgb = (0, 255, 0)

    elif b > r and b > g:
        color = "BLUE"
        rgb = (0, 0, 255)

    else:
        color = "UNKNOWN"
        rgb = (0, 0, 0)

    # Set all 16 LEDs
    for i in range(len(led)): 
        led[i] = rgb

    led.write()

    print("Detected Color:", color)
    time.sleep(1)
