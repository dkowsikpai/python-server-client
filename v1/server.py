import socket
import threading
import argparse
from tqdm import tqdm
import os

parser = argparse.ArgumentParser("Client Program")
parser.add_argument("--host", type=str, default="127.0.0.1", help="Server address")
parser.add_argument("--port", type=int, default=8000, help="Server port")

args = parser.parse_args()

#Variables for holding information about connections
connections = []
total_connections = 0
SIZE = 1024
FORMAT = "utf-8"

#Client class, new instance created for each connected client
#Each instance has the socket and address that is associated with items
#Along with an assigned ID and a name chosen by the client
class Client(threading.Thread):
    def __init__(self, socket, address, id, name, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.name = name
        self.signal = signal
    
    def __str__(self):
        return str(self.id) + " " + str(self.address)
    
    #Attempt to get data from client
    #If unable to, assume client has disconnected and remove him from server data
    #If able to and we get data back, print it in the server and send it back to every
    #client aside from the client that has sent it
    #.decode is used to convert the byte data into a printable string
    def run(self):
        data = self.socket.recv(SIZE).decode(FORMAT)
        item = data.split("_")
        FILENAME = item[0]
        FILESIZE = int(item[1])

        if os.path.isfile(f"recv_{FILENAME}"):
            os.remove(f"recv_{FILENAME}")
    
        print("[+] Filename and filesize received from the client.")
        self.socket.send("Filename and filesize received".encode(FORMAT))
    
        """ Data transfer """
        bar = tqdm(range(FILESIZE), f"Receiving {FILENAME}", unit="B", unit_scale=True, unit_divisor=SIZE)
    
        with open(f"recv_{FILENAME}", "wb") as f:
            while True:
                data = self.socket.recv(SIZE)
    
                if not data:
                    break
    
                f.write(data)
                # self.socket.send("Data received.".encode(FORMAT))
    
                bar.update(len(data))

        self.socket.close()


        # while self.signal:
        #     try:
        #         data = self.socket.recv(32)
        #     except:
        #         print("Client " + str(self.address) + " has disconnected")
        #         self.signal = False
        #         connections.remove(self)
        #         break

            


        #     # if data != "" and len(str(data.decode("utf-8"))) > 0:
        #     #     print("ID " + str(self.id) + ": " + str(data.decode("utf-8")))
        #     #     # for client in connections:
        #     #     #     if client.id != self.id:
        #     #     #         client.socket.sendall(data)
        #     else:
        #         print("Client " + str(self.address) + " has disconnected")
        #         self.signal = False
        #         connections.remove(self)
        #         break

#Wait for new connections
def newConnections(socket):
    # while True:
    sock, address = socket.accept()
    global total_connections
    connections.append(Client(sock, address, total_connections, "Name", True))
    connections[len(connections) - 1].start()
    print("New connection at ID " + str(connections[len(connections) - 1]))
    total_connections += 1 # TODO: Make it thread safe

def main():
    #Get host and port
    host = args.host
    port = args.port

    #Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)

    #Create new thread to wait for connections
    newConnectionsThread = threading.Thread(target = newConnections, args = (sock,))
    newConnectionsThread.start()
    
main()
