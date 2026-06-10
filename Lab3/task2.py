import network
import time
import urequests as requests
from machine import Pin, PWM

# ---------- CONFIG ----------

WIFI_SSID = "Robotic WIFI"
WIFI_PASS = "rbtWIFI@2025"

BLYNK_TOKEN = "w1RzjBil5W6d5IQ3cXgHzFF8ax6SHarf"
BLYNK_API   = "https://blynk.cloud/external/api"

# ---------- SERVO ----------

servo = PWM(Pin(13), freq=50)

# ---------- WIFI ----------

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected!")

# ---------- BLYNK ----------

def read_slider_v0():
    r = requests.get(
        f"{BLYNK_API}/get?token={BLYNK_TOKEN}&V0"
    )
    value = int(str(r.text).strip('[]"{}'))
    r.close()
    return value

def set_angle(angle):
    # Convert 0-180° to duty 26-128
    duty = int(26 + (angle / 180) * (128 - 26))
    servo.duty(duty)

# ---------- MAIN ----------

print("Running Servo Control...")
last_angle = -1
while True:
    angle = read_slider_v0()

    if angle != last_angle:
        print("Servo Angle:", angle)
        set_angle(angle)
        last_angle = angle

    time.sleep(0.05)