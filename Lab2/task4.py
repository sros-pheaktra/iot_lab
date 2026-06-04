from machine import Pin, SoftI2C
from machine_i2c_lcd import I2cLcd
from time import sleep
import network
import socket

# =====================
# WiFi Configuration
# =====================

SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("Connecting to WiFi...")

while not wifi.isconnected():
    sleep(1)

ip = wifi.ifconfig()[0]

print("Connected!")
print("IP Address:", ip)

# =====================
# LCD Configuration
# =====================

I2C_ADDR = 0x27

i2c = SoftI2C(
    sda=Pin(21),
    scl=Pin(22),
    freq=400000
)

lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

lcd.clear()
lcd.putstr("LCD Ready")

# =====================
# Web Page
# =====================

def webpage():
    return """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 LCD Control</title>

    <style>
        *{
            margin:0;
            padding:0;
            box-sizing:border-box;
            font-family:Arial, Helvetica, sans-serif;
        }

        body{
            min-height:100vh;
            display:flex;
            justify-content:center;
            align-items:center;
            background:linear-gradient(135deg,#0f172a,#1e3a8a);
            padding:20px;
        }

        .container{
            background:white;
            padding:30px;
            border-radius:16px;
            box-shadow:0 10px 30px rgba(0,0,0,0.2);
            width:100%;
            max-width:500px;
            text-align:center;
        }

        h1{
            margin-bottom:20px;
            color:#1e3a8a;
        }

        form{
            display:flex;
            gap:12px;
        }

        input{
            flex:1;
            padding:14px;
            border:2px solid #dbeafe;
            border-radius:10px;
            font-size:16px;
        }

        button{
            padding:14px 24px;
            border:none;
            border-radius:10px;
            background:#2563eb;
            color:white;
            font-size:16px;
            cursor:pointer;
        }

        button:hover{
            background:#1d4ed8;
        }
    </style>
</head>

<body>

<div class="container">
    <h1>ESP32 LCD Control</h1>

    <form action="/send" method="GET">
        <input
            type="text"
            name="msg"
            maxlength="64"
            placeholder="Enter text for LCD">

        <button type="submit">Send</button>
    </form>
</div>

</body>
</html>
"""

# =====================
# LCD Display Function
# =====================

def display_lcd(text):

    lcd.clear()

    # If text fits on LCD, display permanently
    if len(text) <= 16:
        lcd.putstr(text)
        return

    # Scroll only if text is longer than 16 chars
    scroll_text = text + "    "

    for i in range(len(scroll_text)):
        lcd.clear()
        lcd.putstr(scroll_text[i:i+16])
        sleep(0.4)
# =====================
# Web Server
# =====================

addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

server = socket.socket()
server.bind(addr)
server.listen(1)

print("Server running")
print("Open:", "http://" + ip)

while True:

    client, address = server.accept()

    request = client.recv(1024).decode()

    print(request)

    if "/send?msg=" in request:

        start = request.find("/send?msg=") + len("/send?msg=")
        end = request.find(" HTTP")

        message = request[start:end]

        message = message.replace("%20", " ")
        message = message.replace("%27", " ")
        message = message.replace("+", " ")

        print("LCD:", message)

        display_lcd(message)

    response = webpage()

    client.send("HTTP/1.1 200 OK\r\n")
    client.send("Content-Type: text/html\r\n")
    client.send("Connection: close\r\n\r\n")
    client.sendall(response)

    client.close()
