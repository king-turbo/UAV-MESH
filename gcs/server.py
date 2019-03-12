import socket
import json
import sys, getopt
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import _thread
import select
import multiprocessing as mp
import time
from datetime import datetime, timezone
from gcs.user_interface import UI
from gcs.onesky_api import OneSkyAPI
import subprocess

class VehicleClass:
    '''
    The VehicleClass class is just a container of information for each vehicle that will be stored in a dictionary
    There are no methods, just attributes. This is just so we can pull the vehicle object from the
    dictionary and find values by doing something like: vehicleObject.valueWeWant
    I should be using a dictionary but I dont wanna ¯\_(._. ' )_/¯
    '''

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
        self.heading = 0



class Server:
    '''
    The server class is only instantiated once and handles clients that are located on the UAV.
    The server class requires a server host and port, UTM api object, and pipes to the UI
    To operate the Server class, first instantiate it, then run the listen method. For example:

    myServerObj = Server(host, port, utmAPI, pipe_in, pipe_out)
    myServerObj.listen()

    '''

    def __init__(self, HOST, PORT, oneskyAPI, inPipe, outPipe, gcsName, utmUpdate = True, verbose = True):

        self.gcsName = gcsName
        self.HOST = HOST
        self.PORT = PORT
        #the agent dictionary has the format: {nameOfClient : <VehicleClass>}
        #the VehicleClass has all the important information like vehicle.lat, vehicle.lon, vehicle.mode, etc
        self.agents = {}
        #the ipDict has the format: {123.456.123.456 : nameOfClient}
        #this allows easy search for ip/client names
        #there's probably a better way than having separate dictionaries, but I like it this way
        self.ipDict = {}
        #the initMsgFrmSrv is the first message the client will recieve from the server
        self.initMsgFrmSrv = {"mode" : "default", "freq" : 5}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.HOST, self.PORT))
        self.utm = oneskyAPI
        self.utmUpdate = utmUpdate
        self.verbose = verbose
        self.inputPipe = inPipe
        self.outputPipe = outPipe

        if self.utmUpdate:
            _thread.start_new_thread(self.UTMTelemUpdate, ())

    def initializeNode(self, conn, addr):

        try:
            #receive data from socket
            data = conn.recv(1024)
            #if there's anything to recieve
            if data:
                #decode data
                _data = json.loads(data.decode("utf-8"))

                if "$probe" in _data:

                    conn.sendall(self.probeReply())
                    conn.close()

                elif "$connect" in _data:
                    #if the connection is new
                    if _data["name"] not in self.agents:
                        print("{} has connected at Lat:{}, Lon:{}, Alt:{}.".format(_data["name"],_data["lat"],_data["lon"],_data["alt"]))
                        #store the new connection name in the IP dictionary
                        self.ipDict[addr[0]] = _data["name"]
                        #also store the new connetion's name in the agents dictionary. the key is the name and the value is
                        #the vehicle class object. This allows for easy vehicle look ups
                        self.agents[_data["name"]] = (VehicleClass(_data["name"], addr[0], _data["type"]))

                        #if we are updated to the UTM
                        if self.utmUpdate:
                            #then create a new point flight to the UTM system
                            self.createUTMPointFlight(_data["name"],_data["lon"],_data["lat"],_data["alt"])
                    #if the connection's name exists, but the IP addresses are the same, then this is indicative of
                    #two vehicles operating with the same name. The connection is closed.
                    elif self.agents[_data["name"]].ip != addr[0]:
                        print("\n A vehicle attempted to connect with a name already in use")  #TODO: make a fancy exception thing
                        conn.close()

                    #if the vehicle's name is already stored and the IP addresses match, this means that
                    #the vehicle lost connection and reconnected
                    elif self.agents[_data["name"]].ip == addr[0]:
                        print("\n{} has reconnected.".format(_data["name"]))
                        self.ipDict[addr[0]] = _data["name"]
                    a = json.dumps({"mode" : "default", "freq" : 5}).encode("utf-8")
                    conn.sendall(a)
                    self.clientHandler(conn, addr) #TODO: check for GUFI, remake if needed
                else:
                    conn.close()
            return None
        except Exception as e:
            print(e)
            conn.close()

    def probeReply(self):

        return json.dumps({"GCS" : self.gcsName}).encode("utf-8")

    def createUTMPointFlight(self, name, lon, lat, alt):
        '''
        This function calls the createPointFlight method from the utm class. It store the GUFI (unique flight identifier)
        to the vehicle object in the agent dictionary
        '''
        self.agents[name].GUFI = self.utm.createPointFlight(name, lon, lat, alt)
        print("Created GUFI:" + self.agents[name].GUFI)

    def UTMTelemUpdate(self):
        '''
        This runs on a separate thread. It updates telemetry to the UTM
        '''
        while True:

            for agent in self.agents:
                try:
                    self.utm.updateTelemetry(self.agents[agent].GUFI, self.agents[agent].lon, self.agents[agent].lat, self.agents[agent].alt)
                except:
                    pass

        #TODO: Add a way to handle onesky replys

    def clientHandler(self, conn, addr):
        '''
        The clientHandler method is a while 1 loop that handles information from the user interface to the server to
        the client and back again. Each clientHandler loop is handled on a thread which is spawned from the 'listen' method
        So each clientHandler only handles one client.
        '''
        oPipe = False
        while True:
            
            #This waits for data with a timeout of 2 seconds
            
            r, _, _ = select.select([conn], [], [], 2)
            
            #if there is data
            if r:
                
                data = conn.recv(1024)

                if data:
                   try:
                       _data = json.loads(data.decode("utf-8"))
                       
                            #The incoming data is in the form of a dictionary. The information from the client is
                        #then stored in the vehicle object which is stored in the agent dictionary

                       self.agents[self.ipDict[addr[0]]].lon = _data["lon"]
                       self.agents[self.ipDict[addr[0]]].lat = _data["lat"]
                       self.agents[self.ipDict[addr[0]]].alt = _data["alt"]
                       self.agents[self.ipDict[addr[0]]].updateRate = _data["updateRate"]
                       self.agents[self.ipDict[addr[0]]].mode = _data["mode"]

                       #This next section of code will send instructions to the vehicle

                       #if the incoming data does not ask to close the connection
                       if "close connection" not in _data:
                           #if there is data in the pipe from the user interface
                           if self.outputPipe.poll():
                               #read the data
                               oPipe = self.outputPipe.recv()
                           #is this if necessary? TODO: test if this if is necessary
                           if oPipe:
                               #The ipDict has the format {ipAddress : nameOfClient}, oPipe[0] should be the name of client
                               #when a user enters "cinerella.rate.5", "cinderella" is oPipe[0]. if cinerella == the name
                               #that this clientHandler is working with, then:
                               if oPipe[0] == self.ipDict[addr[0]]:
                                   #send the remained of the message to the client, in the above example's case: "rate.5"
                                   print(oPipe[1:])
                                   self.replyMsg(conn, oPipe[1:])
                               else:
                                   #This (and the following else!)sends a 0 back to the client to let it know everything is OK! Maybe I should change
                                   #to a 1?
                                   
                                   self.replyMsg(conn, [0])
                                   
                           else:
                               
                               self.replyMsg(conn,[0])
                               
                       else:
                           #client requested removal, remove
                           print("Removed connection at Client's Request")
                           del self.ipDict[addr[0]]
                           conn.close()
                           break
                   except Exception as e:

                       print(e)
                       pass


                else:
                    pass

            else:
                #if the connection has timed out, then remove it from the ipDict. #TODO: make sure this is what we want
                print("\n " + self.ipDict[addr[0]] +"has disconnected!")
                conn.close()
                del self.ipDict[addr[0]]
                break

            #This sends the updated agents dictionary back to the user interface TODO: Is there a better way to do this?
            
            self.inputPipe.send(self.agents)
            
            oPipe = False
            
                  
    def replyMsg(self, conn, msg):
        #sends message to the client
        conn.sendall(json.dumps(msg).encode("utf-8"))

    def closeConnection(self):
        self.sock.close()

    def listen(self):
        '''
        First method that is ran. Spawns new threads for each client.
        '''
        print("\nStarting Server")


        #gonna have to create more sockets eventually
        self.conns = []
        self.inputPipe.send('')
        self.sock.listen(5)
        try:
            while True:
                conn, addr = self.sock.accept()
                self.conns.append(conn)
               # conn.settimeout(1.4)
                if addr[0] not in self.ipDict:
                    _thread.start_new_thread(self.initializeNode, (conn, addr))
        except:
            self.sock.close()


