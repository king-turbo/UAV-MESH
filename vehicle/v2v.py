import socket
import os
import subprocess
import json
import select
from multiprocessing import Pool
import _thread
import threading
import time
from gcs.server import VehicleClass as vc
import sys

class V2V:

    def __init__(self, localIP, name, vehicleType):

        self.HOST = localIP
        self.gcsList = []
        self.nodeList = [[{"fakename":"dummy"},"111.111.111.111"]]
        self.ipDict = {}
        self.PORT = 65432
        self.name = name
        self.vehicleType = vehicleType
        self.REQUEST_PROBE = {"$probe" : "UAV"}
        self.PROBE_REPLY = {"UAV" : name}
        self.initConnToUav = {"$connect" : 1, "type": vehicleType, "name" : name}

        self.uavOutgoingSocketDict = {}
        self.listeningSockets = []
        self.uavs = {}
        self.kill = False
        # self.initListenSocket()

    def initListenSocket(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.HOST, self.PORT))
        listenThread = threading.Thread(target=self.listen)
        listenThread.daemon = True
        listenThread.start()
        # _thread.start_new_thread(self.listen, ())


    def listen(self):

        self.sock.listen(5)
        try:
            while not self.kill:
                conn, addr = self.sock.accept()
                threading.Thread(target=self.talkToNewNode, args=(conn, addr)).start()
                # _thread.start_new_thread(self.talkToNewNode, (conn, addr))
        except:
            print("exception in v2v listen")

    def talkToNewNode(self, conn, addr):
        print("Connected to new node!")
        try:
            data = conn.recv(1024)
            if data:
                _data = json.loads(data.decode("utf-8"))
                if "$probe" in _data:
                    conn.sendall(self.probeReply())
                    conn.close()
                if "$connect" in _data:
                    
                    conn.sendall(self.successConnReply())
                    
                    #incoming socks
                    self.listeningSockets.append([conn, addr])
                    #need to rearrange this.... maybe?
                    threading.Thread(target=self.listenToVehicle, args=((conn, _data["name"],addr[0],_data["type"]))).start()
                    # _thread.start_new_thread(self.listenToVehicle, (conn, _data["name"],addr[0],_data["type"]))
                    print("Received request to connect from node:")
                    print(_data)
                    if _data["name"] not in self.uavOutgoingSocketDict:
                        #outgoing socks
                        success, sock = self.connect2UAV(addr[0])
                        
                        if success:
                                                                #outgoing
                            self.uavOutgoingSocketDict[_data["name"]] = [addr[0], sock]                            
                            self.ipDict[addr[0]] = _data["name"]
                                
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
                if any(_ip in addr for addr in self.ipDict):
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
                    self.ipDict[neighbor[1]] = neighbor[0]["GCS"]
                if "UAV" in neighbor[0]:
                    success, sock = self.connect2UAV(neighbor[1])
                    #connect to the new UAVs
                    #if succesfully connected, then append to nodelist
                    if success:
                        if neighbor[0]["UAV"] not in self.ipDict:
                            self.ipDict[neighbor[1]] = neighbor[0]["UAV"]
                            
                                                                #outgoing
                        self.uavOutgoingSocketDict[neighbor[0]["UAV"]] = [neighbor[1], sock]
                    else:
                        sock.close()
        p.terminate()
        p.join()

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
                                            #ip, sock
        _uavs = [(k,v) for k, v in self.uavOutgoingSocketDict.items()]

        for u in _uavs:
            try:
                u[1][1].sendall(json.dumps(msg).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError):
                print("Outgoing connection to " + u[0] + "closed.")
                u[1][1].close()
                self.uavOutgoingSocketDict[u[0]][1].close()
                del self.uavOutgoingSocketDict[u[0]]
                try:
                    del self.ipDict[u[1][0]]
                except:
                    pass

        # for node in self.uavOutgoingSocketDict:
        #     sock = self.uavOutgoingSocketDict[node][1]
        #     try:
        #         sock.sendall(json.dumps(msg).encode("utf-8"))
        #     except (BrokenPipeError, ConnectionResetError):
        #         sock.close()
        #         del self.uavOutgoingSocketDict[node]
        #         try:
        #             del self.ipDict[node[0]]
        #         except:
        #             pass


    def closeAllConns(self):

        self.sock.close()
        for node in self.listeningSockets:
            try:
                node[0].close()
            except:
                pass
        for node in self.uavOutgoingSocketDict:
            try:
                self.uavOutgoingSocketDict[node].close()
            except:
                pass
        


        print("Closed all v2v Conns")

    def listenToVehicle(self,conn, name, ip, vehicleType):

        self.uavs[name] = vc(name, ip, vehicleType)
        _empty_msg=[]
        while not self.kill:

            try:
                # This waits for data with a timeout of 2 seconds
                r, _, _ = select.select([conn], [], [], 6)
                # if there is data
                if r:
                    data = conn.recv(1024)
                    print(data)

                    if data == b'':
                        _empty_msg.append(1)
                    else:
                        _empty_msg=[]
                    if len(_empty_msg) >= 100:
                        print("\n " + name + " has disconnected!")
                        conn.close()
                        del self.ipDict[ip]
                        break

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

                else:
                    print("\n " + name + " has disconnected!")
                    conn.close()
                    try:
                        del self.ipDict[ip]
                    except:
                        pass
                    break

            except Exception as e:
                print(e)
                print("exception in v2v listen2vehicles")
                conn.close()
                break
        conn.close()



def probe(ip):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect((ip, 65432))
            s.sendall(json.dumps({"$probe" : "UAV"}).encode("utf-8"))
            r, _, _ = select.select([s], [], [], .2)
            if r:
                data = json.loads(s.recv(1024).decode("utf-8"))
                print("Probed node:")
                print(data)
                # newNeighbors.append([data, ip])
                s.close()
                return [data, ip]
        except:
            pass
    s.close()
    print("ended")
