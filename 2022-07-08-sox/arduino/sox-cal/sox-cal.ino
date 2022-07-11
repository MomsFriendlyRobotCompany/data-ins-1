// MIT
// Kevin Walchko (c) 2020
// -----------------------------------------------------------
// accel/gyro: https://adafruit.github.io/Adafruit_LSM6DS/html/class_adafruit___l_s_m6_d_s.html
// mag: https://adafruit.github.io/Adafruit_LIS3MDL/html/class_adafruit___l_i_s3_m_d_l.html
// pressure[lps22]: https://adafruit.github.io/Adafruit_LPS2X/html/_adafruit___l_p_s2_x_8h.html
// pressure[bpm390]: https://github.com/adafruit/Adafruit_BMP3XX/blob/master/bmp3_defs.h
// conversions: https://github.com/adafruit/Adafruit_Sensor/blob/master/Adafruit_Sensor.h
// TFmini: https://github.com/hideakitai/TFmini
// -----------------------------------------------------------

// #include "Arduino.h"
#include <Wire.h>
#include <cstdint>
#include <Adafruit_LSM6DSOX.h>
#include <Adafruit_LIS3MDL.h>


class gciLSOXLIS {
public:
    gciLSOXLIS(): found(false), soxFound(false), lisFound(false),
        bsize(sizeof(data)),
        invg(1.0/SENSORS_GRAVITY_STANDARD) {}

    bool init(){
        if (sox.begin_I2C()) {
            soxFound = true;

            // Accelerometer ------------------------------------------
            sox.setAccelRange(LSM6DS_ACCEL_RANGE_4_G);
            sox.setAccelDataRate(LSM6DS_RATE_208_HZ);

            // Gyros ----------------------------------------------------
            sox.setGyroRange(LSM6DS_GYRO_RANGE_2000_DPS);
            sox.setGyroDataRate(LSM6DS_RATE_208_HZ);
        }

        // Magnetometer -----------------------------------------------------
        if (lis3mdl.begin_I2C()) {
          lisFound = true;
          // lis3mdl.setPerformanceMode(LIS3MDL_ULTRAHIGHMODE); // 155 already does this
          // lis3mdl.setPerformanceMode(LIS3MDL_HIGHMODE); // 300 already does this
          lis3mdl.setOperationMode(LIS3MDL_CONTINUOUSMODE);
          lis3mdl.setDataRate(LIS3MDL_DATARATE_300_HZ); // sets LIS3MDL_HIGHMODE
          lis3mdl.setRange(LIS3MDL_RANGE_4_GAUSS);
        }

        found = soxFound && lisFound;
        return found;
    }

    void read(){
      //[a,g,m,temp,timestamp]
      // if (!found) { return; }

      sox.getEvent(&a,&g,&t);

      data.f[0] = a.acceleration.x * invg;
      data.f[1] = a.acceleration.y * invg;
      data.f[2] = a.acceleration.z * invg;

      data.f[3] = g.gyro.x;
      data.f[4] = g.gyro.y;
      data.f[5] = g.gyro.z;

      data.f[9] = t.temperature;

      lis3mdl.getEvent(&mag);

      data.f[6] = mag.magnetic.x;
      data.f[7] = mag.magnetic.y;
      data.f[8] = mag.magnetic.z;

      data.l[10] = micros();
    }

    inline bool accelFound() const { return soxFound; }
    inline bool gyroFound() const { return soxFound; }
    inline bool magFound() const { return lisFound; }

    bool found;

    union { char b[11*sizeof(float)]; float f[11]; unsigned long l[11];} data;
    const uint8_t bsize; // length of array

protected:
    bool soxFound;
    bool lisFound;
    Adafruit_LSM6DSOX sox; // accel / gyro / temp
    Adafruit_LIS3MDL lis3mdl; // magnetometer
    const float invg;
    sensors_event_t a,g,t;
    sensors_event_t mag;
};

// sensor
gciLSOXLIS imu; // accel / gyro / mag / temp / timestamp

void setup(void) {
    Serial.begin(1000000); // 1Mbps
    Serial.setTimeout(1);
    while (!Serial)
        delay(1000);

    Wire.setClock(1000000); // 1 MHz

    // accel / gyro / mag / temp / timestamp
    imu.init();
}

void loop() {
    imu.read();
    int numChar = Serial.available();

    while ((numChar--) > 0){
        if (Serial.read() == 'g') {
        //     imu.read();
            Serial.write(imu.data.b, imu.bsize);
        }
    }
}
