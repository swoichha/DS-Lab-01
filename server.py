# -*- coding:utf-8 -*-

import socket
import threading
import datetime
import re
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
    client_id = client[1] #change this to add unique random numerical digits of len 5
    print('server start to receiving msg from [%s:%s]....' % (client[0], client[1]))
    link.sendall(f'{client_id}'.encode())
    clients[client_id] = link

    while True:
        client_data = link.recv(1024).decode()
        if client_data == "exit":
            print('communication end with [%s:%s]...' % (client[0], client[1]))
            break

        elif client_data == "list":
            """Returns all the active client IDs."""
            sk_clients = list(clients.keys())
            final_list = []
            for sk_client in sk_clients:
                if client_id == sk_client:
                    final_list.append(str(sk_client)+ "(your id)")
                else:
                    final_list.append(str(sk_client))
            link.sendall(f"Active Clients ID: {final_list}".encode())

        elif re.search(r"forward\s\w+:\s*\w+", client_data):
            '''
            Implemented regex to handle the format
            msg format: forward target_ID: message_content
            '''
            input_split = client_data.split(':')
            target_id = int(input_split[0].split()[-1])
            message = input_split[1]
            messages.setdefault(client_id ,{}).setdefault(target_id, []).append([message,datetime.datetime.now()])
            print("//////////", messages)
            if target_id in list(clients.keys()):
                clients[target_id].sendall(f"{client_id}:{message}".encode())
                link.sendall(f'\nMessage forwarded to client {target_id}'.encode())
            else:
                link.sendall('Error: Invalid Targeted ID'.encode())

        elif re.search(r"history\s\d+", client_data):
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
                link.sendall('Error: Invalid Targeted ID'.encode())
        else:
            link.sendall('Please Provide a valid command with a proper format'.encode())
        print('client from [%s:%s] send a msg：%s' % (client[0], client[1], client_data))
    link.close()
    del clients[client_id]


ip_port = ('127.0.0.1', 9999)
sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.SOCK_STREAM is tcp
sk.bind(ip_port)
sk.listen(1)

print('start socket server，waiting client...')

while True:
    conn, address = sk.accept()
    print('create a new thread to receive msg from [%s:%s]' % (address[0], address[1]))
    t = threading.Thread(target=link_handler, args=(conn, address))
    t.start()
