import socket
import os
from threading import *
import random
import time
import tqdm

Flag = False
peer_repo = []
SERVER_PORT = 7774
SERVER_HOST = "localhost"

def send_requests(msg : str, server_host, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))
    client_socket.send(msg.encode())
    response = client_socket.recv(1024).decode()
    print(response)
    client_socket.close()

def upload():
    upload_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    upload_host = socket.gethostbyname(socket.gethostname())
    upload_socket.bind((upload_host, port))
    upload_socket.listen(5)
    while Flag != True:
        (client_socket,client_addr) = upload_socket.accept()
        print('Got connection from', client_addr)
        new_thread = Thread(target=peer_connect, args=(client_socket, ))
        new_thread.start()
    
    upload_socket.close()

def peer_connect(client_socket):
    filename = client_socket.recv(1024).decode()
    with open(filename, 'rb') as f1:
        file_size = os.path.getsize(filename)
        #Print
        client_socket.send(("recievied_" + filename).encode())
        client_socket.send(str(file_size).encode())

        data = f1.read()
    client_socket.sendall(data)
    client_socket.send(b"<END>")
    f1.close()
    client_socket.close()

def download(filename):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    upload_host1 = socket.gethostbyname(socket.gethostname())
    msg = "FIND P2P-CI/1.0\nFILENAME:" + filename
    send_requests(msg, "localhost", SERVER_PORT)
    #####
    port1 = int(input("Input peer port from list above: "))
    client.connect((upload_host1, port1))
    client.send(filename.encode())
    file_name = client.recv(1024).decode()
    file_size = client.recv(1024).decode()
    print(file_name + " " + file_size)
    file_byte = b""
    done = False

    progress = tqdm.tqdm(unit='B', unit_scale=True, 
                         unit_divisor=1000, total=int(file_size))
    with open(file_name, 'wb') as f:
        while not done:
            data = client.recv(1024)
            if file_byte[-5:] == b"<END>":
                done = True
            else:
                file_byte += data
            progress.update(1024)

        f.write(file_byte)

    f.close()
    client.close()

def add(host):
    msg = "JOIN P2P-CI/1.0\nHost:"+host+'\n'+"Port:"+str(port)
    send_requests(msg, "localhost", SERVER_PORT)

def publish(host, title, filename):
    peer_repo.append(filename)
    msg = "PUBLISH RFC P2P-CI/1.0\nHost:"+ host + '\n'+"Port:"+str(port)+'\n'+"Title:"+ title + '\n'+ "File:"+ filename 
    send_requests(msg, "localhost", SERVER_PORT)

def exit(host):
    msg =  "EXIT P2P-CI/1.0\nHost:"+ host + '\n'+"Port:"+str(port)
    send_requests(msg, "localhost", SERVER_PORT)
    Flag = True


def recieve_ping():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Assign IP address and port number to socket
    serverSocket.bind(("localhost", port))
    serverSocket.settimeout(1)
    while True:
        try:
            rand = random.randint(0, 10)
            time.sleep(1)
            message, address = serverSocket.recvfrom(1024)
            message = message.upper()
            if rand < 3:
                continue
            serverSocket.sendto(message, address)
        except:
            pass

def command_line():
    hostname = input("Input your hostname: ")
    add(hostname)
    while True:
        command = input()
        command_split = command.split(' ')
        if command_split[0] == 'fetch':
            download(command_split[1])
        elif command_split[0] == 'publish':
            publish(hostname, command_split[1], command_split[2])
        elif command_split[0] == 'exit':
            exit(hostname)
            break
        else:
            print('Command error!')

def main():
    upload_thread = Thread(target=upload)
    #destroy this upload thread on quitting
    upload_thread.daemon = True
    upload_thread.start()

    ping_thread = Thread(target=recieve_ping)
    ping_thread.daemon = True
    ping_thread.start()

    command_line()

if __name__ == '__main__':
    port = 8000 + random.randint(0, 255)
    main()