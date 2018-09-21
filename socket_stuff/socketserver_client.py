import socket
import sys

if __name__ == "__main__":
    LOCATION = ("localhost",9999)
    data = " ".join(sys.argv[1:])
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(LOCATION)
        sock.sendall(bytes(data + "\n", "utf-8"))

        received = str(sock.recv(1024), "utf-8")
    print("Sent: {}".format(data))
    print("Received: {}".format(received))
