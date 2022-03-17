import socket
import time
import logging
from typing import Optional, Callable, Union, List, Dict, Any

class ServerUnavaliable(Exception):
	pass

class SimpleSocket(object):
	def __init__(self, hostname: str, port: int = 22611, timeout: int = 20) -> None:
		self.server_addr = (hostname, port)
		self.is_connected = False
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.settimeout(timeout)
		self.retry_connect = 3
		self._connect()

	def __del__(self) -> None:
		self.sock.close()
	
	def _connect(self):
		try:
			if hasattr(self, "sock"):
				connid = 1
				err = self.sock.connect_ex(self.server_addr)
				if err == 0:
					self.retry_connect = 3
					self.is_connected = True
				else:
					self.re_connect()

		except socket.error as msg:
			logging.error(f"[Socket connection error] Cannot connect to { self.server_addr[0] }, error: {msg}\n")
			self.re_connect()

	def re_connect(self):
		time.sleep(5)
		self.retry_connect -= 1
		if self.retry_connect > 0:
			self._connect()
		else:
			raise ServerUnavaliable(f'Cannot connect to <{ self.server_addr[0] }>, host is unavailable')

	def close(self):
		if hasattr(self, "sock"):
			self.sock.close()
			
	# Send a string command to a socket
	def send_command(self, cmd: str):
		"""Send command string to server"""
		if hasattr(self, "sock") and self.is_connected:
			sent = self.sock.send((cmd + '\n').encode('utf-8'))
			if sent == 0:
				raise RuntimeError("Socket connection broken")

	# Send a string command to a socket and return a string response from the socket
	def ask(self, cmd: str) -> str:
		"""Send a command string to server and return the response"""
		if hasattr(self, "sock") and self.is_connected:
			try:
				sent = self.sock.send((cmd + '\n').encode('utf-8'))
				if sent == 0:
					raise RuntimeError("Socket connection broken")
				tmp = self.sock.recv(4096)
				while not tmp:
					tmp = self.sock.recv(4096)
				return tmp.decode('utf_8')
			except socket.error as msg:
				logging.error(f"[Socket connection error] { msg }")
				return ''
		return ''

	# Send a long string data to the socket and return a long string of response from the socket
	def ask_multi(self, cmd:str, num:int) -> str:
		"""Send a number of commands to server and return the responses"""
		if hasattr(self, "sock") and self.is_connected:
			try:
				self.sock.sendall((cmd).encode('utf-8'))
				tmp_resp = self.sock.recv(4096)
				while not tmp_resp:
					tmp_resp = self.sock.recv(4096)
				data = tmp_resp.decode('utf_8')
				while True:
					if data.count('\n') < num:
						data2 = self.sock.recv(4096).decode('utf_8')
						if data2:
							data = data + data2
					else:
						break
				return data
			except socket.error as msg:
				logging.error(f"[Socket connection error] { msg }")
				return ''
		return ''
	
	def set_keepalives(self):
		if hasattr(self, "sock") and self.is_connected:
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 2)
