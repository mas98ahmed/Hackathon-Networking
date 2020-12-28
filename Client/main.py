from socket import *
from struct import *
from getch import *


def ConnectServer():
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.bind(("255.255.255.255", 13117))
    data, address = client_socket.recvfrom(1024)
    msg = unpack(data)
    if len(msg) == 3:
        test_1, test_2, tcp_port = msg
    while len(msg) > 3 or test_1 is not 0xfeedbeef or test_2 is not 0x2:
        data, address = client_socket.recvfrom(1024)
        msg = unpack(data)
        if len(msg) == 3:
            test_1, test_2, tcp_port = msg
    client_socket.send(pack("?", True))
    client_socket.close()
    return tuple(tcp_port)


def TCPConnect(tcp_port, address):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((address, tcp_port))
    tcp_socket.send("Mystic" + "\n")
    return tcp_socket


def GameMode(tcp_socket):
    Terminate = False
    beginning_msg = tcp_socket.recv(2048)
    print(beginning_msg + "\n")
    while Terminate is not True:
        click = getch()
        try:
            tcp_socket.send(click)
        except:
            Terminate = True
    tcp_socket.close()
    

if __name__ == "__main__":
    print("Client started, listening for offer requests...")
    while True:
        tcp_port, address = ConnectServer()
        print("Received offer from {0}, attempting to connect...".format(address))
        TCP_socket = TCPConnect(tcp_port, address)
        GameMode(TCP_socket)
        print("Server disconnected, listening for offer requests...")