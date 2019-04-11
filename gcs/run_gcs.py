#!/usr/bin/env python3

import sys, getopt
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import multiprocessing as mp
from gcs.server import *
from utils.system_killer import Killer


def runServer(HOST, PORT, utm, input_parent_conn, output_child_conn, name, utmUpdate, verbose):
    queenB = Server(HOST, PORT, utm, input_parent_conn, output_child_conn, name, utmUpdate, verbose)
    queenB.listen()

def main(argv):

    #store JWT into 'token'
    with open("mwalton.token", "r") as toke:
        token = toke.read()

    #Get the IP and Port of server from the localIP py file

    



    subprocess.call(['../utils/./sysinfo.sh'])
    time.sleep(.00001)
    peripherals = [line.rstrip('\n') for line in open('sysdisc.txt')]   
    ethernetIP = peripherals[2]
    batmanIP = peripherals[3]
    wlan0 = peripherals[4]
    
    opts, args = getopt.getopt(argv, "ebw", ["ethernet", "batman", "wifi"])
    
    HOST = ""
    
    for opt, arg in opts:
        if opt == "-e":
            HOST = ethernetIP
        if opt == "-b":
            HOST = batmanIP
        if opt == "-w":
            HOST = wlan0
    
    if HOST == "":
        print("Please select ethernet, batman, or wifi with -e, -b, -w")
        sys.exit(0)

    PORT = 65432

    #These two pipes send data from the UI to the clientHandler server loop
    input_parent_conn, input_child_conn = mp.Pipe()
    output_parent_conn, output_child_conn = mp.Pipe()

    #create api interface with onesky
    utm = OneSkyAPI(token)

    kill = Killer()

    #instantiate the UI with the pipes
    ui = UI(input_child_conn, output_parent_conn, kill)
    #instantiate the server
    
    p_server = mp.Process(target= runServer, args=(HOST, PORT, utm, input_parent_conn, output_child_conn,  "castle", True, True))
    p_server.daemon = True
    p_server.start()

    ui.start()    
    p_server.join()    
    sys.exit(0)


if __name__=="__main__":

    main(sys.argv[1:])

    
    

    