import socket
import os
from struct import pack
import scapy.all as scapy
from time import time, sleep
from threading import Thread, Lock
from _thread import *
import random

DATA_LOCK = Lock()
POINTS_LOCK = Lock()

SEARCHING_FOR_PLAYERS = True

GAME_TIME = 10
UDP_MSG_TIME = 10
SEARCH_TIME = 10

DEV_ip = "eth1"
TEST_ip = "eth2"

TEST = False

IP = scapy.get_if_addr(TEST_ip if TEST else DEV_ip)

ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_host = '255.255.255.255'
UDP_port = 13117
TCP_host = IP
TCP_port = 2500

TEAMS = 2

DATA_DICT = {}
POINTS_DICT = {}
CONN_DICT = {}
THREADS = []


def send_udp():
    global SEARCHING_FOR_PLAYERS
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # enable broadcasts
    start_time = time()
    msg = pack('IbH', 0xfeedbeef, 0x2, TCP_port)
    ip = UDP_host
    while UDP_MSG_TIME > time() - start_time:
        udp_socket.sendto(msg, (ip, UDP_port))
        sleep(1)
    SEARCHING_FOR_PLAYERS = False


def game(connection, team):     # game function
    start_time = time()
    while GAME_TIME > time() - start_time:
        connection.settimeout(max(GAME_TIME - time(), 0))
        try:
            data = connection.recv(2048)
            with DATA_LOCK:
                DATA_DICT[team] += data
            with POINTS_LOCK:
                POINTS_DICT[team] += 1
        except Exception:
            pass


def interesting_info():     # function for extra info
    all_data = []
    for (team, data) in DATA_DICT.items():
        all_data += data
    letters_dict = {}
    for letter in all_data:
        if not letters_dict[letter]:
            letters_dict[letter] = 0
        letters_dict[letter] += 1
    max_letter = 0
    max_appearance = 0
    for (letter_, appearance_) in letters_dict.items():
        if appearance_ > max_appearance:
            max_letter = letter_
            max_appearance = appearance_
    return "letter with most appearances is \'" + max_letter + "\' with " + str(max_appearance) + " appearances."


def info():     # sending info about the game to the client
    winner = 0
    max_score = 0
    for (team_, score_) in POINTS_DICT:
        if max_score < score_:
            winner = team_
    info_msg = "team " + winner + " is the winner"
    more_info = "\n" + interesting_info()

    final_msg = info_msg + more_info
    print(final_msg)


def main():
    global SEARCHING_FOR_PLAYERS
    global CONN_DICT
    global POINTS_DICT
    global THREADS

    while True:
        try:
            ServerSocket.bind((TCP_host, TCP_port))
        except socket.error as e:
            print("1. " + str(e))
        try:
            udp_socket.bind((UDP_host, UDP_port))
        except socket.error as e:
            print("2. " + str(e))

        for i in range(1, TEAMS):
            CONN_DICT[i] = []
            POINTS_DICT[i] = 0

        print('Server started, listening on IP address ' + TCP_host)
        ServerSocket.listen(5)

        SEARCHING_FOR_PLAYERS = True
        start_new_thread(send_udp, ())
        while SEARCHING_FOR_PLAYERS:
            ServerSocket.settimeout(0.1)
            try:
                connection, address = ServerSocket.accept()
                name = ServerSocket.recv(2048)
            except Exception as e:
                continue
            team = random.randint(1, TEAMS)
            CONN_DICT[team] += [name, connection]
            THREADS += [[name, connection, team]]
        udp_socket.close()

        #   if noone connected
        if not THREADS:
            print("nope")
            continue

        #   start game
        for (conn, team) in THREADS:
            start_new_thread(game, (conn, team))

        sleep(12)
        #   print game info
        info()

        #   close connections
        for (conn, team) in THREADS:
            conn.close()

        ServerSocket.close()


main()
