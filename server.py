"""
Server receiver of the file
"""
import argparse
import logging
import os
import socket
import sys
import threading
import tqdm

logging.basicConfig(filename='logs/server.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

parser = argparse.ArgumentParser("Client Program")
parser.add_argument("--host", type=str, default="127.0.0.1", help="Server address")
parser.add_argument("--port", type=int, default=8000, help="Server port")

args = parser.parse_args()

# device's IP address
SERVER_HOST = args.host
SERVER_PORT = args.port
# receive 4096 bytes each time
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

def handler(socket):
    # accept connection if there is any
    client_socket, address = socket.accept() 
    # if below code is executed, that means the sender is connected
    logging.info(f"[+] {address} is connected.")

    # receive the file infos
    # receive using client socket, not server socket
    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)
    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(f"server_{filename}", "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:    
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

    # close the client socket
    client_socket.close()


if __name__ == "__main__":

    # Create threads
    thread_connections = []

    # create the server socket
    # TCP socket
    s = socket.socket()
    # bind the socket to our local address
    s.bind((SERVER_HOST, SERVER_PORT))
    # enabling our server to accept connections
    # 5 here is the number of unaccepted connections that
    # the system will allow before refusing new connections
    s.listen(5)
    logging.info(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    # Handle new connections
    thd = threading.Thread(target=handler, args=(s,))
    thread_connections.append(thd)
    thd.start()
    # handler(s)

    # close the server socket
    s.close()