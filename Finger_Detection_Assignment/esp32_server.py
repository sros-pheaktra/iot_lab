import network
import socket
from machine import Pin

SSID     = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

led = Pin(2, Pin.OUT)
led.off()

# ── WiFi ────────────────────────────────────────────────────────────────────
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("Connecting to WiFi", end="")
while not wifi.isconnected():
    print(".", end="")
print()
print("ESP32 IP:", wifi.ifconfig()[0])

# ── HTTP server ──────────────────────────────────────────────────────────────
addr   = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(addr)
server.listen(5)
print("HTTP server listening on port 80 …")

def send_response(client, status="200 OK", body="OK"):
    response = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/plain\r\n"
        "Connection: close\r\n"
        f"Content-Length: {len(body)}\r\n"
        "\r\n"
        f"{body}"
    )
    client.sendall(response.encode())

while True:
    try:
        client, addr = server.accept()
        request = client.recv(1024).decode("utf-8", "ignore")

        # Extract the request line, e.g. "GET /led/on HTTP/1.1"
        first_line = request.split("\r\n")[0] if request else ""
        print("Request:", first_line)

        if "/led/on" in first_line:
            led.on()
            print("LED → ON")
            send_response(client, body="LED ON")

        elif "/led/off" in first_line:
            led.off()
            print("LED → OFF")
            send_response(client, body="LED OFF")

        else:
            send_response(client, status="404 Not Found", body="Unknown command")

        client.close()

    except Exception as e:
        print("Error:", e)
