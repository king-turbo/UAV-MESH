import socket
import sys
import json

file = open("sample.json").read()
file = json.loads(file)
IP_ADDRESS = "172.27.0.2"
PORT = 5005
LOCATION = (IP_ADDRESS,PORT)

print("TARGET IP: ", IP_ADDRESS)
print("TARGET PORT: ", PORT)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(LOCATION)
sock.sendall(json.dumps(file).encode("utf-8"))
