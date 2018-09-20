import socket
import json
import sys
from io import StringIO

def neat_data(data):
    data = json.loads(data.decode("utf-8"))
    with open('received.json', 'w') as outfile:
        json.dump(data,outfile, indent=4, sort_keys=True)
    print("dumppppppppppppppppp")

IP_ADDRESS = "172.27.0.2"
PORT = 5005
LOCATION = (IP_ADDRESS,PORT)

while 1:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(LOCATION)
    sock.listen(1)
    s, addr = sock.accept()
    while True:
        data = s.recv(1024)
        if not data:
            break
        neat_data(data)
    s.close()
