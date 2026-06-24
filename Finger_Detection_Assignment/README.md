# Finger-Controlled LED via ESP32

Control an ESP32's onboard LED using hand gestures detected by your webcam — no buttons, no apps, just your fingers.

Show **1 finger** → LED turns **ON**  
Show **2 fingers** → LED turns **OFF**

---

## How it works

```
Webcam stream
     │
     ▼
PC (OpenCV + MediaPipe)
  detects finger count
     │
     │  HTTP GET /led/on
     │  HTTP GET /led/off
     ▼
ESP32 (MicroPython HTTP server)
  controls GPIO Pin 2 (onboard LED)
```

The PC script reads a camera stream, counts raised fingers using MediaPipe's hand landmark model, and sends a plain HTTP request to the ESP32 whenever the count changes. The ESP32 runs a lightweight web server that listens for those requests and toggles the LED accordingly.

---

## Requirements

### ESP32
- MicroPython firmware flashed
- Connected to the same WiFi network as your PC

### PC
- Python 3.8+
- OpenCV and MediaPipe

Install dependencies:

```bash
pip install opencv-python mediapipe
```

---

## Project structure

```
├── esp32_server.py       # MicroPython — runs on the ESP32
├── pc_finger_control.py  # Python — runs on your PC
└── README.md
```

---

## Setup

### 1. Flash the ESP32

Open `esp32_server.py` and set your WiFi credentials:

```python
SSID     = "Your WiFi Name"
PASSWORD = "Your WiFi Password"
```

Upload the file to your ESP32 as `main.py` using Thonny, ampy, or mpremote:

```bash
mpremote cp esp32_server.py :main.py
```

Reset the board and open the serial monitor. You'll see the ESP32's assigned IP address:

```
ESP32 IP: 10.30.0.xx
HTTP server listening on port 80 …
```

### 2. Configure the PC script

Open `pc_finger_control.py` and update the ESP32 IP:

```python
ESP32_IP = "10.30.0.xx"   # ← paste the IP from the serial monitor
```

If your camera stream is not coming from the ESP32-CAM, update `STREAM_URL` to point to your actual stream, or pass `0` to use a local webcam:

```python
STREAM_URL = 0   # local webcam
# or
STREAM_URL = "http://10.30.0.xx:81/stream"   # ESP32-CAM stream
```

### 3. Run

```bash
python pc_finger_control.py
```

A window opens showing the camera feed with hand landmarks drawn. The current LED state is displayed in the bottom-left corner.

Press `q` to quit.

---

## Gesture reference

| Gesture | Action | HTTP request sent |
|---|---|---|
| ☝️ 1 finger raised | LED ON | `GET /led/on` |
| ✌️ 2 fingers raised | LED OFF | `GET /led/off` |
| Anything else | No action | — |

Commands are debounced — the ESP32 only receives a request when the finger count *changes*, not on every frame.

---

## ESP32 HTTP endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/led/on` | GET | Turns the onboard LED on |
| `/led/off` | GET | Turns the onboard LED off |

Both endpoints return a plain-text response (`LED ON` or `LED OFF`) and HTTP 200. Unknown paths return HTTP 404.

---

## Troubleshooting

**ESP32 not connecting to WiFi**  
Double-check `SSID` and `PASSWORD` in `esp32_server.py`. Make sure the network is 2.4 GHz — ESP32 does not support 5 GHz.

**PC can't reach the ESP32**  
Confirm both devices are on the same network. Try `ping <ESP32_IP>` from your terminal. If the ping fails, check your router's client list to find the correct IP.

**Camera stream not opening**  
If using an ESP32-CAM, make sure the camera stream is running (`/stream` endpoint on port 81). For a local webcam, set `STREAM_URL = 0`.

**Hand not detected**  
Ensure your hand is well-lit and fully visible. MediaPipe requires a minimum detection confidence of 0.5 by default — you can lower `min_detection_confidence` in the script if needed.

**LED doesn't respond but HTTP works**  
The onboard LED on most ESP32 boards is active-low on some variants. If `led.on()` turns it off and vice versa, swap the calls in `esp32_server.py`.

---

## Built with

- [MediaPipe](https://developers.google.com/mediapipe) — hand landmark detection
- [OpenCV](https://opencv.org/) — video capture and display
- [MicroPython](https://micropython.org/) — ESP32 firmware