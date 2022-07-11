#!/usr/bin/env python3
import time
import serial
from struct import Struct
from collections import deque
from tools.magplot import MagPlot
import pickle
# from tqdm import tqdm
import sys
from datetime import date
import yaml
from tools.save import from_yaml

msg = Struct("10fI")

def grabData(ser):
    ser.write(b"g") # get data
    time.sleep(0.001)
    reply = ser.read(11*4)
    ans = msg.unpack(reply)

    # time.sleep(0.007)

    return ans

# def readyaml(file):
#     with open(file,"r") as fd:
#         d = yaml.safe_load(fd)
#     return d


def main(filename, port):

    save = {}
    info = from_yaml("sensor.yml")
    save["info"] = info

    ser = serial.Serial(port,1000000)

    data = deque()
    plot = MagPlot()

    while True:
        try:
            d = grabData(ser)
            data.append(d)
            m = d[6:9]
            plot.push(*m)
            plot.plot()
        except KeyboardInterrupt:
            print("Ctrl-Z")
            ser.close()
            break

    save["data"] = data
    save["count"] = len(data)

    with open(filename, "wb") as fd:
        pickle.dump(save, fd)

if __name__ == "__main__":
    f = "data-mag"
    port = "/dev/cu.usbmodem14601"
    file = f + "-" + date.today().isoformat() + ".pkl"
    main(file, port)
