import socket
import os
import subprocess
import json
import select
from multiprocessing import Pool
import _thread
import time



class NodeFinder:

    def __init__(self, localIP, name):

        self.HOST = localIP
        self.nodeList = []
        self.PORT = 65432  # all "server" sockets will have 33333
        self.name = name
        self.REQUEST_PROBE = {"$probe" : "UAV"}
        self.probe_REPLY = {name: "UAV"}

        # self.initListenSocket()

    def initListenSocket(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.HOST, self.PORT))


    def listen(self):

        self.sock.listen(5)
        while True:
            conn, addr = self.sock.accept()
            if addr[0] not in self.nodeList[1]:
                _thread.start_new_thread(self.talkToNode, (conn, addr))

    def talkToNode(self, conn, addr):
        try:
            data = conn.recv(1024)
            if data:
                _data = json.loads(data.decode("utf-8"))
                if "$probe" in _data:
                    conn.sendall(self.probeReply())
        except:
            pass

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
                else:
                    newIPs.append(_ip)
                _ip = ''
            elif flag == True:
                _ip += char
            elif char == '(':
                flag = True
        #gets ride of "www.nmap.com" and "0 hosts up"
        del newIPs[0]
        del newIPs[-1]

        print (newIPs)

        #multiprocessing to probe all the ips. makes it about 4x as fast
        p = Pool(5)
        newNeighbors = p.map(probe, newIPs)
        print(newNeighbors)
        for neighbor in newNeighbors:
            if neighbor != None:
                self.nodeList.append([neighbor[0],neighbor[1]])

    def returnGCS(self):
        _returnList = []
        for node in self.nodeList:
            if "GCS" in node[0]:
                                     #name of gcs   #ip
                _returnList.append([node[0]["GCS"],node[1]])
        return _returnList




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