#include <SPI.h>
#include <SD.h>

const int chipSelect = 49;

void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  Serial.print("Initializing SD card...");

  if (!SD.begin(chipSelect)) {
    Serial.println("initialization failed!");
    return;
  }
  Serial.println("initialization done.");

  // Wipe the entire SD card
  wipeSDCard();

  pinMode(13, OUTPUT);
  digitalWrite(13, HIGH);
}

void loop() {
  // nothing happens after setup finishes.
}

void wipeSDCard() {
  // Open the root directory
  File root = SD.open("/");
  
  if (!root) {
    Serial.println("Failed to open root directory");
    return;
  }

  // Recursively delete all files and directories
  deleteAllFiles(root);

  // Close the root directory
  root.close();
  
  Serial.println("SD card wiped successfully");
}

void deleteAllFiles(File dir) {
  while (true) {
    File entry = dir.openNextFile();
    if (!entry) {
      // No more files
      break;
    }
    if (entry.isDirectory()) {
      // Recursively delete directory
      deleteAllFiles(entry);
    } else {
      // Delete file
      if (SD.remove(entry.name())) {
        Serial.print("Deleted file: ");
        Serial.println(entry.name());
      } else {
        Serial.print("Failed to delete file: ");
        Serial.println(entry.name());
      }
    }
    entry.close();
  }
}