def getLocalIP(device=''):

    if os.name == 'nt':
        return socket.gethostbyname(socket.gethostname())
    if os.name == 'posix':
        subprocess.call(['.././sysinfo.sh'])
        time.sleep(.00001)
        peripherals = [line.rstrip('\n') for line in open('sysdisc.txt')]
        if device == 'eth0':
            if peripherals[2] == 'None':
                return socket.gethostbyname(socket.gethostname())   #all this shit needs to be tested
            else:
                return peripherals[2]
        if device == 'bat0':
            return peripherals[3]
        if device == 'wlan':
            return peripherals[5]



if __name__=="__main__":

    '''
    The user interface and server loops run on different processes.
    '''

    #store JWT into 'token'
    with open("mwalton.token", "r") as toke:
        token = toke.read()

    #Get the IP and Port of server from the localIP py file

    HOST = getLocalIP(device="eth0")
    PORT = 65432

    #These two pipes send data from the UI to the clientHandler server loop
    input_parent_conn, input_child_conn = mp.Pipe()
    output_parent_conn, output_child_conn = mp.Pipe()

    #create api interface with onesky
    utm = OneSkyAPI(token)

    #instantiate the UI with the pipes
    ui = UI(input_child_conn, output_parent_conn)
    #instantiate the server
    try:
        queenB = Server(HOST, PORT, utm, input_parent_conn, output_child_conn,"castle", utmUpdate = True, verbose=True, )
        #start the listening method with pipes
        listenProc = mp.Process(target= queenB.listen, args=())
        listenProc.start()

        ui.start()
        listenProc.join()

    except Exception as e:
        for conn in queenB.conns:
            conn.close()
        queenB.closeConnection()
        listenProc.join()

        print(e)


    '''
    TODO: work on exception handling
    TODO: work on reconnect for client side (did this now need to test for different types of comms failures)
    TODO: Need to figure out GUFI handling for disconnected vehicles/server failure
    TODO: properly get rid of threads and processes 
    TODO: switch from _threading crap to the ez thread
    '''

