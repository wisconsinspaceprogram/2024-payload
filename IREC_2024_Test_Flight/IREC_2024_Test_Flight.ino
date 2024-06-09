#include <Adafruit_BNO055.h>
#include <SD.h>

//Initializing IMU
Adafruit_BNO055 myIMU = Adafruit_BNO055();

//Setting up the prelaunch and launch cycles
bool launched = false;    
float launchTime = -1;       //Time for keeping the launch sequence on for set time
int cycleState = 0;         //Cycles through the different
float cycleTime = 0.5;     //# of seconds to stay on each cycle state
float lastCycleUpdate = 0;   //# of seconds since last cycle change
float launchDuration = 100; //# of seconds to stay in the launched mode

int preLaunchCycleSize = 11;
bool preLaunchCycle[10][6] = {
  {0, 1, 1, 1, 1, 1},
  {0, 1, 1, 1, 1, 1},
  {0, 1, 1, 1, 1, 1},
  {0, 0, 1, 1, 1, 1},
  {1, 1, 1, 1, 1, 1},
  {1, 1, 0, 1, 1, 1},
  {0, 1, 1, 1, 1, 1},
  {1, 1, 1, 0, 1, 1},
  {1, 1, 1, 1, 1, 1},
  {0, 1, 1, 1, 1, 1}
};


int launchCycleSize = 17;
bool launchCycle[5][6] = {
  {1, 1, 1, 1, 1, 1},
  {1, 1, 1, 1, 1, 1},
  {1, 0, 1, 1, 1, 1},
  {1, 0, 0, 1, 1, 1},
  {0, 0, 0, 0, 0, 1}
};

int cyclePins[6] = {5, 6, 7, 8, 9, 10}; //Pins to connect the current control board to

//Code frequency in Hz
int preLaunchFrequency = 5; 
int launchFrequency = 20;

//SD Card stuff
File myFile;
const int chipSelect = 4;
int dataOutSize = 10;
double dataOut[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
char fileName[] = "text.csv";

//Photo Diode
int photoDiodePin = A0;

//Setup
void setup() {
  //Starting everything
  Serial.begin(9600);
  
  //IMU Setup, external crystal is better clock
  myIMU.begin();
  myIMU.setExtCrystalUse(true);

  //Setting corrent pins to input/output
  pinMode(cyclePins[0], OUTPUT);
  pinMode(cyclePins[1], OUTPUT);
  pinMode(cyclePins[2], OUTPUT);
  pinMode(cyclePins[3], OUTPUT);
  pinMode(cyclePins[4], OUTPUT);
  pinMode(cyclePins[5], OUTPUT);

  //Setting up SD card
  pinMode(chipSelect, OUTPUT);

  if (SD.begin(chipSelect))
  {
    Serial.println("SD card is present & ready");
  } 
  else
  {
    Serial.println("SD card missing or failure");
    //ADD some indication
  }

  //Writing headers to SD
  myFile = SD.open(fileName, FILE_WRITE);    
  if(myFile){
    myFile.println("Idk, headers here");
    myFile.close();
  } else {
    Serial.println("Bad");
  }
}

void loop() {
  // Defining the local time to reference everything from
  float time = millis() / 1000.0;

  // Getting data from IMU

  // Calibration
  uint8_t system, gyro, accel, mg = 0;
  myIMU.getCalibration(&system, &gyro, &accel, &mg);

  // Readings
  imu::Vector<3> acc = myIMU.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
  //imu::Vector<3> gyr = myIMU.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);  //Don't need, but here if needed
  imu::Vector<3> mag = myIMU.getVector(Adafruit_BNO055::VECTOR_MAGNETOMETER) / 100; // in Gauss

  //Photo diode reading
  float photoDiodeValue = analogRead(photoDiodePin);

  // Launch detection and deactivation

  // Launch detected
  if((abs(acc.x()) > 30 || abs(acc.y()) > 30 || abs(acc.z()) > 30) && !launched){
    launched = true;
    launchTime = time;
    cycleState = 0;
    Serial.print("LAUCNH");
  }

  // Launch over
  if(time - launchTime > launchDuration && launched){
    launched = false;
    cycleState = 0;
  }

  // Updating the cycle information
  if(time - lastCycleUpdate > cycleTime){
    cycleState += 1;
    lastCycleUpdate = time;
    if(cycleState > (launched ? launchCycleSize - 1 : preLaunchCycleSize - 1)){
      cycleState = 0;
    }
  }

  // Setting the current control pins to current cycle state
  bool (&currentCombo)[6] = launched ? launchCycle[cycleState] : preLaunchCycle[cycleState];
  digitalWrite(cyclePins[0], currentCombo[0] ? HIGH : LOW);
  digitalWrite(cyclePins[1], currentCombo[1] ? HIGH : LOW);
  digitalWrite(cyclePins[2], currentCombo[2] ? HIGH : LOW);
  digitalWrite(cyclePins[3], currentCombo[3] ? HIGH : LOW);
  digitalWrite(cyclePins[4], currentCombo[4] ? HIGH : LOW);
  digitalWrite(cyclePins[5], currentCombo[5] ? HIGH : LOW);

  dataOut[0] = time;
  dataOut[1] = cycleState;
  dataOut[2] = mag.x();
  dataOut[3] = mag.y();
  dataOut[4] = mag.z();
  dataOut[5] = acc.x();
  dataOut[6] = acc.y();
  dataOut[7] = acc.z();
  dataOut[8] = launchTime;
  dataOut[9] = photoDiodeValue;
  dataOut[10] = launched ? 1 : 0;
  
  writeToSD(fileName, dataOut);

  delay(launched ? launchFrequency : preLaunchFrequency);
}

bool writeToSD(char filename[], double out[]){
  myFile = SD.open(filename, FILE_WRITE);     
   // if the file opened okay, write to it:
   if (myFile) 
   {
     Serial.println("Writing to csv.txt");
     for(int i = 0; i < dataOutSize; i++){
      myFile.print(out[i]);
      Serial.print(out[i]);
      
      if(i != dataOutSize - 1){
        myFile.print(",");
        Serial.print(",");
        
      }
     }
     myFile.println();
     Serial.println();
     myFile.close();
   } 
   else 
   {
     Serial.println("error opening csv.txt");
     SD.begin(chipSelect);
   }
   
   return true;
}
