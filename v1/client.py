import socket
import threading
import sys
import argparse
from tqdm import tqdm
import os

parser = argparse.ArgumentParser("Client Program")
parser.add_argument("--host", type=str, default="127.0.0.1", help="Server address")
parser.add_argument("--port", type=int, default=8000, help="Server port")
parser.add_argument("--file", type=str, required=True, help="File")

args = parser.parse_args()

#Wait for incoming data from server
#.decode is used to turn the message in bytes to a string
def receive(socket, signal):
    while signal:
        try:
            data = socket.recv(32)
            print(str(data.decode("utf-8")))
        except:
            print("You have been disconnected from the server")
            signal = False
            break

#Get host and port
host = args.host
port = args.port
SIZE = 1024
FORMAT = "utf-8"
FILENAME = args.file
FILESIZE = os.path.getsize(FILENAME)

#Attempt connection to server
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
except:
    print("Could not make a connection to the server")
    input("Press enter to quit")
    sys.exit(0)

#Create new thread to wait for data
receiveThread = threading.Thread(target = receive, args = (sock, True))
receiveThread.start()

#Send data to server
#str.encode is used to turn the string message into bytes so it can be sent across the network
# while True:
""" Sending the filename and filesize to the server. """
server_file_name = FILENAME.split("/")[-1]
data = f"{server_file_name}_{FILESIZE}"
sock.send(data.encode(FORMAT))
msg = sock.recv(SIZE).decode(FORMAT)
print(f"SERVER: {msg}")

""" Data transfer. """
bar = tqdm(range(FILESIZE), f"Sending {FILENAME}", unit="B", unit_scale=True, unit_divisor=SIZE)

with open(FILENAME, "rb") as f:
    while True:
        data = f.read(SIZE)

        if not data:
            break

        sock.sendall(data)
        # msg = sock.recv(SIZE).decode(FORMAT)

        bar.update(len(data))

sock.close()
