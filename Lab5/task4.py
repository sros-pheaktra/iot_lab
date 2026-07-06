from machine import Pin, I2C, PWM
import time
import neopixel
import tcs34725

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
sensor = tcs34725.TCS34725(i2c)


# Motor direction pins
IN1 = Pin(27, Pin.OUT)
IN2 = Pin(26, Pin.OUT)

# PWM pin for speed control
ENA = PWM(Pin(14))
ENA.freq(1000)
led = neopixel.NeoPixel(Pin(23), 32)

def motor_forward(pwm):
    IN1.value(1)
    IN2.value(0)
    ENA.duty(pwm)

def motor_stop():
    IN1.value(0)
    IN2.value(0)
    ENA.duty(0)
    
print("Place object in front of sensor")

while True:

    r, g, b, c = sensor.read_raw()

    print("R:", r, "G:", g, "B:", b)

    if r > g and r > b:
        color = "RED"
        rgb = (255, 0, 0)
        pwm = 700
        motor_forward(pwm)

    elif g > r and g > b:
        color = "GREEN"
        rgb = (0, 255, 0)
        pwm = 500
        motor_forward(pwm)

    elif b > r and b > g:
        color = "BLUE"
        rgb = (0, 0, 255)
        pwm = 300
        motor_forward(pwm)

    else:
        color = "UNKNOWN"
        rgb = (0, 0, 0)
        pwm = 0
        motor_stop()

    print("Detected:", color, "PWM:", pwm)

    # Set all LEDs
    #for i in range(len(led)):
        #led[i] = rgb
    
    #Set only 1 LED
    led[0] = rgb

    led.write()

    print("Detected:", color, "PWM:", pwm)
    time.sleep(1)

