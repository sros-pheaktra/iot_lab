import network
import time
import urequests as requests
from machine import Pin
from tm1637 import TM1637

# ---------- CONFIG ----------

WIFI_SSID = "Robotic WIFI"
WIFI_PASS = "rbtWIFI@2025"

BLYNK_TOKEN = "hwEsEMpsZSgZrKSedgngVIv_Oq1usv2j"
BLYNK_API = "https://blynk.cloud/external/api"

IR_PIN = 12

# ---------- HARDWARE ----------

ir_sensor = Pin(IR_PIN, Pin.IN)

tm = TM1637(clk_pin=17, dio_pin=16, brightness=5)
# ---------- WIFI ----------

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected!")

# ---------- BLYNK ----------

def send_count(count):
    try:
        r = requests.get(
            f"{BLYNK_API}/update?token={BLYNK_TOKEN}&V1={count}"
        )
        r.close()
    except:
        print("Failed to update Blynk")

# ---------- INITIAL STATE ----------

count = 0
last_state = 0

tm.show_number(count)
send_count(count)

print("IR Counter Running...")

# ---------- MAIN ----------

while True:

    # Most IR modules output LOW when detecting an object
    detected = 1 if ir_sensor.value() == 0 else 0

    # Count only new detection events
    if detected == 1 and last_state == 0:

        count += 1

        print("Detection Count:", count)

        # Update TM1637
        tm.show_number(count)

        # Update Blynk Numeric Display
        send_count(count)

    last_state = detected

    time.sleep(0.1)