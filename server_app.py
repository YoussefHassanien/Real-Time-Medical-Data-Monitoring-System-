import socket
import threading
import redis

HEADER = 64
SERVER_IP = "192.168.56.1"
PORT = 12345
ADDRESS = (SERVER_IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "DISCONNECT!"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)
Database = redis.Redis(host="localhost", port=6379, password=None)
patients = False


def create_database_patients(patient):
	name, patient_id, temperature, date, time = patient.split(',')
	Database.lpush(f"{name}_{patient_id}", f"{temperature},{date},{time}")

def update_patients_data(data):
	patient_id, temperature, date, time = data.split(',')
	keys = Database.keys(f"*{patient_id}")
	Database.lpush(keys[0], f"{temperature},{date},{time}")


def handle_client_message(conn, addr):
	global patients
	counter = 0
	connected = True
	while connected:
		msg_length = conn.recv(HEADER).decode(FORMAT)
		if msg_length:
			msg_length = int(msg_length)
			msg = conn.recv(msg_length).decode(FORMAT)
			if not patients:
				create_database_patients(msg)
				counter += 1
				if counter >= 3:
					patients = True
			else:
				update_patients_data(msg)

	conn.close()



def start_server():
	server.listen()
	while True:
		conn, addr = server.accept()
		thread = threading.Thread(target=handle_client_message, args=(conn, addr))
		thread.start()


start_server()
