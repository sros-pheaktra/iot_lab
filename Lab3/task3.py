import network
import time
import urequests as requests
from machine import Pin, PWM

# ---------- CONFIG ----------

WIFI_SSID = "Robotic WIFI"
WIFI_PASS = "rbtWIFI@2025"

BLYNK_TOKEN = "3UaqaXXzNjXWY50-VzgKZU4YATL5ZDQT"
BLYNK_API = "https://blynk.cloud/external/api"

SERVO_PIN = 14
IR_PIN = 12

# ---------- HARDWARE ----------

servo = PWM(Pin(SERVO_PIN), freq=50)
ir_sensor = Pin(IR_PIN, Pin.IN)

# ---------- WIFI ----------

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected!")

# ---------- SERVO ----------

def set_angle(angle):
    duty = int(26 + (angle / 180) * (128 - 26))
    servo.duty(duty)

# ---------- BLYNK ----------

def send_ir(status):
    try:
        requests.get(f"{BLYNK_API}/update?token={BLYNK_TOKEN}&V0={status}").close()
    except:
        pass

def send_servo(angle):
    try:
        requests.get(f"{BLYNK_API}/update?token={BLYNK_TOKEN}&V2={angle}").close()
    except:
        pass

# ---------- STATES ----------

CLOSED = 0
OPEN = 90

set_angle(CLOSED)

last_state = 0   # 0 = no object, 1 = object detected

print("Running IR Automatic Servo System...")

# ---------- MAIN LOOP ----------

while True:

    detected = 1 if ir_sensor.value() == 0 else 0

    # Update Blynk label
    send_ir("Detected" if detected else "Not Detected")

    # ONLY trigger when new detection happens
    if detected == 1 and last_state == 0:

        print("Object detected → OPEN")
        set_angle(OPEN)
        send_servo(OPEN)

        time.sleep(1)

        print("Closing servo")
        set_angle(CLOSED)
        send_servo(CLOSED)

    last_state = detected

    time.sleep(0.1)