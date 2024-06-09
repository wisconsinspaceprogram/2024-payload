#include <Adafruit_BNO055.h>
#include <SD.h>

//IMU
Adafruit_BNO055 bno055 = Adafruit_BNO055();


//SD Card
#define SD1CSPIN 53 //Primary SD Card, SD Flash Module 
#define SD2CSPIN 49 //Secondary SD Card, Removable SD Card MOdule

int dataOutSize = 20;
double dataOut[] {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
char filename1[] = "/log_1.csv";
char filename2[] = "/log_2.csv";
bool sd1Active = false;
bool sd2Active = false;
float sd1DeactivationTime = 0;
float sd2DeactivationTime = 0;


//Launch parameters
bool launched = false;    
float launchTime = -1;       //Time for keeping the launch sequence on for set time
int cycleState = 0;         //Cycles through the different
#define cycleTime 4     //# of seconds to stay on each cycle state
float lastCycleUpdate = 0;   //# of seconds since last cycle change
#define launchDuration 300 //# of seconds to stay in the launched mode
int ranCnt = 0;

//Code frequency in Hz
#define PRE_LAUNCH_FREQUENCY 10 
#define LAUNCH_FREQUENCY 50


//Other pins
#define photoDiodePin A0
#define mainBatPin A1
#define coilPin A2
#define coilBatPin A3


//Output LEDs
#define launchLED 8
#define sdLED 9
#define coilLED 10
#define photoDiodeLED 11  
#define imuLED 12
#define ranLED 13

bool coilVoltageDetected = false;


//Cycle Sequences
int preLaunchCycleSize = 18;
bool preLaunchCycle[18][6] = {
  {0, 0, 0, 0, 0, 0},
  {1, 1, 1, 1, 1, 1},
  {1, 0, 1, 1, 1, 1},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0}
};

int launchCycleSize = 14;
bool launchCycle[14][6] = {
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {1, 1, 1, 1, 1, 1},
  {1, 0, 1, 1, 1, 1},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {1, 0, 0, 1, 1, 1},
  {1, 0, 0, 0, 1, 1},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0},
  {1, 0, 0, 0, 0, 1},
  {0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0}, 
  {1, 0, 0, 0, 0, 0}
};

int cyclePins[6] = {2, 3, 4, 5, 6, 7};


void setup() {
  Serial.begin(9600);

  //Starting SD Cards
  pinMode(SD1CSPIN, OUTPUT);
  
  if(SD.begin(SD1CSPIN)){
    Serial.println("SD 1 Good");
    sd1Active = true;
  } else {
    Serial.println("SD 1 Bad");
    sd1Active = false;
  }

  if(SD.begin(SD2CSPIN)){
    Serial.println("SD 2 Good");
    sd2Active = true;
  } else {
    Serial.println("SD 2 Bad");
    sd2Active = false;
  }

  //Starting IMU
  bno055.begin();
  bno055.setExtCrystalUse(true);

  //Setting some outputs pins to output
  pinMode(cyclePins[0], OUTPUT);
  pinMode(cyclePins[1], OUTPUT);
  pinMode(cyclePins[2], OUTPUT);
  pinMode(cyclePins[3], OUTPUT);
  pinMode(cyclePins[4], OUTPUT);
  pinMode(cyclePins[5], OUTPUT);


  pinMode(launchLED, OUTPUT);
  pinMode(sdLED, OUTPUT);
  pinMode(coilLED, OUTPUT);
  pinMode(photoDiodeLED, OUTPUT);  
  pinMode(imuLED, OUTPUT);
  pinMode(ranLED, OUTPUT);

  //Write headers to SD card
  //TODO

}

