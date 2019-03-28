#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from vehicle.client import *

def main(argv):
    display = True
    try:
        opts, args = getopt.getopt(argv, "hn:d", ["help","name=","disableDisplay"])

    except Exception as e:
        print("-n <name> -d disables LED output")
        print(e)
        sys.exit()

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

    if name == None:
        print("Using hostname as UAV name!")
    node = Client("MULTI_ROTOR", name, display)
    try:
        node.initVehicle()
        node.initV2V()
        node.initConn()

    except Exception as e:
        node.closeConnection()
        node.v2vComms.closeOutGoingConns()
        sys.exit(0)

if __name__=="__main__":

    main(sys.argv[1:])
    sys.exit(0)