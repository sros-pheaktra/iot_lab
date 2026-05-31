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

# ---------- STATE ----------
relay_state = False
last_update_id = 0

# ---------- WIFI ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("Connecting to WiFi...")

while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected")

# ---------- SEND MESSAGE ----------
def send_msg(text):
    try:
        urequests.post(URL_SEND, json={
            "chat_id": CHAT_ID,
            "text": text
        })
    except:
        print("Send failed")

# ---------- CHECK COMMANDS ----------
def check_telegram():
    global relay_state, last_update_id

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

                # ---------- /on ----------
                if msg == "/on":
                    relay.value(1)
                    relay_state = True
                    send_msg("Relay is ON")

                # ---------- /off ----------
                elif msg == "/off":
                    relay.value(0)
                    relay_state = False
                    send_msg("Relay is OFF")

                # ---------- /status ----------
                elif msg == "/status":
                    try:
                        sensor.measure()
                        temp = sensor.temperature()
                        hum = sensor.humidity()

                        state = "ON" if relay_state else "OFF"

                        reply = (
                            "Status Report\n"
                            "Temperature: {} C\n"
                            "Humidity: {} %\n"
                            "Relay: {}"
                        ).format(temp, hum, state)

                        send_msg(reply)

                    except:
                        send_msg("Sensor read error")

        res.close()

    except:
        pass

# ---------- MAIN LOOP ----------
while True:
    check_telegram()
    time.sleep(2)