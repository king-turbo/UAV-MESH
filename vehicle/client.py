#!/usr/bin/env python3
import sys, getopt
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import socket
import json
import time
from dronekit import Vehicle, connect
import select
import subprocess
from vehicle.v2v import V2V
from vehicle import led_display
import _thread
import threading
import signal


class UAV(Vehicle):
    '''
    This class inherets from the dronekit Vehicle class. The dronekit library is a super easy way to
    This class inherets from the dronekit Vehicle class. The dronekit library is a super easy way to
    communicate with the flight controller on the UAV
    '''

    def __init__(self, *args):

        super(UAV, self).__init__(*args)
        self.sendDict = {}

    def toJSON(self):
        #Why do I even have this??
        return json.dumps(self.sendDict, default=lambda o: o.__dict__)

    def updateUAVGPS(self):
        #grabs the GPS stuff from the flight controller
        self.global_loc = self.location.global_frame
        return (self.global_loc.lon, self.global_loc.lat, self.global_loc.alt)

class DummyDrone:
    '''
    just for testing purposes
    '''
    def __init__(self):
        self.lon = 0
        self.lat = 0
        self.alt = 0

    def updateUAVGPS(self):
        return (self.lon, self.lat, self.alt)


class Client():

    '''
    Client class handles communication from the flight controller and the server
    
    '''

    def __init__(self, vehicleType, name, kill, allowLED = True):

        self.allowDisplay = allowLED
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1.4)
        self.status = "default"
        self.updateRate = 5
        self.sending = True
        self.vehicleType = vehicleType
        self.heading= 0
        self.kill = kill
        self.ui = False

        if name == None:
            self.name = socket.gethostname()
        else:
            self.name = name
        self.initMsgFrmClient = {"$connect": 1, "type": vehicleType, "name": self.name}



    def initVehicle(self):

        '''
        This method initializes the connection to the flight controller and pulls local IP information
        '''

        #run the ttyfinder shell script to find what type of flight controller and which ACM it is connected to
        subprocess.call(['../utils/./sysinfo.sh'])
        time.sleep(.00001)
        self.peripherals = [line.rstrip('\n') for line in open('sysdisc.txt')]
        self.FCtype = self.peripherals[1]

        #TODO: make it so it can switch between eth0, bat0, wlan0
        self.ethernetIP = self.peripherals[2]

        if self.allowDisplay:
            self.ui = led_display.User2VehicleInterface(0x3C, 0, self.ethernetIP,0)  # TODO: add bat0 and wlan0
            self.ui.loadFlag = True                                                 # TODO: Need better iic thing
            self.ui.displayMode = "connecting2FC"
        try:

            #calls connect method from dronekit library, #TODO: need to set /dev/ttyACM to static (this is fixed?)
                                                         #TODO: need to make a thing for other types of flight controllers
            time.sleep(1)
            self.uav = connect(self.peripherals[0], wait_ready=True, vehicle_class=UAV)
            #call the update method from vehicle class. This gets the first GPS coordinates from the flight controller
            self.lon, self.lat, self.alt = self.uav.updateUAVGPS()

            if self.allowDisplay:
                self.ui.loadFlag = False
            #TODO: make this more robust, basically if we are not on the equator
            if self.lon != 0:
                #then set the init GPS coordinates to the GPS coordinates returned from the vehicle 
                self.initMsgFrmClient["lon"] = self.lon
                self.initMsgFrmClient["lat"] = self.lat
                self.initMsgFrmClient["alt"] = self.alt
            #if the lon is 0, then that means that the GPS lock is probably bad (TODO: make this less stupid)    
            else:
                self.initMsgFrmClient["lon"] = 0
                self.initMsgFrmClient["lat"] = 0
                self.initMsgFrmClient["alt"] = 0



        except:
            if self.allowDisplay:
                self.ui.loadFlag = False
            #if we are unable to connect to the flight controller, then use the DummyDrone class for testing purposes
            self.uav = DummyDrone()
            #this will just returns 0s
            self.lon, self.lat, self.alt = self.uav.updateUAVGPS()
            self.initMsgFrmClient["lon"] = self.lon
            self.initMsgFrmClient["lat"] = self.lat
            self.initMsgFrmClient["alt"] = self.alt
            if self.allowDisplay:
                self.ui.displayMode = "dummy"

        if self.allowDisplay:
            self.ui.displayMode = "status"
            self.ui.displayMode = "status"


    def initV2V(self):
        self.v2vComms = V2V(self.ethernetIP, self.name, self.vehicleType)
        self.v2vComms.initListenSocket()
        self.findGCS()
        self.neighborHandler()

    def neighborHandler(self):

        def loop():
            while not self.kill.kill:
            
                self.v2vComms.msgAllUavs(self.lat, self.lon, self.alt, self.heading)
                time.sleep(2)


        threading.Thread(target=loop).start()


    def update(self):


        '''
        This method gets updates from the flight controller and stores the new GPS values in lon,lat,alt.
        It then updates the sendDict, which is the dictionary that is sent to the server
        '''
        
        self.lon, self.lat, self.alt = self.uav.updateUAVGPS()

        self.sendDict = {"name" : self.name,
                         "mode" : self.mode,
                         "updateRate" : self.updateRate,
                         "lon" : self.lon,
                         "lat" : self.lat,
                         "alt": self.alt}

    def findGCS(self):
        self.v2vComms.findNodes()
        print("Finding GCS")
        self.gcsList = self.v2vComms.returnGCS()
        print("List of GCSs:")
        print(self.gcsList)
        if not self.gcsList:
            #TODO: need to try to connect again if gcslist is empty
            print("gcs list empty")
        #TODO: need to make the user select which GCS from the LED display
        else:
            self.HOST = self.gcsList[0][1]


    def initConn(self):

        '''
        This method initializes the connection to the server. 
        '''
        #connect to the server

        try:
            self.sock.connect((self.HOST, 65432))
            #sent the init message
            self.sock.sendall(json.dumps(self.initMsgFrmClient).encode("utf-8"))
            #recieve data
            data = self.sock.recv(1024)
            print("Init from GCS:")
            print(data)
            #decode data
            _data = json.loads(data.decode("utf-8"))
            #change the updateRate to whatever the server requests
            self.updateRate = _data["freq"]
            #change mode to what the server requests
            #change mode to what the server requests
            self.mode = _data["mode"]
            #if the mode is in default
            if _data["mode"] == "default":
                #then send data
                self.sendData()

        except ConnectionResetError:                            #TODO: Figure out exception for timeout error and
                                                                #TODO: whether or not to have separate method for reconnecting
            print("Connection Reset... Reconnecting\n")
            time.sleep(2)
            self.initConn()


    def sendData(self):
        '''
        sendData handles information to and from the server once a connection has been made
        '''

        while not self.kill.kill:
            try:
                #We want to send the data at precise intervals, so we'll have the loop sleep at time = 1/updatrate - looptime
                tic = time.time()
                #get updates from the flight controller
                self.update()
                #convert to JSON and send to server

                self.sock.sendall(json.dumps(self.sendDict).encode("utf-8"))

                                                          #DANGER! DANGER!: make sure the timeout is > than update rate
                r, _, _ = select.select([self.sock],[],[], 2/self.updateRate)
                #if there is a response
                if r:
                    #recieve the data
                    data = self.sock.recv(1024)
                    #decode the data
                    try:
                        _data = json.loads(data.decode("utf-8"))
                        #Add configurable stuff here. for example if you wanted to be able to control X on the client side, if _data[0]== 'X':
                        #                                                                                                       self.X = int(_data[1])
                        if _data[0] == 'rate':
                            print("Instructions from GCS:")
                            print(_data)
                            self.updateRate = int(_data[1])
                    except:
                        print("Something went wrong decoding message!")
                        pass
                toc =  time.time() - tic
                #try and except is due to
                try:
                    time.sleep((1 / self.updateRate)  - toc)
                except:
                    pass
                

            except BrokenPipeError:
                print("Connection Reset... Reconnecting\n")
                self.sock.close()
                time.sleep(2.2)
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.initConn()

            except ConnectionResetError:
                print("Connection Reset... Reconnecting\n")
                self.sock.close()
                time.sleep(2.2)
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.initConn()

        self.closeConnections()

    def closeConnections(self):

        print("closing connections")
        if self.ui:
            self.ui.kill = True
        self.v2vComms.kill = True
        self.v2vComms.closeAllConns()
        self.v2vComms.sock.close()
        self.sock.close()








#TODO: i2c exception handling


   #TODO: create static /dev/tty (done! not static ttyACM, instead search for which ACM has the FC)
