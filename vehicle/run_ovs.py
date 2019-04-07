#!/usr/bin/env python3

import sys
import os
import signal
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from vehicle.client import *
from utils.system_killer import Killer


def main(argv):

    display = True
    batman = False
    try:
        opts, args = getopt.getopt(argv, "bhn:d", ["batman","help","name=","disableDisplay"])

    except Exception as e:
        print("-n <name> -d disables LED output")
        print(e)
        sys.exit(0)

    name = None
    for opt, arg in opts:
        if opt == "-h":
            print("-n <name> -d disables LED output")
            sys.exit()
        if opt in ('-n', "--name"):
            name = arg
        if opt in ('-d', "--disableDisplay"):
            display = False
            print("LED display is disabled")
        if opt in ('-b', "--batman"):
            batman=True

    if name == None:
        print("Using hostname as UAV name!")

    kill = Killer()
 
    node = Client("MULTI_ROTOR", name, kill, batman, display)
    node.initVehicle()
    node.initV2V()
    node.initConn()


if __name__=="__main__":

    main(sys.argv[1:])
    print("exited")
    sys.exit(0)