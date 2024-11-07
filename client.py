"""
Client that sends the file (uploads)
"""
import argparse
import logging
import os
import socket
import sys
import tqdm

logging.basicConfig(filename='logs/client.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024 * 4 #4KB

def send_file(filename, host, port):
    # get the file size
    filesize = os.path.getsize(filename)
    # create the client socket
    s = socket.socket()
    logging.info(f"[+] Connecting to {host}:{port}")
    s.connect((host, port))
    logging.info("[+] Connected.")

    # send the filename and filesize
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    # start sending the file
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            s.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

    # close the socket
    s.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Simple File Sender")
    parser.add_argument("--file", help="File name to send")
    parser.add_argument("--host", help="The host/IP address of the receiver", default="127.0.0.1")
    parser.add_argument("-p", "--port", help="Port to use, default is 5001", type=int, default=5001)
    args = parser.parse_args()
    filename = args.file
    host = args.host
    port = args.port
    send_file(filename, host, port)