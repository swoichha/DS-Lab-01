# -*- coding:utf-8 -*-

import socket
import threading
import datetime
import re
import random  # Import the random module

clients = {}
messages = {}


def chat_history(client_id,target_id):
    '''
    Retrieves the chat history between
    the clients and manage it in dictionary.
    '''
    history = []
    if target_id in messages:
        if client_id in messages[target_id]:
            history +=[(target_id,msg,timestamp) for msg, timestamp in messages[target_id][client_id]]

    if client_id in messages:
        if target_id in messages[client_id]:
            history += [(client_id,msg,timestamp) for msg, timestamp in messages[client_id][target_id]]
    history.sort(key=lambda x:x[2])
    return history

def link_handler(link, client):
    #client_id = client[1] #change this to add unique random numerical digits of len 5
    client_id = str(random.randint(100000, 999999))  
    print('\033[92m\nserver start to receiving msg from [%s:%s]....\033[0m' % (client[0], client[1]))
    link.sendall(f'{client_id}'.encode())
    clients[client_id] = link

    available_commands = "Use any from these available commands: list; history <client_id>; forward <client_id>: <message>; exit;"

    while True:
        client_data = link.recv(1024).decode()
        if re.search(r"(?i)exit", client_data):
            print('\033[92m\ncommunication end with\033[0m [%s:%s]...' % (client[0], client[1]))
            break

        elif re.search(r"(?i)list", client_data):
            """Returns all the active client IDs."""
            sk_clients = list(clients.keys())
            final_list = []
            for sk_client in sk_clients:
                if client_id == sk_client:
                    final_list.append(str(sk_client)+ "(your id)")
                else:
                    final_list.append(str(sk_client))
            link.sendall(f"\033[92m\nActive Clients ID:\033[0m {final_list}".encode())

        elif re.search(r"(?i)forward\s\d+:\s*.+$", client_data):
            '''
            Implemented regex to handle the format
            msg format: forward target_ID: message_content
            '''
            input_split = client_data.split(':')
            target_id = int(input_split[0].split()[-1])
            message = input_split[1]
            messages.setdefault(client_id ,{}).setdefault(target_id, []).append([message,datetime.datetime.now()])

            if target_id == client_id:
            # Error for sending message to yourself
                link.sendall('\033[91m\nError: Cannot send message to yourself\033[0m'.encode())
            elif target_id in clients:
            # Forward the message if the target is valid and not the same as the sender
                clients[target_id].sendall(f"{client_id}: {message}".encode())
                link.sendall(f'\033[92m\nMessage forwarded to client {target_id}\033[0m'.encode())
            else:
                # Error for invalid target ID
                link.sendall('\033[91m\nError: Invalid Targeted ID\033[0m'.encode())

        elif re.search(r"(?i)history\s\d+", client_data):
            '''
            Returns chatting history between the requested client
            and the client with the ID listed
            #Format
            history target_client_ID
            '''
            target_id = int(client_data.split()[1])
            if target_id in list(clients.keys()):
                chat_hist = chat_history(client_id,target_id)
                if chat_hist:
                    msg = []
                    for chat in chat_hist:
                        if client_id == chat[0]:
                            status="(me)"
                        else:
                            status=""
                        msg.append(f"{str(chat[0])+status} : {chat[1]}")
                    link.sendall('\n'.join(msg).encode())
                else:
                    link.sendall(f'No history found with client ID {target_id}'.encode())
            else:
                link.sendall('\033[91m\nError: Invalid Targeted ID\033[0m'.encode())
        else:
            # link.sendall('Please Provide a valid command with a proper format'.encode())
            link.sendall(f'\033[91m\nError: Command not found.\n{available_commands}\033[0m\n'.encode())

        print('\033[94mclient from [%s:%s] send a msg：%s\033[0m' % (client[0], client[1], client_data))
    link.close()
    del clients[client_id]


ip_port = ('127.0.0.1', 9999)
sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.SOCK_STREAM is tcp
sk.bind(ip_port)
sk.listen(1)

print('start socket server，waiting client...')

while True:
    conn, address = sk.accept()
    print('\033[92m\ncreate a new thread to receive msg from [%s:%s]\033[0m' % (address[0], address[1]))
    t = threading.Thread(target=link_handler, args=(conn, address))
    t.start()
