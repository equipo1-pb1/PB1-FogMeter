
#include <SoftwareSerial.h>


#include <Wire.h>
#include <MPU6050.h>

unsigned long timer = 0;
float timeStep = 0.01;
int action = 0;
float pitch = 0;
float roll = 0;
float yaw = 0;

//pin 10 como RX y 11 como TX
SoftwareSerial BT(10, 11);
MPU6050 mpu;

void setup() 
{
  BT.begin(38400);
  while(!mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_2G))
  {
    delay(500);
  }

  // If you want, you can set accelerometer offsets
  // mpu.setAccelOffsetX();
  // mpu.setAccelOffsetY();
  // mpu.setAccelOffsetZ();
  // Calibrate gyroscope. The calibration must be at rest.
  // If you don't want calibrate, comment this line.
  mpu.calibrateGyro();

  // Set threshold sensivty. Default 3.
  // If you don't want use threshold, comment this line or set 0.
  mpu.setThreshold(3);
  
}


void loop()
{
  
  if (BT.available() > 0) action = BT.read(); else action = 0;
  switch (action){
    case 0:
      break;
    case 'a':
      read_values(1, 0, 30, 500);
      break;
    case 'b':
      read_values(0, 1, 30, 500);
      break;
  }
  delay(100);
}

// 1 min
// 0.3 seg 
// 200 muestras

void read_values(int read_accel, int read_gyro, int secs, int samples){
  pitch = 0;
  roll = 0;
  yaw = 0;
  double interval_ms = (double)secs/samples;
  int loop_rate = interval_ms/timeStep;
  if (loop_rate <= 0) loop_rate = 1;
  int count = 0, act_samp = 0;
  while(act_samp < samples){
    timer = millis();
    if (read_gyro){
      Vector norm = mpu.readNormalizeGyro();
      
      pitch = pitch + norm.YAxis * timeStep;
      roll = roll + norm.XAxis * timeStep;
      yaw = yaw + norm.ZAxis * timeStep;
      yaw = norm.ZAxis;
    }
    
    if (count % loop_rate == 0){
      act_samp++;
      
      if (read_gyro){
        BT.print(yaw);
        BT.write("\n"); 
      }
      
      if (read_accel){
        Vector rawAccel = mpu.readRawAccel();
        Vector normAccel = mpu.readNormalizeAccel();
      
        float zNorm = normAccel.ZAxis;
        float yNorm = normAccel.YAxis;
        float xRaw = rawAccel.XAxis;
        float xNorm = normAccel.XAxis;
        BT.print(xNorm);
        BT.write("\n"); 
      }
    }
    count++;
    delay((timeStep*1000) - (millis() - timer));
  }
  BT.write("Done");
  BT.write("\n");
}
