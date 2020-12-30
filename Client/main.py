import socket
from struct import *
from threading import *
from time import time, sleep
import getch
from _thread import *
import scapy.all as scapy

#colors for the printing
class bcolors:
    CEND      = '\33[0m'
    CBOLD     = '\33[1m'
    CITALIC   = '\33[3m'
    CURL      = '\33[4m'
    CBLINK    = '\33[5m'
    CBLINK2   = '\33[6m'
    CSELECTED = '\33[7m'
    CBLINK    = '\33[5m'

    CBLACK  = '\33[30m'
    CRED    = '\33[31m'
    CGREEN  = '\33[32m'
    CYELLOW = '\33[33m'
    CBLUE   = '\33[34m'
    CVIOLET = '\33[35m'
    CBEIGE  = '\33[36m'
    CWHITE  = '\33[37m'

    CBLACKBG  = '\33[40m'
    CREDBG    = '\33[41m'
    CGREENBG  = '\33[42m'
    CYELLOWBG = '\33[43m'
    CBLUEBG   = '\33[44m'
    CVIOLETBG = '\33[45m'
    CBEIGEBG  = '\33[46m'
    CWHITEBG  = '\33[47m'

    CGREY    = '\33[90m'
    CRED2    = '\33[91m'
    CGREEN2  = '\33[92m'
    CYELLOW2 = '\33[93m'
    CBLUE2   = '\33[94m'
    CVIOLET2 = '\33[95m'
    CBEIGE2  = '\33[96m'
    CWHITE2  = '\33[97m'

    CGREYBG    = '\33[100m'
    CREDBG2    = '\33[101m'
    CGREENBG2  = '\33[102m'
    CYELLOWBG2 = '\33[103m'
    CBLUEBG2   = '\33[104m'
    CVIOLETBG2 = '\33[105m'
    CBEIGEBG2  = '\33[106m'
    CWHITEBG2  = '\33[107m'

#TCP/IP socket
TCP_HOST = ""
TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

TEAM_NAME = 'Totahim_Retsah'

#UDP getting message and returning the TCP port of the server.
def ConnectServer():
    global TCP_HOST
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as UDP_socket:
        UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#Enable the socket to be broadcaster.
        UDP_socket.bind(("", 13117))
        data, address = UDP_socket.recvfrom(4096)#receiving message.
        magic_cookie, message_type, tcp_port = unpack('IBH',data)
        #Checking the UDP message if its data are ok.
        while magic_cookie != 0xfeedbeef or message_type != 0x2:
            data, address = UDP_socket.recvfrom(4096)
            magic_cookie, message_type, tcp_port = unpack(data)
        TCP_HOST = address[0]#The IP of the server that we got it's request.
    return int(tcp_port)#returning the TCP port that we're going to connect to.


#Connecting on TCP socket with the server and sending the name of the client.
def TCPConnect(tcp_port):
    global TCP_socket
    
    TCP_socket.connect((TCP_HOST, tcp_port))
    TCP_socket.send((TEAM_NAME+"\n").encode())


#Getting messages from the server.
def getMessage():
    global TCP_socket
    
    msg = TCP_socket.recv(4096)
    full_msg = msg.decode("utf-8")
    return full_msg

#Starting the game mode
def GameMode():
    global TCP_socket

    beginning_msg = getMessage()#Welcome message.
    print(beginning_msg)
    end_time = time() + 10#finish after 10 seconds.
    while end_time > time():
        click = getch.getch()#Clicking on the keyboard
        try:
            TCP_socket.settimeout(max(end_time-time(), 0))#Setting timeout fo getting message.
            TCP_socket.send(click.encode())
        except:
            break
    winner_msg = getMessage()#The winner message and some more info.
    print(winner_msg)
    TCP_socket.close()


def main():
    global TEAM_NAME
    global TCP_socket
    
    print(f"{bcolors.CWHITEBG}{bcolors.CBLUE}{bcolors.CBOLD}Client started, listening for offer requests...{bcolors.CEND}")
    while True:#Working infinitely.
        TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tcp_port = ConnectServer()#Getting the Tcp port of the server.
            print(f"{bcolors.CGREENBG}{bcolors.CBOLD}Received offer from {TCP_HOST}, attempting to connect...{bcolors.CEND}")
            TCPConnect(tcp_port)#connecting on TCP socket to the server.
            GameMode()#Starting the game.
            print(f"{bcolors.CREDBG}{bcolors.CBOLD}Server disconnected, listening for offer requests...{bcolors.CEND}")
        except:
            continue


main()#Start the main.
