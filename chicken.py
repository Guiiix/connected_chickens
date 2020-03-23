import sys
import os
import time
import queue
import threading
import socket
import signal
import RPi.GPIO as GPIO
from consts import CONF
from classes.Chicken import Chicken

def main():
	action_queue = queue.Queue()
	chicken = Chicken(CONF, action_queue)
	server_address = CONF["SOCKET_PATH"]
	print(server_address)
	try:
		os.unlink(server_address)
	except OSError:
		if os.path.exists(server_address):
			raise
	try:
		th_action_fetcher = threading.Thread(target = chicken.bkg_action_fetcher)
		th_door_state_monitoring = threading.Thread(target = chicken.bkg_door_state_monitoring)
		th_action_fetcher.start()
		th_door_state_monitoring.start()
		sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		sock.bind(server_address)
		os.system("chmod 777 %s" % (server_address))
		sock.listen(1)
		while True:
			connection, client_address = sock.accept()
			action = connection.recv(1024).decode("utf-8")
			print("Received DATA: %s" % (action) )
			if action in ["OPEN", "CLOSE", "STOP"]:
				action_queue.put(action)
	except KeyboardInterrupt:
		print("Program interrupted by user.")
		chicken.tools_stop_running()
		th_action_fetcher.join()
		th_door_state_monitoring.join()
	finally:
		print("Finally")
		GPIO.cleanup()

if __name__ == "__main__":
	main()
