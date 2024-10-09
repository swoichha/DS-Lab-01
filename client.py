# -*- coding:utf-8 -*-
import socket
import threading

is_running = True
ip_port = ('127.0.0.1', 9999)

s = socket.socket()
s.connect(ip_port)

client_id = s.recv(1024).decode()

print(f"Connected to the server! Your assigned Client ID is: {client_id}")

def message_check(s):
    """Thread that listens for incoming messages from the server"""
    global is_running
    while is_running:
        try:
            server_reply = s.recv(1024).decode()
            if server_reply:
                print(f"\n{server_reply}")  # Only display the server's reply once
                print('input msg/command:', end='', flush=True)  # Display the prompt after server response
            else:
                break
        except Exception as e:
            if is_running:
                print(f"\nAn error occurred while receiving a message: {e}")
            break

threading.Thread(target=message_check, args=(s,)).start()

while is_running:
    inp = input('input ///////: ').strip()  # First prompt for input
    if not inp:
        continue

    s.sendall(inp.encode())  # Send message to server

    if inp.lower() == "exit":  # Handle exit case (case insensitive)
        print("Goodbye")
        is_running = False
        break

s.close()
