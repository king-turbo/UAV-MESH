import socket
import json
import time
from dronekit import Vehicle, connect
import select
import sys
class Drone(Vehicle):

    def __init__(self, *args):

        super(Drone, self).__init__(*args)
        self.sendDict = {}

    def toJSON(self):

        return json.dumps(self.sendDict, default=lambda o: o.__dict__)

    def updateUAVGPS(self):

        self.global_loc = self.location.global_frame
        return (self.global_loc.lon, self.global_loc.lat, self.global_loc.alt)

class DummyDrone:

    def __init__(self):
        self.lon = 0
        self.lat = 0
        self.alt = 0

    def updateUAVGPS(self):
        return (self.lon, self.lat, self.alt)


class Client():

    def __init__(self, HOST, PORT, type, name):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = HOST
        self.PORT = PORT
        self.initMsgFrmClient = {"type" : type, "name" : name}
        self.status = "default"
        self.updateRate = 5
        self.sending = True
        self.name = name
        self.type = type


    def initVehicle(self):
        try:
            self.uav = connect('/dev/ttyACM1', wait_ready=True, vehicle_class=Drone)
            self.lon, self.lat, self.alt = self.uav.updateUAVGPS()
            if self.lon != 0:

                self.initMsgFrmClient["lon"] = self.lon
                self.initMsgFrmClient["lat"] = self.lat
                self.initMsgFrmClient["alt"] = self.alt
            else:
                print("GPS lock is bad")

        except:


            self.uav = DummyDrone()
            self.lon, self.lat, self.alt = self.uav.updateUAVGPS()
            self.initMsgFrmClient["lon"] = self.lon
            self.initMsgFrmClient["lat"] = self.lat
            self.initMsgFrmClient["alt"] = self.alt

    def update(self):

        self.lon, self.lat, self.alt = self.uav.updateUAVGPS()

        self.sendDict = {"name" : self.name,
                         "mode" : self.mode,
                         "updateRate" : self.updateRate,
                         "lon" : self.lon,
                         "lat" : self.lat,
                         "alt": self.alt}

    def initConn(self):

        self.sock.connect((self.HOST, self.PORT))
        self.sock.sendall(json.dumps(self.initMsgFrmClient).encode("utf-8"))
        data = self.sock.recv(1024)
        print(data)
        _data = json.loads(data.decode("utf-8"))
        self.updateRate = _data["freq"]
        self.mode = _data["mode"]
        if _data["mode"] == "default":
            self.sendData()

    def sendData(self):

        while True:
            try:
                tic = time.time()
                self.update()
                self.sock.sendall(json.dumps(self.sendDict).encode("utf-8"))
                r, _, _ = select.select([self.sock],[],[], .05)
                if r:
                    data = self.sock.recv(1024)
                    print(data)
                    _data = json.loads(data.decode("utf-8"))
                    if _data[0] == 'rate':
                        self.updateRate = int(_data[1])
                    #add all the other configurable crap here


                toc=  time.time() - tic
                time.sleep((1 / self.updateRate)  - toc)

            except KeyboardInterrupt:

                self.closeConnection()

    def closeConnection(self):

        self.sock.close()


if __name__=="__main__":

    HOST = '192.168.254.11'
    PORT = 65432
    node = Client(HOST,PORT,"MULTI_ROTOR","cinderella")
    node.initVehicle()
    node.initConn()
