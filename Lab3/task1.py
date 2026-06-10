import network
import time
import machine
import urequests as requests

# ---------- CONFIG ----------

WIFI_SSID = "Robotic WIFI"
WIFI_PASS = "rbtWIFI@2025"

BLYNK_TOKEN = "j-gcI6oAiD1fi1pQpgZ9Wq4yPPskiqR4"
BLYNK_API   = "https://blynk.cloud/external/api"

IR_PIN = 12

# ---------- HARDWARE ----------

ir_sensor = machine.Pin(IR_PIN, machine.Pin.IN)

# ---------- WIFI ----------

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected!")

# ---------- BLYNK ----------

def send_ir_status_v0(status):
    try:
        status = status.replace(" ", "%20")
        url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&V3={status}"
        r = requests.get(url)
        r.close()

    except Exception as e:
        print("Blynk Error:", e)

# ---------- MAIN ----------

print("Running IR Sensor Monitoring...")
while True:

    if ir_sensor.value() == 0:
        status = "Detected"
    else:
        status = "Not Detected"

    print("IR Status:", status)
    send_ir_status_v0(status)

    time.sleep(2)