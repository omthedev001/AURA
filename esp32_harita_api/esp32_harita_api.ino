/*
 * This ESP32 code is created by esp32io.com
 *
 * This ESP32 code is released in the public domain
 *
 * For more detail (instruction and wiring diagram), visit https://esp32io.com/tutorials/esp32-gps
 */

#include <TinyGPS++.h>

#define GPS_BAUDRATE 9600  // The default baudrate of NEO-6M is 9600

TinyGPSPlus gps;  // the TinyGPS++ object

const double LONDON_LAT = 21.218629;
const double LONDON_LON = 81.646797;

void setup() {
  Serial.begin(9600);
  Serial2.begin(GPS_BAUDRATE);

  Serial.println(F("ESP32 - GPS module"));
}

void loop() {
  if (Serial2.available() > 0) {
    if (gps.encode(Serial2.read())) {
      if (gps.location.isValid()) {
        double latitude = gps.location.lat();
        double longitude = gps.location.lng();
        unsigned long distanceKm = TinyGPSPlus::distanceBetween(latitude, longitude, LONDON_LAT, LONDON_LON) ;

        Serial.print(F("- latitude: "));
        Serial.println(latitude);

        Serial.print(F("- longitude: "));
        Serial.println(longitude);

        Serial.print(F("- distance to London: "));
        Serial.println(distanceKm);
      } else {
        Serial.println(F("- location: INVALID"));
      }

      Serial.println();
    }
  }

  if (millis() > 5000 && gps.charsProcessed() < 10)
    Serial.println(F("No GPS data received: check wiring"));
}
