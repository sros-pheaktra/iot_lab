from machine import Pin, time_pulse_us
import time
import network
import socket
import dht



# Pin configuration
TRIG = Pin(27, Pin.OUT)
ECHO = Pin(26, Pin.IN)
dht_sensor = dht.DHT11(Pin(33))  # GPIO 4

SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

ip = wifi.ifconfig()[0]
print("Connected!")
print("ESP32 IP address:", ip)

def webpage(temp, distance):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 Sensor Monitor</title>

        <meta http-equiv="refresh" content="2">

        <style>
            body {{
                font-family: Arial;
                background: #0f172a;
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}

            .container {{
                background: #1e293b;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                width: 320px;
            }}

            h1 {{
                margin-bottom: 20px;
            }}

            .card {{
                background: #334155;
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
            }}

            .value {{
                font-size: 28px;
                font-weight: bold;
                color: #22c55e;
            }}
        </style>
    </head>

    <body>
        <div class="container">
            <h1>ESP32 Sensors</h1>

            <div class="card">
                <h3>Temperature</h3>
                <div class="value">{temp} °C</div>
            </div>

            <div class="card">
                <h3>Distance</h3>
                <div class="value">{distance} cm</div>
            </div>
        </div>
    </body>
    </html>
    """
    return html
# ==============================
# WEB SERVER SETUP
# ==============================
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Web server running...")
def get_distance_cm():
    # Ensure trigger is LOW
    TRIG.value(0)
    time.sleep_us(2)

    # Send 10µs pulse
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)

    # Measure echo pulse duration
    duration = time_pulse_us(ECHO, 1, 30000)  # timeout = 30ms

    # Check for timeout
    if duration < 0:
        return None

    # Distance calculation (cm)
    distance = (duration * 0.0343) / 2
    return distance

def get_temp():
    try:
        dht_sensor.measure()
        return dht_sensor.temperature()
    except Exception as e:
        print("DHT Error:", e)
        return "N/A"

while True:
    try:
        conn, addr = s.accept()
        print("Client connected:", addr)

        request = conn.recv(1024)
        print("Request received")

        # Read sensors
        distance = get_distance_cm()

        if distance is None:
            distance = "Out of range"
        else:
            distance = round(distance, 2)

        temp = get_temp()  # Replace with actual temperature sensor reading

        # Generate webpage
        response = webpage(temp, distance)

        # Send HTTP response
        conn.send("HTTP/1.1 200 OK\r\n")
        conn.send("Content-Type: text/html\r\n")
        conn.send("Connection: close\r\n\r\n")
        conn.send(response)

        conn.close()

    except Exception as e:
        print("Error:", e)
        try:
            conn.close()
        except:
            pass


