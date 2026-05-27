# Lab 1 : Temperature Sensor with Relay Control (Telegram)
This project uses an ESP32 to measure temperature and humidity with a DHT11 sensor and operate a relay module through Telegram commands.

### Equipment and Wiring
- ESP32 Dev Board (MicroPython firmware flashed)
- DHT11 sensor
- Relay module
- jumper wires
- USB cable + laptop with Thonny
- Wi-Fi access (internet)
#### Wiring Connection
<img width="1105" height="802" alt="Screenshot 2026-05-25 142810" src="https://github.com/user-attachments/assets/3879ec1e-c1a7-4a96-a022-ef3b7f8c9196" />

#### DHT11 → ESP32
| DHT11 Pin | ESP32 Pin |
|----------|-----------|
| VCC (+) | VCC/3V3 |
| DATA (I/O) | GPIO 4 (D4) |
| GND (-) | GND |

#### Relay Module → ESP32
| Relay Pin | ESP32 Pin |
|----------|-----------|
| VCC | VCC/5V (VIN) |
| GND | GND |
| IN | GPIO 2 (D2)|

### Configuration Steps
#### 1. Telegram Bot Setup:
- Create your own telegram bot using @BotFather
- Get the generated Bot Token 
- Add your bot into your telegram group
- Get your group Chat ID

#### 2. Code Configuration:
##### Update the information into the code:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
```
```python
relay = Pin(2, Pin.OUT)
relay.value(0)

# -------- DHT SENSOR --------
sensor = dht.DHT11(Pin(4))
```

#### 3. Wi-Fi Credentials
```python
SSID = "YOUR_WIFI_NAME"
PASSWORD = "YOUR_WIFI_PASSWORD"
```
#### How to Use: 
- Power the ESP32
- Connect ESP32 to Wi-Fi
- Connect ESP32 to telegram
- Use the following commands:
1. /status : to show temperature, humidity, and relay status
2. /on : to turn the relay on
3. /off : to turn the relay off
# Tasks & Checkpoints
### Task 1-Sensor Read & Print
- Read DHT11 every 5 seconds and print the temperature and humidity with 2
decimals.
- Evidence: serial screenshot.
<img width="991" height="769" alt="image" src="https://github.com/user-attachments/assets/5955689a-ebb8-4083-8749-237051044e82" />
<img width="1285" height="1355" alt="Screenshot 2026-05-27 140242" src="https://github.com/user-attachments/assets/d5ebe11f-4ae3-4b23-9eb0-0b90371bc6c2" />

### Task 2-Telegram Send
- Implement send_message() and post a test message to your group.
- Evidence: chat screenshot.
<img width="1788" height="274" alt="image" src="https://github.com/user-attachments/assets/ba6c354f-2247-4cfe-8fc8-2d86ab04da13" />

### Task 3-Bot Command
- Implement /status to reply with current T/H and relay state.
- Implement /on and /off to control the relay.
- Evidence: chat screenshot showing all three commands working.
<img width="1280" height="677" alt="image" src="https://github.com/user-attachments/assets/ccaabe68-29b1-45d6-8ad6-636a808ef212" />


### Task 4-Bot Command
- No messages while T < 30 °C.
- If T ≥ 30 °C and relay is OFF, send an alert every loop (5 s) until /on is
received.
- After /on, stop alerts. When T < 30 °C, turn relay OFF automatically and senda one-time “auto-OFF” notice.
- Evidence: short video (60–90s) demonstrating above behavior https://youtu.be/eMreX57w4FE
#### Flowchart 
<img width="3148" height="4608" alt="image" src="https://github.com/user-attachments/assets/51a4a24c-8b27-43db-abdd-489e8a91ac2b" />


### Task 5-Robustness
- Auto-reconnect Wi-Fi when dropped.
- Handle Telegram HTTP errors (print status; skip this cycle on failure).
- Avoid crashing on DHT OSError (skip cycle).
<img width="1105" height="802" alt="Screenshot 2026-05-25 142810" src="https://github.com/user-attachments/assets/6e8aa279-f3d4-4b6d-b100-182cc5cc303f" />