void loop() {
  //Local time 
  float time = millis() / 1000.0;

  //IMU
  //Get calibration
  uint8_t system, gyro, accel, mg = 0;
  bno055.getCalibration(&system, &gyro, &accel, &mg);

  //Get readings
  imu::Vector<3> acc = bno055.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
  //imu::Vector<3> gyr = bno055.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);  //Don't need, but here if needed
  imu::Vector<3> mag = bno055.getVector(Adafruit_BNO055::VECTOR_MAGNETOMETER) / 100; // in Gauss

  //Other readings
  //Reading photo diode value
  float newPhotoDiodeValue = analogRead(photoDiodePin);

  //Reading voltage dividers
  float mainBatVoltage = (analogRead(mainBatPin)/1023.0) * 15.625;
  float coilBatVoltage = (analogRead(coilBatPin)/1023.0) * 15.625;
  float coilVoltage = (analogRead(coilPin)/1023.0) * 15.625;


  //Launch management
  // Launch detected
  if((abs(acc.x()) > 20 || abs(acc.y()) > 20 || abs(acc.z()) > 20) && !launched){
    launched = true;
    launchTime = time;
    cycleState = 0;
    ranCnt++;
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

  //Updating LEDs
  digitalWrite(launchLED, launched ? HIGH : LOW);
  digitalWrite(sdLED, (sd1Active && sd2Active) ? HIGH : LOW); 
  digitalWrite(coilLED, coilVoltageDetected ? HIGH : LOW);
  digitalWrite(photoDiodeLED, (newPhotoDiodeValue > 0 && newPhotoDiodeValue < 350) ? HIGH : LOW);
  digitalWrite(imuLED, (acc.x() != 0.0 || acc.y() != 0.0 || acc.z() != 0.0) ? HIGH : LOW);
  digitalWrite(ranLED, ranCnt > 0);

  //Setting this to true if we see some voltage over coil
  if(coilVoltage > 0.25){
    coilVoltageDetected = true;
  }

  Serial.println(newPhotoDiodeValue);
  //Serial.println(acc.z());

  //Logging data
  dataOut[0] = time;
  dataOut[1] = cycleState;
  dataOut[2] = mag.x();
  dataOut[3] = mag.y();
  dataOut[4] = mag.z();
  dataOut[5] = acc.x();
  dataOut[6] = acc.y();
  dataOut[7] = acc.z();
  dataOut[8] = launchTime;
  dataOut[9] = newPhotoDiodeValue;
  dataOut[10] = launched ? 1 : 0;
  dataOut[11] = ranCnt;
  dataOut[12] = bno055.getTemp();
  dataOut[13] = sd1Active ? 1 : 0;
  dataOut[14] = sd2Active ? 1 : 0;
  dataOut[15] = mainBatVoltage;
  dataOut[16] = coilBatVoltage;
  dataOut[17] = coilVoltage;

  
  //Writing to SD
  if(sd1Active || (time - sd1DeactivationTime > 15)){
    bool began = SD.begin(SD1CSPIN);
    if(began){
      sd1Active = writeToSD(filename1, dataOut);
      if(!sd1Active){
        sd1Active = false;
        sd1DeactivationTime = time;
      }
    } else {
      sd1Active = false;
      sd1DeactivationTime = time;
    }
  }

  if(sd2Active || (time - sd2DeactivationTime > 15)){
    bool began = SD.begin(SD2CSPIN);
    if(began){
      sd2Active = writeToSD(filename2, dataOut);
      if(!sd2Active){
        sd2Active = false;
        sd2DeactivationTime = time;
      }
    } else {
      sd2Active = false;
      sd2DeactivationTime = time;
    }
  }
  

  delay(launched ? (1000 / LAUNCH_FREQUENCY) : (1000 / PRE_LAUNCH_FREQUENCY));
}

bool writeToSD(char filename[], double out[]){
  File myFile = SD.open(filename, FILE_WRITE);     
   // if the file opened okay, write to it:
   if (myFile) 
   {
     //Serial.println("Writing to csv.txt");
     for(int i = 0; i < dataOutSize; i++){
      myFile.print(out[i]);
      //Serial.print(out[i]);
      
      if(i != dataOutSize-1){
        myFile.print(",");        
      }
     }
     myFile.println();
     myFile.close();
     return true;//sdLoaded = true
     ;
   } 
   else 
   {
     //Serial.println("error opening csv.txt");
     //SD.begin(chipSelect);
     return false;//sdLoaded = false;
   }
   
   return false;
}
