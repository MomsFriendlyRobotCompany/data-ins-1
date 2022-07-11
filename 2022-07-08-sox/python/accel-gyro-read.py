#!/usr/bin/env python3
import time
import serial
from struct import Struct
from collections import deque
import pickle
from tqdm import tqdm
import sys
from datetime import date

def grabData(num, ser):
    msg = Struct("10fI")
    data = deque()

    for i in tqdm(range(num)):
        ser.write(b"g") # get data
        time.sleep(0.001)
        reply = ser.read(11*4)
        ans = msg.unpack(reply)

        data.append(ans)

        time.sleep(0.007)

    return data

def main(filename, port, count):

    save = {}
    info = from_yaml("sensor.yml")
    save["info"] = info

    ser = serial.Serial(port,1000000)

    order = [
        "x-up",
        "x-down",
        "y-up",
        "y-down",
        "z-up",
        "z-down"
    ]

    data = deque()

    for o in order:
        _ = input(f">> Orient {o}, press ENTER when ready")
        data += grabData(count, ser)

    # save = {
    #     "info": {
    #         "LSM6DSOX": {
    #             "accel": ("4000G", "208Hz"),
    #             "gyro": ("2000DPS", "208Hz"),
    #             "temp": "Celcius"
    #         },
    #         "LIS3MDL": {
    #             "mag": ("4GAUSS", "300Hz")
    #         }
    #     },
    #     "count": count,
    #     "order": order,
    #     "data": data
    # }
    save["data"] = data
    save["order"] = order
    save["count"] = len(data)

    with open(filename, "wb") as fd:
        pickle.dump(save, fd)

if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     # print(f"Usage: {sys.argv[0]} filename")
    #     # sys.exit(1)
    #     f = "data"
    # else:
    #     f = sys.argv[1]

    count = 1000
    port = "/dev/cu.usbmodem14601"
    file = "data-" + date.today().isoformat() + ".pkl"
    main(file, port, count)
