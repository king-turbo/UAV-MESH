import socket
import json
import _thread
import select

class VehicleObj:

    def __init__(self, name, ip, vehicleType):
        self.name = name
        self.ip = ip
        self.vehicleType = vehicleType
        self.mode = "default"


class Server:

    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.agents = {}
        self.ipDict = {}
        self.initMsgFrmSrv = {"mode" : "default", "freq" : 5}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.HOST, self.PORT))

    def initializeNode(self, conn, addr):
        try:
            data = conn.recv(1024)
            if data:
                _data = json.loads(data.decode("utf-8"))
                print(_data)
                #dict with ip addresses and the name of the agent
                self.ipDict[addr[0]] = _data["name"]
                #agent dict with names as keys and a vehicle class as value
                if _data["name"] not in self.agents:
                    self.agents[_data["name"]] = (VehicleObj(_data["name"], addr[0], _data["type"]))
                elif self.agents[_data["name"].ip != addr[0]]:
                    print("need a unique name")  #TODO: make a fancy exception thing
                    conn.close()
                    return None

                a = json.dumps({"mode" : "default", "freq" : 5}).encode("utf-8")
                conn.sendall(a)
                print("what")
                self.clientHandler(conn, addr)
        except:
            conn.close()


    def clientHandler(self, conn, addr):
        print("hey")
        while True:
            r, _, _ = select.select([conn], [], [], 2)
            if r:
                data = conn.recv(1024)
                if data:
                    _data = json.loads(data.decode("utf-8"))
                    if "close connection" in _data:
                        del self.ipDict[addr[0]]
                        conn.close()
                        break
                    else:
                        # pass connection and vehicle object to the reply function
                        self.replyMsg(conn, self.agents[self.ipDict[addr[0]]])
                        pass
            else:
                print("removing connection")
                conn.close()
                del self.ipDict[addr[0]]
                break


    def listen(self):
        self.sock.listen(5)
        while True:
            conn, addr = self.sock.accept()  # this may need to get moved later when we switch to threadingls
            # conn.settimeout(3)
            if addr[0] not in self.ipDict:
                _thread.start_new_thread(self.initializeNode, (conn, addr))




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


