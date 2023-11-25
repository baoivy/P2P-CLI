import socket
from threading import Thread
import time
import sys
#Define parameter 
PORT = 7774

#Using array to store client 
active_client = []
rfc_index = []

def add_client(data_list, client_socket):
    host = data_list[1].split(':')[1]
    port = data_list[2].split(':')[1]
    active_client.append({"host" : host, "port" : port})
    client_socket.send('Sucessfully joined the P2P network'.encode())


def discover(data_list):
    host = data_list[1]
    for rfc,i in zip(rfc_index, range(1, len(rfc_index) + 1)):
        if rfc['host'] == host:
            print(str(i) + ". " + rfc['filename'])

def ping(data_list):
    tmp_port = 0
    for rfc in active_client:
        if rfc['host'] == data_list[1]:
            tmp_port = int(rfc['port'])
            break
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.settimeout(1)
    for i in range(5): 
        sendTime = time.time()
        message = 'PING ' + str(i + 1) + " " + str(time.strftime("%H:%M:%S"))
        try:
            clientSocket.sendto(message.encode('utf-8'), ("localhost", tmp_port))
            data, server = clientSocket.recvfrom(1024)
            recdTime = time.time()
            rtt = recdTime - sendTime
            print ("Message Received :", data)
            print ("Round Trip Time", rtt)
        
        except:
            time.sleep(1)
            print ('REQUEST TIMED OUT')
    return


def find_peer(data_list, client_socket):
    filename = data_list[1].split(':')[1]
    tmp_msg = ""
    for rfc in rfc_index:
        if rfc['filename'] == filename:
            tmp_str = str(rfc['host']) + " " + str(rfc['port']) + '\n'
            tmp_msg += tmp_str
    client_socket.send(tmp_msg.encode())

def add_repo_client(data_list, client_socket):
    host = data_list[1].split(':')[1]
    filename = data_list[3].split(':')[1]
    port = data_list[2].split(':')[1]
    rfc_index.append({"host" : host, "port" : port, "filename" : filename})
    response = "PUBLISH P2P-CI/1.0 200 OK"
    client_socket.send(response.encode())

def client_exit(data_list, client_socket):
    host = data_list[1].split(':')[1]
    port = data_list[2].split(':')[1]
    print('host {0} at port {1} is quitting'.format(host,port))
    for item in rfc_index:
        if host == item['host']:
            rfc_index.remove(item)
    
    for item in active_client:
        if host == item['host']:
            active_client.remove(item)
    client_socket.send(f'Bye {host}'.encode())


def new_client_connect(client_socket):
    data = client_socket.recv(1024).decode()
    data_list  = data.split('\n')
    if data_list[0].split(' ')[0] == 'JOIN':
        add_client(data_list,client_socket)
    elif data_list[0].split(' ')[0] == 'PUBLISH':
        add_repo_client(data_list,client_socket)
    elif data_list[0].split(' ')[0] == 'FIND':
        find_peer(data_list,client_socket)
    elif data_list[0].split(' ')[0] == 'EXIT':
        client_exit(data_list,client_socket)
        return
    
def command_line():
    command = input()
    command_split = command.split(' ')
    if command_split[0] == 'discover':
        discover(command_split)
    elif command_split[0] == 'ping':
        ping(command_split)
    elif command_split[0] == 'exit':
        return

def handle_process(client_socket):
    thread1 = Thread(target=new_client_connect, args=(client_socket,))
    thread1.daemon = True
    thread1.start()

    while True:
        command_line()

def main():
    #Initialize socket
    print('Server starting...')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_host = socket.gethostbyname(socket.gethostname())
    server_socket.bind(('localhost', PORT))

    server_socket.listen(5)
    print('Server waiting...')
    try:
        while True:
            client, addr = server_socket.accept()
            print(f'Connected from : {addr}')
            thread = Thread(target=handle_process, args=(client,))
            thread.start()
    finally:
        #Shutdown
        print('Shut down server...')
        server_socket.close()


if __name__ == '__main__':
    main()