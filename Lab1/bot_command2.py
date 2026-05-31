import network
import urequests
import time
from machine import Pin
import dht

# ---------- WIFI ----------
SSID = "YOUR_WIFI_NAME"
PASSWORD = "YOUR_WIFI_PASSWORD"

# ---------- TELEGRAM ----------
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

URL_SEND = "https://api.telegram.org/bot{}/sendMessage".format(BOT_TOKEN)
URL_GET = "https://api.telegram.org/bot{}/getUpdates".format(BOT_TOKEN)

# ---------- SENSOR ----------
sensor = dht.DHT11(Pin(33))

# ---------- RELAY ----------
relay = Pin(15, Pin.OUT)
relay.value(0)

# ---------- VARIABLES ----------
TEMP_LIMIT = 30

relay_state = False
alert_enabled = True
auto_off_sent = False

last_update_id = 0
last_loop_time = 0

# ---------- WIFI ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("Connecting to WiFi...")

while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected")

# ---------- TELEGRAM SEND ----------
def send_msg(text):
    try:
        urequests.post(URL_SEND, json={
            "chat_id": CHAT_ID,
            "text": text
        })
    except:
        print("Send failed")

# ---------- CHECK COMMAND (/on) ----------
def check_telegram():
    global relay_state, alert_enabled, last_update_id

    try:
        res = urequests.get(URL_GET)
        data = res.json()

        for item in data["result"]:
            update_id = item["update_id"]

            if update_id <= last_update_id:
                continue

            last_update_id = update_id

            if "message" in item:
                msg = item["message"]["text"]

                if msg == "/on":
                    relay.value(1)
                    relay_state = True
                    alert_enabled = False
                    send_msg("Relay ON. Alerts stopped.")

        res.close()

    except:
        pass

# ---------- MAIN LOOP ----------
while True:

    check_telegram()

    # run every 5 seconds
    if time.ticks_ms() - last_loop_time >= 5000:
        last_loop_time = time.ticks_ms()

        try:
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()

            print("Temp:", temp, "Hum:", hum)

            # --------------------------
            # CASE 1: T < 30
            # --------------------------
            if temp < TEMP_LIMIT:
                relay.value(0)
                relay_state = False
                alert_enabled = True

                if not auto_off_sent:
                    send_msg("Auto-OFF: temperature dropped below 30C")
                    auto_off_sent = True

            # --------------------------
            # CASE 2: T >= 30
            # --------------------------
            else:
                auto_off_sent = False

                if not relay_state and alert_enabled:
                    send_msg("Alert: temperature is high: {}C".format(temp))

        except:
            print("Sensor error")
