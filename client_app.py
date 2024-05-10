import socket 

HEADER = 64
SERVER_IP = "10.0.2.15"
PORT = 12345
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "DISCONNECT!"
ADDRESS = (SERVER_IP, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
client.connect(ADDRESS)

def send(msg):
	message = msg.encode(FORMAT)
	msg_length = len(message)
	send_length = str(msg_length).encode(FORMAT)
	send_length += b' ' * (HEADER - len(send_length))
	client.send(send_length)
	client.send(message)
	print("Server Reply: ",client.recv(2048).decode(FORMAT))

while True:
	message = input("Send a message to the server: ")
	if message == DISCONNECT_MESSAGE:
		break	
	send(message)
