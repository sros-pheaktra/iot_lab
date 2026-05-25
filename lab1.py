import network
import urequests
import time
from machine import Pin
import dht

# ---------------- WIFI ----------------
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

# ---------------- TELEGRAM ----------------
BOT_TOKEN = "8562091283:AAHikvh7zMRqWJzvzQ08-fGWoDtMoql6RRQ"
CHAT_ID = "-1003891153762"

# ---------------- SENSOR ----------------
sensor = dht.DHT11(Pin(4))

# ---------------- RELAY ----------------
relay = Pin(2, Pin.OUT)
relay.value(0)

# ---------------- VARIABLES ----------------
TEMP_THRESHOLD = 30

relay_state = False
alert_sent = False
last_update_id = 0

# ---------------- WIFI CONNECT ----------------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting WiFi...")
        wlan.connect(SSID, PASSWORD)

        while not wlan.isconnected():
            time.sleep(1)

    print("WiFi Connected")
    print(wlan.ifconfig())

# ---------------- SEND TELEGRAM ----------------
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    try:
        response = urequests.post(url, json=data)
        print("Telegram:", response.status_code)
        response.close()

    except Exception as e:
        print("Telegram Error:", e)

# ---------------- GET COMMANDS ----------------
def check_commands():
    global relay_state
    global last_update_id

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id + 1}"

    try:
        response = urequests.get(url)
        data = response.json()

        if data["ok"]:

            for result in data["result"]:

                last_update_id = result["update_id"]

                message = result["message"]["text"]

                print("Command:", message)

                if message == "/on":
                    relay.value(1)
                    relay_state = True
                    send_message("Relay ON")

                elif message == "/off":
                    relay.value(0)
                    relay_state = False
                    send_message("Relay OFF")

                elif message == "/status":

                    sensor.measure()

                    t = sensor.temperature()
                    h = sensor.humidity()

                    status = f"""
Temperature: {t:.2f} C
Humidity: {h:.2f} %
Relay: {"ON" if relay_state else "OFF"}
"""

                    send_message(status)

        response.close()

    except Exception as e:
        print("Command Error:", e)

# ---------------- MAIN ----------------
connect_wifi()

send_message("ESP32 Started")

while True:

    try:

        # reconnect wifi if disconnected
        wlan = network.WLAN(network.STA_IF)

        if not wlan.isconnected():
            connect_wifi()

        sensor.measure()

        temp = sensor.temperature()
        hum = sensor.humidity()

        print(f"Temp: {temp:.2f} C")
        print(f"Humidity: {hum:.2f} %")

        check_commands()

        # temperature alert logic
        if temp >= TEMP_THRESHOLD:

            if not relay_state:
                send_message(
                    f"WARNING!\nTemperature High: {temp:.2f} C"
                )

        else:

            if relay_state:
                relay.value(0)
                relay_state = False

                send_message("Temperature normal -> Relay AUTO OFF")

        time.sleep(5)

    except OSError as e:
        print("DHT Error:", e)
        time.sleep(5)

    except Exception as e:
        print("Main Error:", e)
        time.sleep(5)
