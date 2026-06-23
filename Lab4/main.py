import network
import time
import ujson
import ntptime
from umqtt.simple import MQTTClient
from machine import Pin, I2C, ADC
from bmp280 import BMP280
from ds3231 import DS3231

# =========================
# Optional MLX90614
# =========================
try:
    from mlx90614 import MLX90614
    HAS_MLX = True
except:
    HAS_MLX = False

# =========================
# WiFi
# =========================
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

# =========================
# MQTT
# =========================
BROKER = "test.mosquitto.org"
PORT = 1883
CLIENT_ID = b"esp32_multi_sensor"
TOPIC = b"/aupp/esp32/lab4"
KEEPALIVE = 30

# =========================
# Constants
# =========================
FEVER_THRESHOLD = 32.5
GAS_PIN = 33
MOVING_AVG_SIZE = 5

gas_adc = ADC(Pin(GAS_PIN))
gas_adc.atten(ADC.ATTN_11DB)
gas_adc.width(ADC.WIDTH_12BIT)

gas_buffer = []

# =========================
# WiFi
# =========================
def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)

        timeout = time.ticks_ms()

        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), timeout) > 20000:
                raise RuntimeError("WiFi timeout")
            time.sleep(0.3)

    print("WiFi OK:", wlan.ifconfig())

# =========================
# MQTT
# =========================
def make_client():
    return MQTTClient(
        client_id=CLIENT_ID,
        server=BROKER,
        port=PORT,
        keepalive=KEEPALIVE
    )

# =========================
# Gas Processing
# =========================
def gas_sample():
    raw = gas_adc.read()
    gas_buffer.append(raw)

    if len(gas_buffer) > MOVING_AVG_SIZE:
        gas_buffer.pop(0)

    avg = sum(gas_buffer) / len(gas_buffer)

    if avg < 2100:
        risk = "SAFE"
    elif avg < 2600:
        risk = "WARNING"
    else:
        risk = "DANGER"

    return raw, round(avg, 2), risk

# =========================
# Main
# =========================
def main():

    wifi_connect()

    # =========================
    # NTP SYNC
    # =========================
    try:
        ntptime.host = "pool.ntp.org"
        ntptime.settime()
        print("NTP synced")
    except Exception as e:
        print("NTP failed:", e)

    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

    devices = i2c.scan()
    print("I2C Devices:", devices)

    bmp = BMP280(i2c)

    # MLX90614
    mlx = None
    if HAS_MLX and 90 in devices:
        try:
            mlx = MLX90614(i2c)
            print("MLX90614 detected")
        except Exception as e:
            print("MLX Error:", e)

    # DS3231
    ds3231 = None
    if 104 in devices:
        print("DS3231 detected")
        ds3231 = DS3231(i2c)
    else:
        print("DS3231 not detected, using NTP time")

    client = make_client()

    while True:

        try:
            client.connect()
            print("MQTT connected")

            while True:

                temperature = round(bmp.temperature, 2)
                pressure = round(bmp.pressure / 100, 2)
                altitude = round(bmp.altitude, 2)

                gas_raw, gas_avg, risk_level = gas_sample()

                if mlx:
                    try:
                        body_temp = round(mlx.read_object_temp(), 2)
                    except:
                        body_temp = -1
                else:
                    body_temp = -1

                fever_flag = 1 if body_temp >= FEVER_THRESHOLD else 0

                # =========================
                # TIMESTAMP
                # =========================
                if ds3231:
                    y, mo, d, h, mi, s = ds3231.get_time()
                else:
                    t = time.localtime(time.time() + 7 * 3600)  # UTC+7
                    y, mo, d, h, mi, s = t[0], t[1], t[2], t[3], t[4], t[5]

                timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                    y, mo, d, h, mi, s
                )

                print("------------------------------------")
                print("Temp:", temperature, "°C")
                print("Pressure:", pressure, "hPa")
                print("Altitude:", altitude, "m")
                print("Gas Raw:", gas_raw)
                print("Gas Avg:", gas_avg)
                print("Risk:", risk_level)
                print("Body Temp:", body_temp)
                print("Fever:", fever_flag)
                print("Time:", timestamp)

                payload = {
                    "temperature": temperature,
                    "pressure": pressure,
                    "altitude": altitude,
                    "gas_raw": gas_raw,
                    "gas_average": gas_avg,
                    "risk_level": risk_level,
                    "body_temp": body_temp,
                    "fever_flag": fever_flag,
                    "timestamp": timestamp
                }

                msg = ujson.dumps(payload)

                client.publish(TOPIC, msg)
                print("Published:", msg)

                time.sleep(5)

        except Exception as e:
            print("Error:", e)
            try:
                client.disconnect()
            except:
                pass
            time.sleep(3)

main()
