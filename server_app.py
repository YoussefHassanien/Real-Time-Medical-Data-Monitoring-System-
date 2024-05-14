import socket
import threading
import redis
import json

HEADER = 64
SERVER_IP = "192.168.56.1"
PORT = 12345
ADDRESS = (SERVER_IP, PORT)
FORMAT = "utf-8"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)
Database = redis.Redis(host="localhost", port=6379, password=None)


def create_database_patient(patient):
	data = json.loads(patient)
	name = data['name']
	patient_id = data['id']
	temperature = data['temperature']
	date, time = data['date'].split(',')
	keys = Database.keys(f"*{patient_id}")
	if len(keys):
		Database.lpush(keys[0], f"{temperature},{date},{time}")
	else:
		Database.lpush(f"{name}_{patient_id}", f"{temperature},{date},{time}")


def handle_client_message(conn, addr):
	connected = True
	while connected:
		msg_length = conn.recv(HEADER).decode(FORMAT)
		if msg_length:
			msg_length = int(msg_length)
			msg = conn.recv(msg_length).decode(FORMAT)
			create_database_patient(msg)


def start_server():
	server.listen()
	while True:
		conn, addr = server.accept()
		thread = threading.Thread(target=handle_client_message, args=(conn, addr))
		thread.start()


start_server()
