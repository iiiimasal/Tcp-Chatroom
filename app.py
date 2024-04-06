from flask import Flask, render_template, request, jsonify
import socket
import threading

app = Flask(__name__)

HOST = "127.0.0.1"
PORT = 8020

@app.route('/')
def index():
    return render_template('index.html')

def receive_messages(conn):
    while True:
        try:
            # Receive messages from the server
            data = conn.recv(1024).decode()
            if data:
                return data
        except Exception as e:
            print("An error occurred while receiving messages:", e)
            break

def send_messages(conn, message):
    try:
        # Send messages to the server
        conn.sendall(message.encode())
    except Exception as e:
        print("An error occurred while sending messages:", e)

def handle_client_connection(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        c.connect((HOST, PORT))
        send_messages(c, message)
        return receive_messages(c)

@app.route('/send-message', methods=['POST'])
def send_message():
    message = request.json.get('message')
    response = handle_client_connection(message)
    return jsonify({"message": response})

if __name__ == '__main__':
    app.run(debug=True)
