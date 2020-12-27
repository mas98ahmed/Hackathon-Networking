from socket import *
from struct import *


def ConnectServer():
    client_socket = socket(AF_INET,SOCK_DGRAM)
    data, address = client_socket.recvfrom(1024)
    msg = unpack(data)
    if len(msg) == 3:
        test_1 = msg[0]
        test_2 = msg[1]
        tcp_port = msg[3]
    while len(msg) > 3 or test_1 is not 0xfeedbeef or test_2 is not 0x2:
        data, address = client_socket.recvfrom(1024)
        msg = unpack(data)
        if len(msg) == 3:
            test_1 = msg[0]
            test_2 = msg[1]
            tcp_port = msg[2]
    return tuple(tcp_port, address)
    

if __name__ == "__main__":
    print("Client started, listening for offer requests...")
    tcp_port, address = ConnectServer()
    print("Received offer from %s, attempting to connect...".format(address))