import socket

HOST = "127.0.0.1"
PORT = 8020

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
    c.connect((HOST, PORT))
    print("[Connected to server]")
    data = c.recv(1024)
    print("server: ", data.decode())
    while True: 

        
        message = input("[Enter your message (type exit for quit)] : ")
        if message == 'exit':
            break 
        c.sendall(message.encode())
        data = c.recv(1024)
        if not data:
            break 
        print("Received: ", data.decode())

print("[Connection has been closed]")
