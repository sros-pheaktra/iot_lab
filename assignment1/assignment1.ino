#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

const char* ssid = "Robotic WIFI";
const char* password = "rbtWIFI@2025"

void startCameraServer();
void setupLedFlash(int pin);


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

}