# -*- coding:utf-8 -*-
import socket
import threading

is_running = True
ip_port = ('127.0.0.1', 9999)

s = socket.socket()
s.connect(ip_port)

client_id = s.recv(1024).decode()

print(f"\033[92m\nConnected to the server! Your assigned Client ID is: {client_id}\033[0m")

def message_check(s):
    """Thread that listens for incoming messages from the server"""
    global is_running
    while is_running:
        try:
            server_reply = s.recv(1024).decode()
            if server_reply:
                print(f"\n{server_reply}")  # Display server's reply only once
                print('\033[93minput msg/command:\033[0m', end='', flush=True)
            else:
                break
        except Exception as e:
            if is_running:
                print(f"\033[91m\nAn error occurred while receiving a message: {e}\033[0m")
            break

# Start the message-checking thread
threading.Thread(target=message_check, args=(s,)).start()

while is_running:
    inp = input('\033[93minput msg/command: \033[0m').strip()  # First prompt for input
    if not inp:
        continue

    s.sendall(inp.encode())  # Send message to server

    if inp.lower() == "exit":  # Handle exit case (case insensitive)
        print("Goodbye")
        is_running = False
        break

s.close()
