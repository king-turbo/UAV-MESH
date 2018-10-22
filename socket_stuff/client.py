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

    def updateDrone(self):

        self.global_loc = self.location.global_frame

class DummyDrone():

    def __init__(self):
        self.global_loc = 12345.12

    def updateDrone(self):
        self.global_loc = 9999945.12


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
            self.uav = connect('/dev/ttyACM0', wait_ready=True, vehicle_class=Drone)
        except:
            self.uav = DummyDrone()

    def update(self):
        self.uav.updateDrone()
        self.sendDict = {"name" : self.name,
                         "mode" : self.mode,
                         "updateRate" : self.updateRate,
                         "GPS" : self.uav.global_loc }

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


if __name__=="__main__":

    HOST = '192.168.254.11'
    PORT = 65432
    node = Client(HOST,PORT,"UAV","rapunzel")
    node.initVehicle()
    node.initConn()
