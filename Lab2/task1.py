import network
import socket
from machine import Pin
import time

# ==============================
# LED SETUP
# ==============================
led = Pin(2, Pin.OUT)
led.off()
led_state = False  # False = OFF, True = ON

# ==============================
# WIFI SETUP (Station Mode)
# ==============================
ssid = "Robotic WIFI"
password = "rbtWIFI@2025"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

ip = wifi.ifconfig()[0]
print("Connected!")
print("ESP32 IP address:", ip)

# ==============================
# WEB SERVER SETUP
# ==============================
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Web server running...")

# ==============================
# HTML PAGE WITH LED STATUS
# ==============================
def web_page(state):
    if state:
        color = "green"
        status = "LED is ON"
    else:
        color = "red"
        status = "LED is OFF"

    html = f"""
    <html>
<head>
    <title>ESP32 LED Control</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }}

        body {{
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #0f172a, #1e293b);
        }}

        .container {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            text-align: center;
            width: 350px;
        }}

        h1 {{
            color: #1e293b;
            margin-bottom: 25px;
        }}

        .circle {{
            width: 100px;
            height: 100px;
            background-color: {color};
            border-radius: 50%;
            margin: 20px auto;
            box-shadow: 0 0 25px {color};
            border: 4px solid #e5e7eb;
        }}

        h2 {{
            margin-bottom: 25px;
            color: #475569;
        }}

        .buttons {{
            display: flex;
            justify-content: center;
            gap: 15px;
        }}

        button {{
            width: 120px;
            height: 50px;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
            color: white;
        }}

        .on-btn {{
            background: #22c55e;
        }}

        .on-btn:hover {{
            background: #16a34a;
            transform: translateY(-2px);
        }}

        .off-btn {{
            background: #ef4444;
        }}

        .off-btn:hover {{
            background: #dc2626;
            transform: translateY(-2px);
        }}

        a {{
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP32 LED Control</h1>

        <div class="circle"></div>

        <h2>{status}</h2>

        <div class="buttons">
            <a href="/on">
                <button class="on-btn">ON</button>
            </a>

            <a href="/off">
                <button class="off-btn">OFF</button>
            </a>
        </div>
    </div>
</body>
</html>
    """
    return html

# ==============================
# MAIN LOOP
# ==============================
while True:
    conn, addr = s.accept()
    request = conn.recv(1024).decode()

    print("Request:", request)

    if "/on" in request:
        led.on()
        led_state = True
        print("LED ON")

    if "/off" in request:
        led.off()
        led_state = False
        print("LED OFF")

    response = web_page(led_state)
    conn.send("HTTP/1.1 200 OK\n")
    conn.send("Content-Type: text/html\n")
    conn.send("Connection: close\n\n")
    conn.sendall(response)
    conn.close()


