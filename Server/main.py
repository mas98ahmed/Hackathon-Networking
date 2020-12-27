import socket
import os
from struct import pack

import scapy
from time import time, sleep
from threading import Thread, Lock
from _thread import *
import random

DATA_LOCK = Lock()
POINTS_LOCK = Lock()

GAME_TIME = 10
UDP_MSG_TIME = 10
SEARCH_TIME = 10

DEBUG = True
ServerSocket = socket.socket()
udp_socket = socket.socket()
UDP_host = '255.255.255.255'
UDP_port = 13117
TCP_host = ""
TCP_port = 2127

TEAMS = 2

DATA_DICT = {}
POINTS_DICT = {}
CONN_DICT = {}
THREADS = []


def send_udp():
    start_time = time()
    msg = pack('IbH', 0xfeedbeef, 2, UDP_port)
    ip = UDP_host if DEBUG else UDP_port
    while UDP_MSG_TIME > time() - start_time:
        udp_socket.sendto(msg, (ip, UDP_port))
        sleep(1)


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


def info(connection, team):     # sending info about the game to the client
    winner = 0
    max_score = 0
    score = 0
    for (team_, score_) in POINTS_DICT:
        if max_score < score_:
            winner = team_
        if team_ == team:
            score = score_
    winner_msg = "you won!" if winner == team else "team " + str(winner) + "."
    info_msg = "\nyour team: " + str(team) + "\nyour score: " + str(score)
    more_info = "\n" + interesting_info()

    final_msg = winner_msg + info_msg + more_info
    connection.sendall(str.encode(final_msg))


def main():
    global CONN_DICT
    global POINTS_DICT
    global THREADS

    try:
        ServerSocket.bind((TCP_host, TCP_port))
        udp_socket.bind((UDP_host, UDP_port))
    except socket.error as e:
        print(str(e))

    for i in range(1, TEAMS):
        CONN_DICT[i] = []
        POINTS_DICT[i] = 0

    print('“Server started, listening on IP address ' + TCP_host)
    ServerSocket.listen(5)

    start_new_thread(send_udp, ())
    start_time = time()
    while SEARCH_TIME > time() - start_time:
        connection, address = ServerSocket.accept()
        name = ServerSocket.recv(2048)
        team = random.randint(1, TEAMS)
        CONN_DICT[team] += [name, connection]
        THREADS += [[name, connection, team]]

    #   start game
    for (conn, team) in THREADS:
        start_new_thread(game, (conn, team))

    sleep(12)
    #   send game info
    for (conn, team) in THREADS:
        start_new_thread(info, (conn, team))

    #   close connections
    for (conn, team) in THREADS:
        conn.close()

    ServerSocket.close()
