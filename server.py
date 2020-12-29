import socket
import os
from struct import pack
from time import time, sleep
from threading import Thread, Lock
from _thread import *
import random

POINTS_LOCK = Lock()

UDP_host = '255.255.255.255'
UDP_port = 13117
TCP_host = socket.gethostbyname(socket.gethostname())
TCP_port = 2127

TEAMS = 2

TEAM_1 = []
Points_1 = 0

TEAM_2 = []
Points_2 = 0

CLIENTS_DICT = {}
THREADS = []


def udp_sending():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = pack('IbH', 0xfeedbeef, 0x2, TCP_port)
    end_time = time() + 10
    while end_time > time():
        udp_socket.sendto(msg, (UDP_host, UDP_port))
        sleep(1)
    udp_socket.close()
    

def tcp_connect():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((TCP_host, TCP_port))
    serversocket.listen()
    end_time = time() + 10
    while end_time >= time():
        connection, address = serversocket.accept()
        Thread(getName,(connection)).start()
    

def getName(connection):
    global CLIENTS_DICT

    connection.setblocking(False)
    client_name = ''
    while True:
        msg = connection.recv(1024)
        if len(msg) <= 0:
            break
        client_name += msg.decode("utf-8")
    CLIENTS_DICT[client_name] = connection


def Welcome_Message(connection):
    team1 =""
    for name in TEAM_1:
        team1 += name + "\n"
    team2 =""
    for name in TEAM_2:
        team2 += name + "\n"
    msg = f"Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n{team1}Group 2:\n==\n{team2}Start pressing keys on your keyboard as fast as you can!!"
    connection.sendall(msg)


def game(connection, team):     # game function
    #Sending welcome message
    Welcome_Message(connection)
    end_time = time() + 10
    while end_time > time() :
        try:
            data = connection.recv(1024)
            with POINTS_LOCK:
                if team == 1 :
                    Points_1 += 1
                else :
                    Points_2 += 2
        except Exception:
            continue


def info(connection, team):     # sending info about the game to the client
    winner = 1
    max_score = Points_1 if Points_2 < Points_1 else Points_2 
    score = Points_1 if team == 1 else Points_2    
    
    winner_msg ="draw" if Points_1 == Points_2 else "you won!" if winner == team else "team " + str(winner) + "."
    info_msg = "\nyour team: " + str(team) + "\nyour score: " + str(score)
    #more_info = "\n" + interesting_info()

    final_msg = winner_msg + info_msg #+ more_info
    connection.sendall(final_msg)

def main():
    global THREADS

    print('“Server started, listening on IP address ' + TCP_host)
    while True :
        try:
            # Sending UDP broadcast.
            udp_messages = Thread(udp_sending, ())
            udp_messages.start()

            # TCP connecting phase.
            tcp_connect()

            # Waiting till UDP send all the messages.
            udp_messages.join()

            # Building teams up.
            if len(CLIENTS_DICT.keys) > 1 :
                for name in CLIENTS_DICT.keys:
                    team_num = random.randint(1, TEAMS)
                    if team_num == 1 :
                        if len(TEAM_1) < len(CLIENTS_DICT) / 2:
                            TEAM_1.append(name)
                        else :
                            TEAM_2.append(name)
                    if team_num == 2 :
                        if len(TEAM_2) < len(CLIENTS_DICT) / 2:
                            TEAM_2.append(name)
                        else :
                            TEAM_1.append(name)
            else :
                print("There is just one client")

            # start game.
            for name in CLIENTS_DICT:
                team = 1
                conn = CLIENTS_DICT[name]
                if name in TEAM_2:
                    team = 2
                t = Thread(game, (conn, team))
                THREADS.append(t)
                t.start()

            for thread in THREADS:
                thread.join()
            
            #Sending the winning message.
            for name in CLIENTS_DICT:
                team = 1 if name in TEAM_1 else 2
                info(CLIENTS_DICT[name], team)

            # close connections.
            for name in CLIENTS_DICT:
                CLIENTS_DICT[name].close()
            
            # Listening for offers again.
            print("Server disconnected, listening for offer requests...")
        except :
            continue

main()


















# def interesting_info():     # function for extra info
#     all_data = []
#     for (team, data) in TEAMS_DICT.items():
#         all_data += data
#     letters_dict = {}
#     for letter in all_data:
#         if not letters_dict[letter]:
#             letters_dict[letter] = 0
#         letters_dict[letter] += 1
#     max_letter = 0
#     max_appearance = 0
#     for (letter_, appearance_) in letters_dict.items():
#         if appearance_ > max_appearance:
#             max_letter = letter_
#             max_appearance = appearance_
#     return "letter with most appearances is \'" + max_letter + "\' with " + str(max_appearance) + " appearances."