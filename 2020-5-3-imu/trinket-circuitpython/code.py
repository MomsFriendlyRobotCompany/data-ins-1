"""
For this to run, the Trinket M0 should have both LEDs Green

By the uC:
- Green: running
- White/Purple: REPL
"""
import time
import board
import busio
import adafruit_fxos8700
import adafruit_fxas21002c
import struct
from adafruit_binascii import hexlify, unhexlify

i2c = busio.I2C(board.SCL, board.SDA)
accel = adafruit_fxos8700.FXOS8700(i2c)
gyros = adafruit_fxas21002c.FXAS21002C(i2c)


class Rate:
    """
    Uses sleep to keep a desired message/sample rate.
    """
    def __init__(self, hertz):
        self.last_time = time.monotonic()
        self.dt = 1/hertz

    def sleep(self):
        """
        This uses sleep to delay the function. If your loop is faster than your
        desired Hertz, then this will calculate the time difference so sleep
        keeps you close to you desired hertz. If your loop takes longer than
        your desired hertz, then it doesn't sleep.
        """
        now = time.monotonic()
        diff = now - self.last_time
        if diff < self.dt:
            new_sleep = self.dt - diff
            time.sleep(new_sleep)

        # now that we hav slept a while, set the current time
        # as the last time
        self.last_time = time.monotonic()

# rate = Rate(100)

while True:
    accel_x, accel_y, accel_z = accel.accelerometer
    mag_x, mag_y, mag_z = accel.magnetometer
    #print('Acceleration (m/s^2): ({0:0.3f}, {1:0.3f}, {2:0.3f})'.format(accel_x, accel_y, accel_z))
    #print('Magnetometer (uTesla): ({0:0.3f}, {1:0.3f}, {2:0.3f})'.format(mag_x, mag_y, mag_z))

    gyro_x, gyro_y, gyro_z = gyros.gyroscope
    #print('Gyroscope (radians/s): ({0:0.3f},  {1:0.3f},  {2:0.3f})'.format(gyro_x, gyro_y, gyro_z))

    d = (accel_x, accel_y, accel_z,mag_x, mag_y, mag_z,gyro_x, gyro_y, gyro_z)
    d = struct.pack('fffffffff', *d)
    s = hexlify(d)
    # s = sum(d) & 0xff
    # dd = b'\xff' + d + struct.pack('B',s)
    # print(dd)
    # print(b'\xff')
    # rate.sleep()
    # print([255,255])
    # print(','.join(('F',accel_x, accel_y, accel_z,mag_x, mag_y, mag_z,gyro_x, gyro_y, gyro_z)))

    # works - ascii
    # s = "F,{},{},{},{},{},{},{},{},{}".format(accel_x, accel_y, accel_z,mag_x, mag_y, mag_z,gyro_x, gyro_y, gyro_z)

    print(b'FF' + s, flush=True)
    # rate.sleep()
