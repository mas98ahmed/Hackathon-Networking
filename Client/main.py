from socket import *
from struct import *


def ConnectServer():
    global tcp_port, test_1, test_2
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
    return tcp_socket


if __name__ == "__main__":
    print("Client started, listening for offer requests...")
    tcp_port, address = ConnectServer()
    print("Received offer from %s, attempting to connect...".format(address))
    TCP_socket = TCPConnect(tcp_port, address)
