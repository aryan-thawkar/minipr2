#include <Adafruit_Fingerprint.h>
#include <SoftwareSerial.h>

// On Arduino Uno, use pins 2 & 3 for sensor connection
#define FINGERPRINT_RX 2
#define FINGERPRINT_TX 3

// Set up the serial port for the sensor
SoftwareSerial fingerSerial(FINGERPRINT_RX, FINGERPRINT_TX);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&fingerSerial);

void setup() {
  // Start serial communication with computer
  Serial.begin(9600);
  while (!Serial);

  // Start fingerprint sensor
  finger.begin(57600);
  
  if (finger.verifyPassword()) {
    Serial.println("Found fingerprint sensor!");
  } else {
    Serial.println("Did not find fingerprint sensor :(");
    while (1);
  }

  Serial.println("Ready to receive commands:");
  Serial.println("E - Enroll new fingerprint");
  Serial.println("V - Verify/match fingerprint");
}

uint8_t getFingerprintEnroll(uint8_t id) {
  int p = -1;
  Serial.println("Waiting for valid finger to enroll");
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image taken");
      break;
    case FINGERPRINT_NOFINGER:
      Serial.println(".");
      break;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      break;
    case FINGERPRINT_IMAGEFAIL:
      Serial.println("Imaging error");
      break;
    default:
      Serial.println("Unknown error");
      break;
    }
  }

  p = finger.image2Tz(1);
  if (p != FINGERPRINT_OK) {
    Serial.println("Image conversion failed");
    return p;
  }

  Serial.println("Remove finger");
  delay(2000);
  p = 0;
  while (p != FINGERPRINT_NOFINGER) {
    p = finger.getImage();
  }

  Serial.println("Place same finger again");
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
  }

  p = finger.image2Tz(2);
  if (p != FINGERPRINT_OK) {
    Serial.println("Image conversion failed");
    return p;
  }

  p = finger.createModel();
  if (p != FINGERPRINT_OK) {
    Serial.println("Failed to create model");
    return p;
  }

  p = finger.storeModel(id);
  if (p != FINGERPRINT_OK) {
    Serial.println("Failed to store model");
    return p;
  }

  Serial.println("Stored!");
  return true;
}

uint8_t getFingerprintMatching() {
  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK) return p;

  p = finger.image2Tz();
  if (p != FINGERPRINT_OK) return p;

  p = finger.fingerFastSearch();
  if (p == FINGERPRINT_OK) {
    Serial.print("Found ID #"); Serial.print(finger.fingerID);
    Serial.print(" with confidence of "); Serial.println(finger.confidence);
  } else if (p == FINGERPRINT_NOTFOUND) {
    Serial.println("Did not find a match");
  } else {
    Serial.println("Unknown error");
  }
  return p;
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == 'V') {
      Serial.println("Starting verification...");
      getFingerprintMatching();
    }
    else if (cmd == 'E') {
      // Read the ID number that follows the 'E'
      String idStr = "";
      while (Serial.available()) {
        char c = Serial.read();
        if (isdigit(c)) {
          idStr += c;
        }
      }
      int id = idStr.toInt();
      Serial.print("Starting enrollment for ID #");
      Serial.println(id);
      getFingerprintEnroll(id);
    }
  }
}