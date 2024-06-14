//#include <SPI.h>
#include <SD.h>

void setup() {
    pinMode(53, OUTPUT);
    Serial.begin(256000);
    if (!SD.begin(53)) {
        Serial.println("Initialization failed!");
        return;
    }
}

void loop() {
    // Other code or tasks can go here
  String command = "";
  if (Serial.available() > 0) {
    command = Serial.readStringUntil('\n');
  }

  if(command == "1"){
    dump("log_1.csv", 53);
    Serial.println("Done");
  }

  if(command == "2"){
    dump("log_2.csv", 49);
    Serial.println("Done");
  }




    //dump("/log_1.csv", 53);
}

void dump(char filename[], int pin){
  SD.begin(pin);
  File dataFile = SD.open(filename, FILE_READ);
    if (dataFile) {
        while (dataFile.available()) {
            Serial.write(dataFile.read());
        }
        dataFile.close();
    } else {
        Serial.println("Error opening ");
    }
}
