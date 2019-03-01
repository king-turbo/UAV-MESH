import socket
import os
import subprocess
import json
import select
from multiprocessing import Pool


class V2V:

    def __init__(self, localIP, localPort, name, vehicleType):

        self.ip = localIP
        self.port = localPort
        self.name = name
        self.vehicleType = vehicleType
        self.lat, self.lon, self.alt, self.heading = 0, 0, 0, 0

    def replyMsg(self, *args):
        return ({self.name : [self.vehicleType, self.lat, self.lon, self.alt, self.heading, *args]})

    def run(self):
        while True:

            pass


