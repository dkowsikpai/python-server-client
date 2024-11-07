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
parser.add_argument("--protocol", type=str, default="TCP", choices=["TCP", "UDP"], help="Server Protocol")

args = parser.parse_args()

# device's IP address
SERVER_HOST = args.host
SERVER_PORT = args.port
# receive 4096 bytes each time
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

def tcp_handler(client_socket, address):
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
        f.close()

    # close the client socket
    client_socket.close()


def udp_handler(client_socket):
    received, s_addr = client_socket.recvfrom(BUFFER_SIZE)
    received = received.decode()
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
            bytes_read, s_addr = client_socket.recvfrom(BUFFER_SIZE)
            if not bytes_read:    
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
        f.close()



if __name__ == "__main__":

    # Create threads
    thread_connections = []

    # create the server socket
    if args.protocol == "TCP":
        # TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # bind the socket to our local address
    s.bind((SERVER_HOST, SERVER_PORT))
    # enabling our server to accept connections
    # 5 here is the number of unaccepted connections that
    # the system will allow before refusing new connections
    if args.protocol == "TCP":
        s.listen(5)
    logging.info(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    # Handle new connections
    # accept connection if there is any
    if args.protocol == "TCP":
        while True:
            client_socket, address = s.accept() 
            thd = threading.Thread(target=tcp_handler, args=(client_socket, address))
            thread_connections.append(thd)
            thd.start()
            # handler(s)
        # s.close() # Wait for the next client; Remove While true and uncomment for single client
    else:
        thd = threading.Thread(target=udp_handler, args=(s,))
        thread_connections.append(thd)
        thd.start()
