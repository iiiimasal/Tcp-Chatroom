import socket
import threading
import datetime
HOST = "127.0.0.1"
PORT = 8020
clients_list = []
nicknames = {}

def user_registration(conn, login_data):
    print("Received registration data:", login_data)
    username, password = login_data.split(":")
    with open('login_history.txt', 'a') as file:
        file.write(f"{username}:{password}\n")
    conn.sendall(b"Registered successfully.")

def user_login(conn, login_data):
    print("Received login data:", login_data)
    username = login_data
    print(username)
    with open("login_history.txt", "r") as f:
        for line in f:
            stored_data = line.strip().split(":")
            if len(stored_data) == 2:
                stored_username, stored_password = stored_data
                if stored_username == username:
                    return "Login successful."
    return "Invalid username or password."

def handle_connection(conn, addr):
    print("Connected by:", addr)
    while True:
        data = conn.recv(1024)
        if not data:
            break 
        
        # Decode the received data and split it into command and login data
        try:
            command, login_data = data.decode().split(":", 1)
        except ValueError:
            print("Invalid format of received data:", data.decode())
            conn.sendall(b"Invalid request.")
            continue
        
        if command == "register":
            user_registration(conn, login_data)
        elif command == "login":
            login_response = user_login(conn, login_data)
            conn.sendall(login_response.encode())
            if login_response.startswith("Login successful"):
                # Check if the client sends a "Hello" message
                hello_message = conn.recv(1024).decode().strip().lower()  # Convert to lowercase and strip whitespace
                print("Received message from client:", hello_message)
                if hello_message == "hello":
                    
                    clients_list.append(conn)
                   
                    nickname = login_data
                    # print("nickname",nickname)
                    nicknames[conn] = nickname

                    # print(clients_list)
                    # print("ni",nicknames)
                    welcome_message = f"Welcome {nickname} to the chatroom!"
                    conn.sendall(welcome_message.encode())

                    broadcast(f"{nickname} has joined the chatroom!".encode(), conn)
                    handle_chatroom_connection(conn, addr)
                else:
                    print("Client did not send 'Hello'")
        else:
            conn.sendall(b"Invalid request.")

    print("Connection closed by:", addr)
    remove(conn)
    conn.close()

def handle_chatroom_connection(conn, addr): 
    try:
        while True: 
            data = conn.recv(1024)
            if not data:
                break 
            print("Received message:", data.decode())
            received_data=data.decode().strip().lower()
            if received_data == "please send the list of attendees":
                request_attendees(conn)


            sender_nickname = nicknames[conn]
             # Get the current time
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Write the message along with the time to the chat history file
            with open('chat_history.txt', 'a') as file:
                file.write(f"{current_time} - {sender_nickname}: {data.decode()}\n")
                            # file.write(f"{addr[0]}: {message}\n")
            broadcast(data, conn)
    except Exception as e:
        print("Error handling client connection:", e)
    finally:
        remove(conn)
        print("Connection closed by:", addr)

def request_attendees(conn):
    attendees = ", ".join(nicknames.values())
    response = f"Here is the list of attendees:\r\n{attendees}\r\n"
    conn.sendall(response.encode())

def broadcast(message, sender_conn):
    sender_nickname = nicknames[sender_conn]
    for client_conn in clients_list:
        if client_conn != sender_conn:
            # print("Broadcasting message:", message.decode(), "to", client_conn)
            try:
                data=f"{sender_nickname}: {message.decode()}".encode()
                client_conn.send(data)


            except Exception as e:
                print("Error broadcasting message:", e)







def remove(conn): 
    if conn in clients_list: 
        clients_list.remove(conn)
        nickname = nicknames[conn]
        del nicknames[conn]
        broadcast(f"{nickname} has left the chat.".encode(), conn)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print("Server started on port:", PORT)
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_connection, args=(conn, addr))
        thread.start()
