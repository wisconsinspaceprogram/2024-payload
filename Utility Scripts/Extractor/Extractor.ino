#include <SPI.h>
#include <SD.h>

void setup() {
    Serial.begin(115200);
    if (!SD.begin(53)) {
        Serial.println("Initialization failed!");
        return;
    }

    File dataFile = SD.open("log_1.csv", FILE_READ);
    if (dataFile) {
        while (dataFile.available()) {
            Serial.write(dataFile.read());
        }
        dataFile.close();
    } else {
        Serial.println("Error opening log.csv");
    }
}

void loop() {
    // Other code or tasks can go here
}
