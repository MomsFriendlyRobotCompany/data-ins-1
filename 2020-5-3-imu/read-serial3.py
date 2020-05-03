#!/usr/bin/env python
"""
For this to run, the Trinket M0 should have both LEDs Green

By the uC:
- Green: running
- White/Purple: REPL
"""
import struct
from serial import Serial
#import attr
from the_collector import BagIt
from the_collector import Pickle
import time
from binascii import unhexlify
import binascii
from colorama import Fore
from datetime import datetime
import logging
import sys

if len(sys.argv) != 2:
    print(f"{Fore.CYAN} Usage: ./read.py filename {Fore.RESET}")
filename = sys.argv[1]

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(name)s:%(levelname)s:%(message)s"
    )

s = Serial()
s.port = "/dev/serial/by-id/usb-Adafruit_Industries_LLC_Trinket_M0_CED3D24F0345C405A413E273237090FF-if00"
s.buadrate = 115200
s.timeout = 1/30
s.open()

# logger = logging.getLogger("imu-logger")

bag = BagIt(Pickle)
now = datetime.now().timestamp()

if s.is_open:
    try:
        cnt = 0
        while True:
            # cnt = cnt + 1
            if cnt%100 == 0:
                # n = datetime.now().timestamp()
                # hz = 1/(n - now)
                # print(cnt*hz, hz)
                # now = n
                # cnt = 0
                print(cnt)

            if cnt > 2000:
                break

            d = s.read_until(terminator=b"\r\nb")

            d = d.decode("utf-8")
            # print(f"{Fore.YELLOW}{d}{Fore.RESET}")
            lines = d.split("'")
            # print(f"{Fore.MAGENTA}{lines}{Fore.RESET}")
            if not lines:
                continue

            bad = []
            for i,l in enumerate(lines):
                if len(l)%2 == 1:
                    bad.append(i)
                    # print(f"{Fore.CYAN}*** POP[{i}]: odd {Fore.RESET}")
                elif l[:2] != 'FF':
                    bad.append(i)
                    # print(f"{Fore.CYAN}*** POP[{i}]: no FF {Fore.RESET}")
                else:
                    l = l[2:]
                    lines[i] = l
                    # print(f">> {len(l)}: {l}")

            # for i,l in enumerate(lines):
            #     if i in bad:
            #         print(f"{Fore.RED}** [{i}] {l} {Fore.RESET}")
            #     else:
            #         print(f">> [{i}] {l}")

            bad.reverse()
            for i in bad:
                # print(f"{i}")
                lines.pop(i)

            # print(lines)
            # print("-----------------------------------------------")
            for line in lines:
                # print(f">> {type(line)}")
                try:
                    m = unhexlify(line)
                    d = struct.unpack('fffffffff', m)
                    cnt = cnt + 1
                    ts = datetime.now().timestamp()
                    bag.push("accel", (d[:3], ts,))
                    bag.push("mag", (d[3:6], ts,))
                    bag.push("gyro", (d[6:], ts,))
                    # print(f"{Fore.GREEN}>> {d} {Fore.RESET}")
                    # print(f"{Fore.CYAN}>> {len(m)}")
                    # broken = None
                except struct.error as e:
                    print(f"{Fore.RED}{len(line)}: {line}")
                    print(f"***struct: {e}***{Fore.RESET}")
                    # broken = line
                    continue
                except binascii.Error as e:
                    print(f"{Fore.RED}{len(line)}: {line}")
                    print(f"***binascii: {e}***{Fore.RESET}")
                    continue

    except KeyboardInterrupt:
        print("bye ... space cowboy!")

s.close()
bag.write(filename, timestamp=False)
