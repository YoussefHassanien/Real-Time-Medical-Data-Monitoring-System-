import socket
import random
import datetime
import time


HEADER = 64
SERVER_IP = "192.168.56.1"
PORT = 12345
FORMAT = "utf-8"
ADDRESS = (SERVER_IP, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)
first_names = ["Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Henry", "Ivy", "Jack"]
last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
patient_id = None
patient_name = None


def generate_random_patient():
	global patient_id
	global patient_name
	if patient_name is None and patient_id is None:
		patient_name = f"{random.choice(first_names)} {random.choice(last_names)}"
		patient_id = round(random.uniform(1, 100))
	temperature = round(random.uniform(36.1, 37.3), 1)
	date_and_time = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
	return f"{patient_name},{patient_id},{temperature},{date_and_time}"


def send_data(msg):
	message = msg.encode(FORMAT)
	msg_length = len(message)
	send_length = str(msg_length).encode(FORMAT)
	send_length += b' ' * (HEADER - len(send_length))
	client.send(send_length)
	client.send(message)


while True:
	message = generate_random_patient()
	send_data(message)
	time.sleep(0.1)

