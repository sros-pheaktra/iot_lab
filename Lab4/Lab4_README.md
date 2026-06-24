# Lab 4 – Multi-Sensor IoT Monitoring System

## System Architecture

```
ESP32 (MicroPython)
  ├── BMP280   (I2C 0x76) → temperature, pressure, altitude
  ├── MLX90614 (I2C 0x5A) → body temperature → fever detection
  ├── MQ-5     (ADC GPIO33) → gas reading → moving average → risk level
  └── DS3231   (I2C 0x68) → real-time timestamp
          │
          │  MQTT  (test.mosquitto.org:1883)
          │  Topic: /aupp/esp32/bmp280
          ▼
      Node-RED
          │  function node → formats InfluxDB payload
          ▼
      InfluxDB  (127.0.0.1:8086 / database: aupp_lab)
          │  measurement: bmp280
          ▼
      Grafana Dashboard
```

---

## File Structure

```
├── main.py              ← ESP32 MicroPython source
├── node_red_flow.json   ← Node-RED flow export
└── README.md            ← This file
```

---

## Edge Processing Logic

### Task 1 – Gas Moving Average Filter
The MQ-5 analog output is read via ESP32 ADC on GPIO 33 (12-bit, 0–4095).
A ring buffer stores the last 5 raw readings. Each cycle a new raw value is
appended, the oldest is evicted when the buffer exceeds 5, and the average
is computed as `sum(buffer) / len(buffer)`. This smooths transient noise
from the MQ-5 warm-up and power fluctuations. Both raw and averaged values
are printed to the serial monitor and included in the MQTT payload.

### Task 2 – Gas Risk Classification
The averaged ADC value is mapped to a risk level string each cycle:

| Averaged ADC | Risk Level |
|---|---|
| < 2100       | `SAFE`    |
| 2100 – 2599  | `WARNING` |
| ≥ 2600       | `DANGER`  |

`risk_level` is included in every MQTT JSON packet as a string tag.

### Task 3 – Fever Detection (MLX90614)
The MLX90614 measures object (body) temperature via infrared.

```python
fever_flag = 1 if body_temp >= 32.5 else 0
```

- `fever_flag = 1` → fever detected
- `fever_flag = 0` → normal temperature
- If MLX90614 is not detected on the I2C bus, `body_temp = -1`

### Task 4 – Pressure & Altitude (BMP280)
BMP280 values are read each cycle:
- `pressure` is converted from Pa to hPa (divided by 100)
- `altitude` is computed by the BMP280 driver using the barometric formula
- Both are sent in the JSON payload and visualized in Grafana time series panels

---

## Timestamp Logic

1. **Primary**: DS3231 RTC at I2C address 0x68 via `ds3231.get_time()`
2. **Fallback**: NTP sync (`ntptime.settime()`) at boot, then `time.localtime()` with UTC+7 offset applied

---

## MQTT JSON Payload Example

```json
{
  "temperature": 26.85,
  "pressure":    1008.62,
  "altitude":    25.73,
  "gas_raw":     2045,
  "gas_average": 2102.40,
  "risk_level":  "WARNING",
  "body_temp":   36.75,
  "fever_flag":  1,
  "timestamp":   "2025-04-10 09:32:15"
}
```

---

## Node-RED Function Node Code

```javascript
var p = msg.payload;
if (typeof p === "string") p = JSON.parse(p);

msg.payload = [{
    measurement: "bmp280",
    fields: {
        temperature: p.temperature,
        pressure:    p.pressure,
        altitude:    p.altitude,
        gas_raw:     p.gas_raw     || 0,
        gas_average: p.gas_average || 0,
        body_temp:   p.body_temp   || 0,
        fever_flag:  p.fever_flag  || 0
    },
    tags: {
        risk_level: p.risk_level || "SAFE"
    }
}];
return msg;
```

---

## Grafana Dashboard Panels

| # | Panel Title      | Type        | Field         |
|---|------------------|-------------|---------------|
| 1 | Gas Average      | Time Series | `gas_average` |
| 2 | Risk Level       | Stat        | `risk_level`  |
| 3 | Body Temperature | Gauge       | `body_temp`   |
| 4 | Pressure (hPa)   | Time Series | `pressure`    |
| 5 | Altitude (m)     | Time Series | `altitude`    |
| 6 | Fever Flag       | Stat        | `fever_flag`  |
| 7 | Room Temperature | Time Series | `temperature` |

---

## Hardware Wiring

| Sensor   | ESP32 Pins     | I2C Address |
|----------|----------------|-------------|
| BMP280   | SDA=21, SCL=22 | 0x76        |
| MLX90614 | SDA=21, SCL=22 | 0x5A        |
| DS3231   | SDA=21, SCL=22 | 0x68        |
| MQ-5     | GPIO 33 (ADC)  | —           |

All I2C sensors share the same bus on GPIO 21 (SDA) and GPIO 22 (SCL).

---

## How to Export Node-RED Flow as JSON

1. Open Node-RED in your browser (usually `http://127.0.0.1:1880`)
2. Click the **hamburger menu** (☰) at the top-right corner
3. Go to **Export**
4. In the dialog that opens:
   - Select **current flow** (exports only the active tab)
   - or select **all flows** (exports everything)
5. Click **Download** to save as `flows.json`
   - or click **Copy to clipboard** and paste into a `.json` file manually
6. Rename the file to `node_red_flow.json` for submission

> To reimport later: Menu → Import → select the file → click Import

