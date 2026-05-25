
import network
import urequests
import time
from machine import Pin
import dht

# -------- SETTINGS --------
SSID = "WIFI NAME"
PASSWORD = "Password"

BOT_TOKEN = "Bot_Token"
CHAT_ID = "Chat_ID"



# -------- WIFI --------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected")

# -------- TELEGRAM --------
URL_SEND = "https://api.telegram.org/bot{}/sendMessage".format(BOT_TOKEN)

# -------- MAIN LOOP --------
def send_message(message):
    urequests.post(URL_SEND, json={
        "chat_id": CHAT_ID,
        "text": message
    })
    print("Sent:", message)
while True:
    try:
        a = "HELLO SCAMMERs"
        send_message(a)
        
    except Exception as e:
        print(f"{e}")
    time.sleep(2)

