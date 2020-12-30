import socket
import os
from struct import pack
import scapy.all as scapy
from time import time, sleep
from threading import Thread, Lock
from _thread import *
import random
import codecs
from string import Formatter


DATA_LOCK = Lock()      # only one thread has access for data at a time
POINTS_LOCK = Lock()    # same for points dict

SEARCHING_FOR_PLAYERS = True

GAME_TIME = 5
CLIENT_SEARCH_TIME = 10

DEV_ip = "eth1"
TEST_ip = "eth2"

TEST = False

IP = scapy.get_if_addr(TEST_ip if TEST else DEV_ip)

ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_dest = '172.1.255.255'
UDP_port = 13117
TCP_port = 2216

TEAMS = 2

NAME_TO_POINTS = {}
DATA_DICT = {}
POINTS_DICT = {}
CONN_DICT = {}
THREADS = []

INTRO_MSG = ""


class bcolors:
    HEADER = '\033[95m'
    CBLACK  = '\33[30m'
    CRED    = '\33[31m'
    CGREEN  = '\33[32m'
    CYELLOW = '\33[33m'
    CBLUE   = '\33[34m'
    CVIOLET = '\33[35m'
    CBEIGE  = '\33[36m'
    CWHITE  = '\33[37m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    COLORS = [CBLUE, CYELLOW, CGREEN]
    CBLINK    = '\33[5m'


def send_udp():
    global SEARCHING_FOR_PLAYERS
    global IP
    global udp_socket
    try:
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)    # enable broadcasts
        msg = pack('IBH', 0xfeedbeef, 0x2, TCP_port)                        # create package
        while SEARCHING_FOR_PLAYERS:
            udp_socket.sendto(msg, (UDP_dest, UDP_port))                    # send to everyone
            sleep(1)
    except Exception as e:  
        print("error sending usp: ", e)
    udp_socket.close()                                                      # no need for the socket


def game(connection, name, team):     # game function
    try:
        # print("sending intro")
        connection.send(INTRO_MSG.encode())                                 # send the intro and teams data
    except Exception as e:
        print(str(e))
        return
    # print("intro sent")
    start_time = time()
    data = []
    while GAME_TIME > time() - start_time:
        connection.settimeout(max(GAME_TIME - time() + start_time, 0))
        try:
            data = connection.recv(4096)                                    # get the data
            data = codecs.decode(data, 'UTF-8')
            if not data:
                continue
        except Exception as e:
            if str(e) != "timed out":
                print(f"{bcolors.WARNING}error with player {name}\t{e}{bcolors.ENDC}")
            pass
        # print(str(data))                                          
        DATA_LOCK.acquire()                                                 # document the data
        NAME_TO_POINTS[name] += 1
        DATA_DICT[team] += data
        # print("team " + str(team) + " data: " + str(DATA_DICT[team]))
        DATA_LOCK.release()
        POINTS_LOCK.acquire()
        POINTS_DICT[team] += 1
        # print("team " + str(team) + " points: " + str(POINTS_DICT[team]))
        # print()
        POINTS_LOCK.release()


def interesting_info():     # function for extra info, like the mvp, most used letter and more
    all_data = []
    for (team, data) in DATA_DICT.items():
        all_data += data
    letters_dict = {}
    for letter in all_data:
        letters_dict[letter] = 0
    for letter in all_data:
        letters_dict[letter] += 1
    max_letter = 0
    max_appearance = 0
    for (letter_, appearance_) in letters_dict.items():
        if appearance_ > max_appearance:
            max_letter = letter_
            max_appearance = appearance_
    ret = "letter with most appearances is \'" + str(max_letter) + "\' with " + str(max_appearance) + " appearances.\n"
    max_player = ""
    max_score = 0
    for (name, score) in NAME_TO_POINTS.items():
        if max_score < score:
            max_player = name
            max_score = score
    max_player = max_player
    ret += f"{bcolors.BOLD}{bcolors.CBLINK}{bcolors.CBLUE}THE MVP IS {max_player} WITH A CRAZY INCREDIBLE SCORE OF {max_score}{bcolors.ENDC}{bcolors.ENDC}{bcolors.ENDC}"
    return ret
        


def send_info(conn, name, final_msg, winning_team):         # send the players game data
    try:                
        conn.settimeout(2)
        msg = ("you won!!\n" if winning_team else "better luck next time!!\n") + final_msg
        conn.sendall(msg.encode())
    except Exception as e:
        print("could not send final msg to " + name + " because " + str(e))


def info():     # returns the final msg for the clients. includes analytics
    winner = 0
    max_score = 0
    for (team_, score_) in POINTS_DICT.items():
        if max_score < score_:
            winner = team_
    info_msg = f"{bcolors.BOLD}team {str(winner)} is the winner {bcolors.ENDC}"
    more_info = "\n" + interesting_info()
    final_msg = info_msg + more_info
    print(final_msg)
    return final_msg, winner


