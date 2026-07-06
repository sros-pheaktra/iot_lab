# Smart Color Detection & Control with MIT App Inventor

# Project Overview

This project demonstrates the integration of an ESP32 with a TCS34725 color sensor, NeoPixel RGB LED, DC motor, and MIT App Inventor to perform real-time color detection, automatic device control, and manual remote operation.

The system supports:

- RGB color detection using the TCS34725 sensor
- Automatic color classification (Red, Green, Blue)
- NeoPixel color indication based on detected color
- DC motor speed control using PWM
- Real-time color monitoring through MIT App Inventor
- Manual motor control (Forward, Stop, Backward)
- Manual NeoPixel RGB control from the mobile app

---

# Hardware Components

| Component | Quantity |
| ---------- | -------- |
| ESP32 Development Board | 1 |
| TCS34725 Color Sensor | 1 |
| NeoPixel RGB LED | 1 |
| DC Motor | 1 |
| Motor Driver Module | 1 |
| Jumper Wires | Several |
| Breadboard | 1 |

---

# Hardware Setup

## Actual Hardware Setup

> Insert a clear photo of your hardware circuit.

<br>

---

# MIT App Inventor Interface

> Insert screenshots of your MIT App Inventor application below.







---

# Software Requirements

- MicroPython installed on ESP32
- Thonny IDE
- MIT App Inventor
- Wi-Fi Network

---

# Wi-Fi Configuration

Update your Wi-Fi credentials inside `main.py`:

```python
SSID = "YOUR_WIFI_NAME"
PASSWORD = "YOUR_WIFI_PASSWORD"
```

If your project communicates with the MIT App using the ESP32 IP address, note the IP displayed in the Serial Monitor after connecting to Wi-Fi.

---

# Running the Project

1. Connect the ESP32 to the TCS34725 sensor, NeoPixel LED, and motor driver.
2. Upload `main.py` to the ESP32 using Thonny.
3. Run the program.
4. Wait until the ESP32 connects to Wi-Fi.
5. Open the MIT App Inventor application.
6. Monitor the detected color or manually control the motor and NeoPixel.

---

# Task 1 – RGB Reading

## Objective

Read RGB values from the TCS34725 color sensor and display them in the Serial Monitor.

### Expected Behavior

- RGB values continuously update.
- Values change when different colored objects are placed in front of the sensor.

---

## Evidence

### Serial Monitor Screenshot

[Watch Video](images/task1.png)

---

# Task 2 – Color Classification

## Objective

Classify the detected object as Red, Green, or Blue using the RGB values.

### Classification Rules

- **R > G** and **R > B** → RED
- **G > R** and **G > B** → GREEN
- **B > R** and **B > G** → BLUE

### Expected Behavior

- The correct color name is detected and displayed.
- The detected color is sent to the MIT App.

---

## Evidence

### Demonstration Video

[Watch Video](videos/task2.mp4)

---

# Task 3 – NeoPixel Control

## Objective

Automatically change the NeoPixel LED according to the detected color.

### Expected Behavior

- RED detected → NeoPixel displays Red
- GREEN detected → NeoPixel displays Green
- BLUE detected → NeoPixel displays Blue

---

## Evidence

### Demonstration Video

[Watch Video](videos/task3.mp4)

---

# Task 4 – Motor Speed Control

## Objective

Control the DC motor speed using PWM based on the detected color.

### Expected Behavior

| Detected Color | PWM Value |
| -------------- | --------- |
| Red | 700 |
| Green | 500 |
| Blue | 300 |

The motor speed changes automatically whenever the detected color changes.

---

## Evidence

### Demonstration Video

[Watch Video](videos/task4.mp4)

---

# Task 5 – MIT App Integration

## Objective

Develop an MIT App Inventor application for monitoring and manual control.

### App Features

- Display detected color
- Forward button
- Stop button
- Backward button
- RGB input boxes
- Button to manually set NeoPixel color

### Expected Behavior

- The detected color updates in real time.
- Motor responds to Forward, Stop, and Backward commands.
- User can manually enter RGB values to change the NeoPixel color.

---

## Evidence

### MIT App Screenshot

> Insert screenshot here.

### Demonstration Video

[Watch Video](videos/task5.mp4)

---

# GitHub Repository

Repository Link:

```text
https://github.com/yourusername/your-repository
```

---

# Demonstration Video

A 60–90 second video demonstrating:

- RGB sensor reading
- Color classification
- NeoPixel color changes
- Motor speed control
- MIT App color monitoring
- Manual motor control
- Manual NeoPixel RGB control

Video Link:

```text
videos/final-demo.mp4
```

---

# Challenges Encountered

Describe any issues experienced during development and how they were solved.

Examples:

- Incorrect RGB readings due to ambient lighting
- Wi-Fi connection problems
- Motor PWM tuning
- NeoPixel synchronization
- MIT App communication issues

---

# Conclusion

This lab successfully demonstrated the implementation of an IoT-based smart color detection and control system using ESP32 and MIT App Inventor. By integrating a color sensor, NeoPixel LED, DC motor, and mobile application, the system provides both automatic color-based control and manual user interaction. The project highlights practical applications of embedded systems, edge computing, and IoT for real-time monitoring and intelligent device control.