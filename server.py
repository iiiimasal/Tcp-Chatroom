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

logged_in = []

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
                    if username not in logged_in:  # Check if the user is not already logged in
                        logged_in.append(username)
                        print(logged_in)
                        return "Login successful."
                    return "You are already logged in with another client service."
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
                    # print("this is client lis",clients_list)
                    nickname = login_data
                    nicknames[conn] = nickname
                    # print("this is nicknames lis",nicknames)
                    welcome_message = f"Welcome {nickname} to the chatroom!"
                    conn.sendall(welcome_message.encode())
                    joining_leaving(f"{nickname} has joined the chatroom!".encode(), conn)
                    r=handle_chatroom_connection(conn, addr)  # Handle chatroom connection here
                    if r=="Goodbye.You are not allowed in the chatroom anymore":
                        break
                else:
                    print("Client did not send 'Hello'")
        else:
            conn.sendall(b"no connection")

    print("Connection closed by:", addr)
    conn.close()
    remove(conn)



def handle_chatroom_connection(conn, addr): 
    try:
        while True: 
            data = conn.recv(1024)
            if not data:
                break 
            
            segments = data.decode().split(",")
            message_type = segments[0].strip().lower()
            # if message_type.startswith("public"):
            #     handle_public_message(segments[1], conn)
            if message_type.startswith("private"):
                print("yes")
                print(type(data.decode()))
                length, receiver_list, message_body=extract_private_message(data=data)
                print(length," ",receiver_list,message_body)
                handle_private_message(length,message_body,receiver_list,conn)
            else:
                # the data which is sent to server in specific form
                print("Received message:", data.decode())
                received_data = data.decode().strip().lower()
                
                # extercat the message body including "\r\n" 
                raw_data,length = message_format(received_data)
                
                line = raw_data[1]
                
                
                message_to_brodcast = line  # Define message_to_brodcast outside the if-else block
                # removing "\r\n" and exteract the main message body
            
                    
                
                if message_to_brodcast.strip() == "please send the list of attendees":
                    print("yes")
                    request_attendees(conn)

                elif message_to_brodcast.strip()=="bye":
                    conn.sendall(b'Goodbye.You are not allowed in the chatroom anymore')
                   
                    return 'Goodbye.You are not allowed in the chatroom anymore'
                    
                else:
                      
                    sender_nickname = nicknames[conn]
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    broadcast(message_to_brodcast,length, conn)  
                with open('chat_history.txt', 'a') as file:
                    file.write(f"{current_time} - {sender_nickname}: {message_to_brodcast}\n")
    
    except Exception as e:
        print("Error handling client connection:", e)
    # finally:
    #     remove(conn)
    #     print("Connection closed by:", addr)

def handle_private_message(length, message_body, receivers_list, sender_conn):
    try:
        sender_nickname = nicknames[sender_conn]
        
        for client_conn in clients_list:
            nickname = nicknames.get(client_conn)  # Retrieve nickname for the current client_conn
            for reciver in receivers_list:
                try:
                    if reciver==nickname:
                        # Construct message format for each recipient
                        new_format = f"Private message,{length} from {sender_nickname} to {nickname}\r\n{message_body}"
                        client_conn.sendall(new_format.encode())
                except Exception as e:
                    print(f"Error sending message to {nickname}: {e}")
    except Exception as e:
        print("Error handling private message:", e)



def message_format(data):
    raw_data = data.split("\r\n")
    first_line=raw_data[0].split(",")
    length=first_line[1]
    formatted_data=[]
    for word in raw_data:
        formatted_data.append(word)
    return formatted_data,length
    

def request_attendees(conn):
    attendees = ", ".join(nicknames.values())
    response = f"Here is the list of attendees:\\r\\n\r\n{attendees}\\r\\n"
    conn.sendall(response.encode())

def broadcast(message,length ,sender_conn):
    sender_nickname = nicknames[sender_conn]
    for client_conn in clients_list:
        # if client_conn != sender_conn:
            # print("Broadcasting message:", message.decode(), "to", client_conn)
            try:
                data=f"Public message from {sender_nickname},{length}:\r\n {message}\r\n".encode()
                client_conn.send(data)


            except Exception as e:
                print("Error broadcasting message:", e)

def joining_leaving(message, sender_conn):
    sender_nickname = nicknames[sender_conn]
    for client_conn in clients_list:
        if client_conn != sender_conn:
            try:
                # Send the message as a string without the byte prefix
                client_conn.sendall(message)
            except Exception as e:
                print("Error broadcasting message:", e)

def extract_private_message(data):
    data_str = data.decode()
    # Split the data by "\r\n" to separate the message header and body
    # print(data_str)
    header, body = data_str.split("\r\n")
    # print("header:",header)
    
    # Split the header by "to" to extract the recivers
    segments = header.split("to")
    # print(segments)
    # Extract the length of the message
    length = segments[0].split(",")[1].strip()
    # print(length)
    # Extract the receivers
    receiver_list = [receiver.strip() for receiver in segments[1].split(",")]

    # print(receiver_list)
    
    # Extract the message body
    message_body = body.strip()
    
    return length, receiver_list, message_body




def remove(conn): 
    if conn in clients_list: 
        nickname = nicknames[conn]  # Retrieve nickname before removing conn
        clients_list.remove(conn)
        logged_in.remove(nickname)
        joining_leaving(f"{nickname} has left the chat.".encode(), conn)  # Pass conn instead of sender_conn
        del nicknames[conn]
        # conn.close()  # Close the connection




with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print("Server started on port:", PORT)
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_connection, args=(conn, addr))
        thread.start()
