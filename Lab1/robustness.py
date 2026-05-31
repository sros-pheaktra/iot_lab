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

# ---------- WIFI SETUP ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

def connect_wifi():
    if not wifi.isconnected():
        print("Reconnecting WiFi...")
        wifi.connect(SSID, PASSWORD)

        timeout = 10
        while not wifi.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

        if wifi.isconnected():
            print("WiFi reconnected")
        else:
            print("WiFi reconnect failed")

connect_wifi()

# ---------- TELEGRAM SEND (SAFE) ----------
def send_msg(text):
    try:
        res = urequests.post(URL_SEND, json={
            "chat_id": CHAT_ID,
            "text": text
        })

        # check HTTP status
        print("Telegram status:", res.status_code)
        res.close()

    except Exception as e:
        print("Telegram send error:", e)

# ---------- CHECK COMMANDS ----------
def check_telegram():
    global relay_state, last_update_id

    try:
        res = urequests.get(URL_GET)

        if res.status_code != 200:
            print("Telegram HTTP error:", res.status_code)
            res.close()
            return  # skip cycle

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
                    send_msg("Relay ON")

                elif msg == "/off":
                    relay.value(0)
                    relay_state = False
                    send_msg("Relay OFF")

                elif msg == "/status":
                    try:
                        sensor.measure()
                        temp = sensor.temperature()
                        hum = sensor.humidity()

                        state = "ON" if relay_state else "OFF"

                        send_msg(
                            "Status\nTemp: {}C\nHum: {}%\nRelay: {}".format(
                                temp, hum, state
                            )
                        )

                    except OSError:
                        print("DHT read failed (skipping)")
                        return

        res.close()

    except Exception as e:
        print("Telegram error:", e)

# ---------- MAIN LOOP ----------
while True:

    # WiFi auto-reconnect
    if not wifi.isconnected():
        connect_wifi()

    check_telegram()

    time.sleep(2)