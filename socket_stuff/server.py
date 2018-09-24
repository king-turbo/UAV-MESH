
import socket
import json


class VehicleObj:

    def __init__(self, name, ip, vehicleType, connObj):
        self.name = name
        self.ip = ip
        self.vehicleType = vehicleType
        self.mode = "default"
        self.connObj = connObj

class Server:

    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.agents = {}
        self.ipDict = {}
        self.initMsgFrmSrv = {"mode" : "default", "freq" : 5}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.HOST, self.PORT))
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.listen(5)

    def initializeNode(self, conn, addr):

        data = conn.recv(1024)
        if data:
            _data = json.loads(data.decode("utf-8"))
            #dict with ip addresses and the name of the agent
            self.ipDict[addr[0]] = _data["name"]
            #agent dict with names as keys and a vehicle class as value
            self.agents[_data["name"]] = (VehicleObj(_data["name"], addr[0], _data["type"], conn))
            conn.sendall(json.dumps(self.initMsgFrmSrv).encode("utf-8"))

    def parseData(self, conn, addr):

        data = conn.recv(1024)
        if data:
            _data = json.loads(data.decode("utf-8"))
            if "close connection" in _data:
                del self.ipDict[addr[0]]
            else:
                #pass connection and vehicle object to the reply function
                self.replyMsg(conn, self.agents[self.ipDict[addr[0]]])
                pass


    def listen(self):
        self.conn, addr = self.sock.accept()  # this may need to get moved later when we switch to threading
        while True:
            if addr[0] in self.ipDict:
                self.parseData(self.conn, addr)
            else:
                self.initializeNode(self.conn, addr)

    def replyMsg(self, conn, agent):
        #send back a 0 if there is nothing to change
        print("in reply func")
        if agent.mode == "default":
            print("replying")
            conn.sendall(json.dumps('0').encode("utf-8"))


if __name__=="__main__":

    HOST = '192.168.254.11'
    PORT = 65432
    queenB = Server(HOST, PORT)

    queenB.listen()