import socket
import threading

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


def hello_message():
    choice = input("Enter 'Hello' if you want to join the chatroom: ")
    if choice.lower() == "hello":
        return choice
    else:
        return None

def receive_messages(conn):
    while True:
        try:
            # Receive messages from the server
            data = conn.recv(1024).decode()
            if data:
                print("[Server]:", data)
        except Exception as e:
            print("An error occurred while receiving messages:", e)
            break

def send_messages(conn):
    while True:
        try:
            # Prompt for user input and send messages to the server
            message = input("[You]: ")
            conn.sendall(message.encode())
            if message.lower() == 'exit':
                break
        except Exception as e:
            print("An error occurred while sending messages:", e)
            break

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
        print(f"Login successful for: {username}")
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
