import socket
import os
import subprocess
import json
import select
from multiprocessing import Pool
import _thread
import time
from gcs.server import VehicleClass as vc


class V2V:

    def __init__(self, localIP, name, vehicleType):

        self.HOST = localIP
        self.gcsList = []
        self.nodeList = [[{"fakename":"dummy"},"111.111.111.111"]]
        self.PORT = 65432
        self.name = name
        self.vehicleType = vehicleType
        self.REQUEST_PROBE = {"$probe" : "UAV"}
        self.PROBE_REPLY = {"UAV" : name}
        self.initConnToUav = {"$connect" : 1, "type": vehicleType, "name" : name}

        self.uavOutgoingSocketDict = {}
        self.listeningSockets = []
        self.uavs = {}
        # self.initListenSocket()

    def initListenSocket(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.HOST, self.PORT))
        _thread.start_new_thread(self.listen, ())


    def listen(self):

        self.sock.listen(5)
        while True:
            conn, addr = self.sock.accept()

            _thread.start_new_thread(self.talkToNewNode, (conn, addr))

    def talkToNewNode(self, conn, addr):
        print("NEW NODE!!")
        try:
            data = conn.recv(1024)
            if data:
                _data = json.loads(data.decode("utf-8"))
                if "$probe" in _data:
                    conn.sendall(self.probeReply())
                    conn.close()
                if "$connect" in _data:
                    print("we are in connecting!")
                    conn.sendall(self.successConnReply())
                    print("we have replied")
                    #incoming socks
                    self.listeningSockets.append([conn, addr])
                    #need to rearrange this.... maybe?
                    _thread.start_new_thread(self.listenToVehicle, (conn, _data["name"],addr[0],_data["type"]))
                    print(_data)
                    if _data["name"] not in self.uavOutgoingSocketDict:
                        #outgoing socks
                        success, sock = self.connect2UAV(addr[0])
                        print(success)
                        if success:
                                                                #outgoing
                            self.uavOutgoingSocketDict[_data["name"]] = [addr[0], sock]
                            if _data["name"] not in self.nodeList:
                                self.nodeList.append([_data["name"], addr[0]])


                                #this means i will need to remove key-value pair if outgoing sock is lost
                                #also need to remove name in nodeList if disconnected

        except:
            pass


    # def nodeHandler(self):
    #
    def successConnReply(self):
        return json.dumps({"$success": 1}).encode("utf-8")

    def probeReply(self):
        return json.dumps({"UAV" : self.name}).encode("utf-8")

    def findNodes(self):
        newIPs = []
        a = ["nmap", "-sL", "192.168.254.*"]
        b = subprocess.check_output(a).decode("utf-8").strip()
        _ip = ''
        flag = False
        for char in b:
            if char == ')':
                flag = False
                if any(_ip in addr for addr in self.nodeList):
                    pass
                elif _ip != self.HOST:
                    newIPs.append(_ip)
                _ip = ''
            elif flag == True:
                _ip += char
            elif char == '(':
                flag = True
        #gets rid of "www.nmap.com" and "0 hosts up"
        del newIPs[0]
        del newIPs[-1]


        #multiprocessing to probe all the ips. makes it about 4x as fast
        p = Pool(5)
        newNeighbors = p.map(probe, newIPs)

        for neighbor in newNeighbors:
            if neighbor != None:
                                       #node name       #ip
                if "GCS" in neighbor[0]:
                    self.gcsList.append([neighbor[0]["GCS"],neighbor[1]])
                    self.nodeList.append([neighbor[0]["GCS"],neighbor[1]])
                if "UAV" in neighbor[0]:
                    success, sock = self.connect2UAV(neighbor[1])
                    #connect to the new UAVs
                    #if succesfully connected, then append to nodelist
                    if success:
                        if neighbor[0]["UAV"] not in self.nodeList:
                            self.nodeList.append([neighbor[0]["UAV"],neighbor[1]])
                                                                #outgoing
                        self.uavOutgoingSocketDict[neighbor[0]["UAV"]] = [neighbor[1], sock]

    def connect2UAV(self,ip):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, 65432))
        sock.sendall(json.dumps(self.initConnToUav).encode("utf-8"))

        r, _, _ = select.select([sock], [], [], 2)
        if r:
            data = json.loads(sock.recv(1024).decode("utf-8"))
            if "$success" in data:
                return True, sock
            else:
                sock.close()
                return False, 0

        

    def returnGCS(self):

        return self.gcsList

    def msgAllUavs(self, lat, lon, alt, heading, **kwargs):
        msg = ({"name": self.name,
                 "vehicleType" : self.vehicleType,
                "lat" : lat,
                "lon": lon,
                "alt": alt,
                "heading": heading,
                **kwargs})

        #maybe do this multiprocessing?
        for node in self.uavOutgoingSocketDict:
            sock=self.uavOutgoingSocketDict[node][1]
            sock.sendall(json.dumps(msg).encode("utf-8"))

    def listenToVehicle(self,conn, name, ip, vehicleType):

        self.uavs[name] = vc(name,ip, vehicleType)
        while True:

            # This waits for data with a timeout of 2 seconds

            r, _, _ = select.select([conn], [], [], 2)

            # if there is data
            if r:

                data = conn.recv(1024)

                if data:
                    try:
                        _data = json.loads(data.decode("utf-8"))

                        self.uavs[name].lon = _data["lon"]
                        self.uavs[name].lat = _data["lat"]
                        self.uavs[name].alt = _data["alt"]
                        self.uavs[name].heading  = _data["heading"]
                    except Exception as e:
                        print("exception occured in listenToVehicle method")
                        print(e)
                        pass








def probe(ip):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect((ip, 65432))
            s.sendall(json.dumps({"$probe": "UAV"}).encode("utf-8"))
            r, _, _ = select.select([s], [], [], .2)
            if r:
                data = json.loads(s.recv(1024).decode("utf-8"))
                print(data)
                # newNeighbors.append([data, ip])

                return [data, ip]

        except:
            pass
    s.close()