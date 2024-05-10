import socket
import random
import datetime


HEADER = 64
SERVER_IP = "192.168.56.1"
PORT = 12345
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "DISCONNECT!"
ADDRESS = (SERVER_IP, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)
first_names = ["Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Henry", "Ivy", "Jack"]
last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]


def generate_random_patients(patient_id):
	name = f"{random.choice(first_names)} {random.choice(last_names)}"
	temperature = round(random.uniform(36.1, 37.2), 1)
	date_and_time = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
	return f"{name},{patient_id},{temperature},{date_and_time}"


def generate_patients_data():
	temperature = round(random.uniform(36.5, 37.4), 1)
	date_and_time = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
	return f"{ round(random.uniform(1, 3))},{temperature},{date_and_time}"


def send_data(msg):
	message = msg.encode(FORMAT)
	msg_length = len(message)
	send_length = str(msg_length).encode(FORMAT)
	send_length += b' ' * (HEADER - len(send_length))
	client.send(send_length)
	client.send(message)
	print(message)


for i in range(1, 4):
	message = generate_random_patients(i)
	send_data(message)

while True:
	message = generate_patients_data()
	send_data(message)
