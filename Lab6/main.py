from machine import Pin, SPI
from mfrc522 import MFRC522
import network
import urequests
import time
import os
import sdcard

# ==========================
# WiFi Configuration
# ==========================
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

# ==========================
# Firestore Configuration
# ==========================
PROJECT_ID = "rfid-bde6c"

URL = "https://firestore.googleapis.com/v1/projects/{}/databases/(default)/documents/rfid_logs".format(
    PROJECT_ID
)

# ==========================
# Student Database
# Replace these UIDs with your own cards
# ==========================
students = {
    "1425411918150": {
        "name": "Khorn Sokhadom",
        "student_id": "2023517",
        "major": "Software Engineering"
    },
}

# ==========================
# Buzzer
# Change GPIO if necessary
# ==========================
buzzer = Pin(4, Pin.OUT)
buzzer.off()

# ==========================
# RFID
# ==========================
spi = SPI(
    1,
    baudrate=1000000,
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(23),
    miso=Pin(19)
)

rdr = MFRC522(
    spi=spi,
    gpioRst=Pin(22),
    gpioCs=Pin(16)
)

# ==========================
# SD Card
# Change pins to your module
# ==========================
# ==========================
# SD Card
# ==========================

try:
    sd_spi = SPI(
        2,
        baudrate=1000000,
        sck=Pin(14),
        mosi=Pin(15),
        miso=Pin(2)
    )

    cs = Pin(13, Pin.OUT)

    sd = sdcard.SDCard(sd_spi, cs)
    vfs = os.VfsFat(sd)
    os.mount(vfs, "/sd")

    print("SD Card Mounted")
    print("Files:", os.listdir("/sd"))

except Exception as e:
    print("SD Card Error:", e)

# ==========================
# Connect WiFi
# ==========================
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("Connecting WiFi...", end="")

while not wifi.isconnected():
    print(".", end="")
    time.sleep(0.5)

print("\nConnected")
print(wifi.ifconfig())

# ==========================
# Functions
# ==========================

def get_time():
    current = time.localtime()

    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        current[0],
        current[1],
        current[2],
        current[3],
        current[4],
        current[5]
    )


def buzz(seconds):
    buzzer.on()
    time.sleep(seconds)
    buzzer.off()


def save_sd(uid, student):
    try:
        if "attendance.csv" not in os.listdir("/sd"):
            with open("/sd/attendance.csv", "w") as f:
                f.write("uid,name,student_id,major,date_time\n")
            print("attendance.csv created")
            
        with open("/sd/attendance.csv", "a") as f:
            f.write("{},{},{},{},{}\n".format(
                uid,
                student["name"],
                student["student_id"],
                student["major"],
                get_time()
            ))

        print("Saved to SD")

    except Exception as e:
        print("SD Error:", e)


def send_firestore(uid, student):

    data = {
        "fields": {

            "uid": {
                "stringValue": uid
            },

            "name": {
                "stringValue": student["name"]
            },

            "studentID": {
                "stringValue": student["student_id"]
            },

            "major": {
                "stringValue": student["major"]
            },

            "datetime": {
                "stringValue": get_time()
            }

        }
    }

    try:

        response = urequests.post(URL, json=data)

        print("Firestore:", response.text)

        response.close()

    except Exception as e:

        print("Firestore Error:", e)


# ==========================
# Main Loop
# ==========================

print("Ready to scan RFID card...")

while True:

    (stat, tag_type) = rdr.request(rdr.REQIDL)

    if stat == rdr.OK:

        (stat, uid) = rdr.anticoll()

        if stat == rdr.OK:

            uid_str = "".join(str(i) for i in uid)

            print("UID:", uid_str)

            if uid_str in students:

                student = students[uid_str]

                print("Valid Student")
                print(student)

                buzz(0.3)

                save_sd(uid_str, student)

                send_firestore(uid_str, student)

            else:

                print("Unknown Card")

                buzz(3)

            time.sleep(2)
