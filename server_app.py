# aho ya yousseff
# import redis

# # Redis connection details
# redis_host = 'localhost'
# redis_port = 6379
# redis_password = None

# # Connect to Redis
# r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

# # Example usage
# try:
#     # Set a key-value pair
#     r.set('mykey', 'Hello Redis!')

#     # Get the value of a key
#     value = r.get('mykey')
#     print(value.decode('utf-8'))  # Decode bytes to string

# except redis.RedisError as e:
#     print(f"Error: {e}")



import socket 
import threading

HEADER = 64
SERVER_IP = "10.0.2.15"
PORT = 12345
ADDRESS = (SERVER_IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "DISCONNECT!"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

def handle_clients(conn, addr):
	print("[NEW CONNECTION]", addr, "connected.")
	connected = True
	while connected:
		msg_length = conn.recv(HEADER).decode(FORMAT)
		if msg_length:
			msg_length = int(msg_length)
			msg = conn.recv(msg_length).decode(FORMAT)
			if msg == DISCONNECT_MESSAGE:
				connected = False 		
			print("Client of address [", addr[1], "] sent the following message:", msg)
			message = input("Reply to the client: ")
			conn.send(message.encode(FORMAT))
			
	conn.close()

def start_server():
	server.listen()
	print("[LISTENING] Server is listening on", SERVER_IP)
	while True:
		conn, addr = server.accept()
		thread = threading.Thread(target=handle_clients, args=(conn,addr))
		thread.start()
		print("[ACTIVE CONNECTIONS]", threading.active_count() - 1)
	
	
print("[STARTING] server is starting")
start_server()	

