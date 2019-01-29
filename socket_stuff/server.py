import socket
import json
import _thread
import select
import multiprocessing as mp
import time
from datetime import datetime, timezone
from userInterface import UI
from oneskyapi import OneSkyAPI
from localIP import myLocalIP
from localIP import myLocalPort
class VehicleObj:

    def __init__(self, name, ip, vehicleType):
        self.name = name
        self.ip = ip
        self.vehicleType = vehicleType
        self.mode = "default"
        self.updateRate = 0
        self.lat = 0
        self.lon = 0
        self.alt = 0
        self.GUFI = ''



class Server:

    def __init__(self, HOST, PORT, oneskyAPI, utmUpdate = True, verbose = True):

        self.HOST = HOST
        self.PORT = PORT
        self.agents = {}
        self.ipDict = {}
        self.initMsgFrmSrv = {"mode" : "default", "freq" : 5}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.HOST, self.PORT))
        self.utm = oneskyAPI
        self.utmUpdate = utmUpdate
        self.verbose = verbose

    def initializeNode(self, conn, addr):
        try:
            data = conn.recv(1024)
            if data:
                _data = json.loads(data.decode("utf-8"))
                #dict with ip addresses and the name of the agent

                #agent dict with names as keys and a vehicle class as value
                print(_data)
                if _data["name"] not in self.agents:
                    print("new agent")
                    self.ipDict[addr[0]] = _data["name"]
                    self.agents[_data["name"]] = (VehicleObj(_data["name"], addr[0], _data["type"]))

                    print(_data)

                    self.createUTMPointFlight(_data["name"],_data["lon"],_data["lat"],_data["alt"])

                elif self.agents[_data["name"]].ip != addr[0]:
                    print("need a unique name")  #TODO: make a fancy exception thing
                    conn.close()
                    return None
                elif self.agents[_data["name"]].ip == addr[0]:
                    self.ipDict[addr[0]] = _data["name"]

                a = json.dumps({"mode" : "default", "freq" : 5}).encode("utf-8")

                conn.sendall(a)
                self.clientHandler(conn, addr)
        except:
            conn.close()

    def createUTMPointFlight(self, name, lon, lat, alt):
        print("are we here?")
        self.agents[name].GUFI = self.utm.createPointFlight(name, lon, lat, alt)
        print(self.agents[name].GUFI)

    def UTMTelemUpdate(self):

        while True:
            for agent in self.agents:
                try:
                    self.utm.updateTelemetry(self.agents[agent].GUFI, self.agents[agent].lon, self.agents[agent].lat, self.agents[agent].alt)
                except:
                    pass

    def clientHandler(self, conn, addr):
        oPipe = False
        while True:

            #THIS HANDLES INCOMING DATA FROM PRINCESS

            r, _, _ = select.select([conn], [], [], 2)
            if r:
                data = conn.recv(1024)
                if data:
                    _data = json.loads(data.decode("utf-8"))

            ##THIS SECTION WILL GET THE DATA FROM THE PRINCESSES


                    self.agents[self.ipDict[addr[0]]].lon = _data["lon"]
                    self.agents[self.ipDict[addr[0]]].lat = _data["lat"]
                    self.agents[self.ipDict[addr[0]]].alt = _data["alt"]
                    self.agents[self.ipDict[addr[0]]].updateRate = _data["updateRate"]
                    self.agents[self.ipDict[addr[0]]].mode = _data["mode"]


            ##THIS SECTION WILL TELL THE PRINCESSES WHAT TO DO

                    if "close connection" not in _data:
                        if self.outputPipe.poll():
                            oPipe = self.outputPipe.recv()
                        if oPipe:
                            if oPipe[0] == self.ipDict[addr[0]]:
                                self.replyMsg(conn, oPipe[1:])
                            else:
                                self.replyMsg(conn, [0])
                        else:
                            self.replyMsg(conn,[0])

                    else:
                        print("shits getting del")
                        del self.ipDict[addr[0]]
                        conn.close()
                        break

            else:
                print("removing connection")
                conn.close()
                del self.ipDict[addr[0]]
                break

            self.inputPipe.send(self.agents)
            oPipe = False

    def replyMsg(self, conn, msg):
        conn.sendall(json.dumps(msg).encode("utf-8"))

    def listen(self, inPipe, outPipe):
        print("Starting Server")

        if self.utmUpdate:
            _thread.start_new_thread(self.UTMTelemUpdate, ())

        self.inputPipe = inPipe
        self.outputPipe = outPipe
        self.inputPipe.send('')
        self.sock.listen(5)
        while True:
            conn, addr = self.sock.accept()
            # conn.settimeout(3)
            if addr[0] not in self.ipDict:
                _thread.start_new_thread(self.initializeNode, (conn, addr))


if __name__=="__main__":

    '''
    The user interface and server loops run on different processes.
    '''



    with open("mwalton.token", "r") as toke:
        token = toke.read()

    HOST = myLocalIP
    PORT = myLocalPort
    input_parent_conn, input_child_conn = mp.Pipe()
    output_parent_conn, output_child_conn = mp.Pipe()

    #create api interface with onesky
    utm = OneSkyAPI(token)

    ui = UI(input_child_conn, output_parent_conn)
    queenB = Server(HOST, PORT, utm, utmUpdate = False, verbose=True,)

    listenProc = mp.Process(target= queenB.listen, args=(input_parent_conn, output_child_conn)).start()
    #
    ui.start()

    # queenB.listen(parent_conn)
    # while True:
    #
    #     time.sleep(.5)
    #     try:
    #         a = parent_conn.recv()
    #         print(a['rapunzel'].ip)
    #     except:
    #         pass

