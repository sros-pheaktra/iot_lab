from machine import Pin, PWM, I2C
import network
import socket
import neopixel
import tcs34725

# =============================
# WiFi
# =============================
ssid = "WIFI name "
password = "WIFI Password"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting", end="")
while not wifi.isconnected():
    pass

print("\nConnected!")
print("ESP32 IP:", wifi.ifconfig()[0])

# =============================
# Color Sensor
# =============================
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
sensor = tcs34725.TCS34725(i2c)

current_color = "UNKNOWN"

# =============================
# NeoPixel
# =============================
led = neopixel.NeoPixel(Pin(23), 32)

# =============================
# Motor
# =============================
IN1 = Pin(27, Pin.OUT)
IN2 = Pin(26, Pin.OUT)

ENA = PWM(Pin(14))
ENA.freq(1000)

def forward():
    IN1.value(1)
    IN2.value(0)
    ENA.duty(700)
    print("FORWARD")

def backward():
    IN1.value(0)
    IN2.value(1)
    ENA.duty(700)
    print("BACKWARD")

def stop():
    IN1.value(0)
    IN2.value(0)
    ENA.duty(0)
    print("STOP")

def set_speed(value):
    ENA.duty(int(value))
    print("Speed:", value)

# =============================
# Web Server
# =============================
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(5)

print("Server running on", addr)

while True:

    # Update detected color
    r, g, b, c = sensor.read_raw()

    if r > g and r > b:
        current_color = "RED"

    elif g > r and g > b:
        current_color = "GREEN"

    elif b > r and b > g:
        current_color = "BLUE"

    else:
        current_color = "UNKNOWN"

    # Wait for App request
    client, addr = server.accept()
    print("Client:", addr)

    request = client.recv(1024).decode()
    print(request)

    if "GET /forward" in request:
        forward()
        response = "Forward"

    elif "GET /backward" in request:
        backward()
        response = "Backward"

    elif "GET /stop" in request:
        stop()
        response = "Stop"

    elif "GET /speed" in request:
        try:
            value = request.split("value=")[1].split(" ")[0]
            set_speed(value)
            response = "Speed Updated"
        except:
            response = "Invalid Speed"

    elif "GET /color" in request:
        response = current_color

    elif "GET /rgb" in request:
        try:
            r = int(request.split("r=")[1].split("&")[0])
            g = int(request.split("g=")[1].split("&")[0])
            b = int(request.split("b=")[1].split(" ")[0])

            # Limit values to 0-255
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            for i in range(len(led)):
                led[i] = (r, g, b)

            led.write()

            response = "RGB: {}, {}, {}".format(r, g, b)

        except:
            response = "Invalid RGB"

    else:
        response = "Invalid Command"

    client.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n")
    client.send(response)
    client.close()
