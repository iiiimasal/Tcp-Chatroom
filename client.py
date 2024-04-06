import socket
import threading
import os
HOST = "127.0.0.1"
PORT = 8020

def create_user(conn):
    print("Do you have an account? (yes/no)")
    choice = input()

    if choice.lower() == "no":
        print("Please create an account.")
        username = input("Enter a username: ")
        password = input("Enter a password: ")

        # Check if username or password contains white spaces
        if ' ' in username or ' ' in password:
            print("Username and password cannot contain white spaces.")
            return create_user(conn)

        # Encode the message as bytes before sending
        message = f"register:{username}:{password}"
        conn.sendall(message.encode())  # Indicate registration with "register"
        
        # Return the login data
        return message
        
    elif choice.lower() == "yes":
        print("Please login into your account.")
        username = input("Enter a username: ")

        # Encode the message as bytes before sending
        message = f"login:{username}"
        conn.sendall(message.encode())  # Indicate login with "login"
        
        # Return the login data
        return message
        
    else:
        print("Invalid choice. Please enter 'yes' or 'no'.")
        return create_user(conn)

def receive_key(conn):
    key = conn.recv(32)
    return key



def hello_message():
    choice = input("Enter 'Hello' if you want to join the chatroom: ")
    if choice.lower() == "hello":
        return choice
    else:
        return None

def receive_messages(conn):
    save_directory = os.getcwd()
    print(save_directory)
    while True:
        try:
            # Receive messages from the server
            data = conn.recv(1024).decode()
            if data:
                print("[Server]:", data)
                if "has sent a file" in data:
                    file_info = data.split(":")
                    file_name = file_info[1]
                    file_size = int(file_info[2])
                    receive_file(conn, file_name, file_size, save_directory)
        except Exception as e:
            print("An error occurred while receiving messages:", e)
            break

def receive_file(conn, file_name, file_size, save_directory):
    try:
        file_path = os.path.join(save_directory, file_name)
        with open(file_path, "wb") as file:
            received_size = 0
            while received_size < file_size:
                data = conn.recv(1024)
                file.write(data)
                received_size += len(data)
            print(f"File '{file_path}' received successfully.")
    except Exception as e:
        print(f"An error occurred while receiving the file '{file_name}':", e)


def send_messages(conn):
    while True:
        try:
            # Prompt for user input and send messages to the server
            message = input("")
            if message.lower().startswith("private"):  # Corrected condition
                new_form = private_message_format(message)
                print(new_form)

            elif message.lower().startswith("file"):  # Send file if message starts with "file"
                file_path = message.split(",", 1)[1].strip()
                new_form=public_message_format(message)
                send_file(conn, file_path)

            else:
                new_form = public_message_format(message)
            conn.sendall(new_form.encode())
            if message.lower() == 'exit':
                break
        except Exception as e:
            print("An error occurred while sending messages:", e)
            break


def send_file(conn, file_path):
    if os.path.isfile(file_path):
        # Send file name and size
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        conn.sendall(f"file:{file_name}:{file_size}".encode())

        # Send file content
        with open(file_path, "rb") as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                conn.sendall(data)
        print(f"File '{file_name}' sent successfully.")
    else:
        print("File not found.")


def public_message_format(message):
    length=len(message).to_bytes()
    new_format=f"Public message,{length}\r\n{message}\r\n"
    return new_format

def private_message_format(message):
    segments = message.split(",")
    receivers = segments[0].split(" ")[1:]

    body = segments[1]
    # Calculate the length of the body in bytes
    length = len(body).to_bytes()
    # Convert the length to bytes using big-endian encoding
    # length_bytes = length.to_bytes(2, byteorder='big')
    
    new_format = f"Private message,{length} to {', '.join(receivers)}\r\n{body} "
    
    return new_format


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
    c.connect((HOST, PORT))
    print("[Connected to server]")

    # Login or create user account
    login_data = create_user(c)
    print(login_data)
    command, received_data = login_data.split(":", 1)  # Split command and received data
    
    if command == "login":
        # No password is sent for login, so received_data contains only the username
        username = received_data
        key = receive_key(c)
        print(f"Login successful for: {username}")
        print("Received key:", key)

    else:
        # For registration, split received_data into username and password
        username, password = received_data.split(":")
        print(f"Registered successfully. Username: {username}, Password: {password}")

    login_response = c.recv(1024).decode()
    print(login_response)

    if login_response.startswith("Login successful"):
        # If logged in successfully, check for "Hello" message
        first_message = hello_message()
        if first_message:
            c.sendall(first_message.encode())
            welcome_response = c.recv(1024).decode()
            print(welcome_response)
            if welcome_response.startswith("Welcome"):
                print("You can start chatting now.")
                
                # Start two threads for receiving and sending messages
                receive_thread = threading.Thread(target=receive_messages, args=(c,))
                send_thread = threading.Thread(target=send_messages, args=(c,))
                receive_thread.start()
                send_thread.start()
                receive_thread.join()
                send_thread.join()

print("[Connection has been closed]")
