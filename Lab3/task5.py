import network
import time
import urequests as requests
from machine import Pin, PWM

# ---------- CONFIG ----------

WIFI_SSID = "Robotic WIFI"
WIFI_PASS = "rbtWIFI@2025"

BLYNK_TOKEN = "m8bgyhf0Hn71vp2hwlE8xlNmuanI0-hg"
BLYNK_API = "https://blynk.cloud/external/api"

IR_PIN = 12
SERVO_PIN = 13

# ---------- HARDWARE ----------

ir_sensor = Pin(IR_PIN, Pin.IN)
servo = PWM(Pin(SERVO_PIN), freq=50)

# ---------- WIFI ----------

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected!")

# ---------- FUNCTIONS ----------

def set_angle(angle):
    duty = int(26 + (angle / 180) * (128 - 26))
    servo.duty(duty)

def read_switch_v0():
    try:
        r = requests.get(
            f"{BLYNK_API}/get?token={BLYNK_TOKEN}&V0"
        )

        value = int(str(r.text).strip('[]"{}'))
        r.close()

        return value

    except:
        return 0      # Default to Automatic Mode

def send_mode(mode):
    try:
        r = requests.get(
            f"{BLYNK_API}/update?token={BLYNK_TOKEN}&V0={mode}"
        )
        r.close()
    except:
        pass

# ---------- INITIAL STATE ----------

CLOSED = 0
OPEN = 90

set_angle(CLOSED)

last_ir_state = 0
last_mode = -1

print("System Running...")

# ---------- MAIN ----------

while True:

    manual_mode = read_switch_v0()

    # Update Blynk label only when mode changes
    if manual_mode != last_mode:

        if manual_mode == 1:
            print("Manual Override Mode")
            send_mode("Manual")

        else:
            print("Automatic Mode")
            send_mode("Automatic")

        last_mode = manual_mode

    # AUTOMATIC MODE
    if manual_mode == 0:

        detected = 1 if ir_sensor.value() == 0 else 0

        if detected == 1 and last_ir_state == 0:

            print("Object Detected")

            set_angle(OPEN)

            time.sleep(3)

            set_angle(CLOSED)

        last_ir_state = detected

    # MANUAL MODE
    else:
        # Ignore IR sensor
        pass

    time.sleep(0.1)