def assemble_intro_msg():                                   # creating the opening msg, with the player names and teams
    global INTRO_MSG
    INTRO_MSG = f"\n{bcolors.CVIOLET}***************************************************{bcolors.ENDC}\n"
    INTRO_MSG += f"{bcolors.HEADER}Welcome to Keyboard Spamming Battle Royale.{bcolors.ENDC}\n"
    for i in range(1, TEAMS+1):
        group_msg = f"\tgroup {i}:\n"
        if len(CONN_DICT[i]) == 0:
            group_msg += "\t\tno players\n"
        for (name, conn) in CONN_DICT[i]:
            group_msg += f"\t\t{name}"
        INTRO_MSG += f"{bcolors.COLORS[i]}{group_msg}{bcolors.ENDC}"
    INTRO_MSG += f"{bcolors.BOLD}Start pressing keys on your keyboard as fast as you can!!\n{bcolors.ENDC}"
    INTRO_MSG += f"{bcolors.CVIOLET}***************************************************{bcolors.ENDC}\n"
    print(INTRO_MSG)


def reset_data():                                           # at the start of an iteration, resetting the data
    global CONN_DICT
    global POINTS_DICT
    global DATA_DICT
    global THREADS
    global NAME_TO_POINTS
    NAME_TO_POINTS = {}
    THREADS = []
    for i in range(1, TEAMS+1):
        CONN_DICT[i] = []
        POINTS_DICT[i] = 0
        DATA_DICT[i] = []


def main():
    global SEARCHING_FOR_PLAYERS
    global CONN_DICT
    global POINTS_DICT
    global DATA_DICT
    global THREADS
    global CLIENT_SEARCH_TIME
    global ServerSocket
    global udp_socket
    global TCP_port
    global NAME_TO_POINTS

    while True:
        ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        # setting up the sockets
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ServerSocket.bind((IP, 0))
            TCP_port = ServerSocket.getsockname()[1]
        except socket.error as e:
            print("1. " + str(e))
            print("trying again")
            sleep(5)
            continue
        try:
            udp_socket.bind((IP, 0))
        except socket.error as e:
            print("2. " + str(e))
            print("trying again")
            sleep(5)
            continue
        
        reset_data()                                                            # resetting the data

        print(f"{bcolors.CYELLOW}Server started, listening on IP address{bcolors.ENDC} {bcolors.CBLUE}{IP}{bcolors.ENDC}")       
        ServerSocket.listen(5)                                                  # enabling listen for connection requests

        SEARCHING_FOR_PLAYERS = True
        start_new_thread(send_udp, ())                                          # while looking for clients, send offer msgs
        start_time = time()
        while CLIENT_SEARCH_TIME > time() - start_time:
            try:
                ServerSocket.settimeout(max(CLIENT_SEARCH_TIME - time() + start_time, 0))
                connection, address = ServerSocket.accept()                     # accept connection request
                connection.settimeout(max(CLIENT_SEARCH_TIME - time() + start_time, 0))
                name = (connection.recv(4096)).decode()                         # get name
                print(f"{bcolors.COLORS[2]}{name} is on the server...{bcolors.ENDC}")
            except Exception as e:
                if str(e) != "timed out":
                    print(f"{bcolors.FAIL}3: {e}{bcolors.ENDC}")
                continue
            team = 1 if len(CONN_DICT[1]) < len(CONN_DICT[2]) else 2            # setting up client data
            NAME_TO_POINTS[name] = 0
            CONN_DICT[team] += [[name, connection]]
            THREADS += [[name, connection, team]]
        SEARCHING_FOR_PLAYERS = False
        #   if noone connected
        if not THREADS:                                                         # if no clients found - restart
            ServerSocket.close()
            print(f"{bcolors.WARNING}no players found{bcolors.ENDC}")
            continue
        
        assemble_intro_msg()
        
        game_threads = []
        #   start game
        for (name, conn, team) in THREADS:                                      # start the game
            t = Thread(target= game, args= (conn, name, team))
            game_threads.append(t)
            t.start()

        for thread in game_threads:                                             # wait for threads to finish
            thread.join()
        
        #   print game info
        final_msg, winning_team = info()
        msg_threads = []
        for (name, conn, team) in THREADS:                                      # send the msgs
            t1 = Thread(target= send_info, args= (conn, name, final_msg, winning_team == team))
            msg_threads.append(t1)
            t1.start()
        
        for thread in msg_threads:                                              # wait for threads to finish
            thread.join()

        #   close connections
        for (name, conn, team) in THREADS:                                      # close connections
            conn.close()

        THREADS = []
        ServerSocket.close()                                                    # close listening socket


main()
