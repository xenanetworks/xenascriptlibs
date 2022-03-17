import os
import sys
import time
import threading
import inspect
import logging

from typing import Optional, Callable, Union, List, Dict, Any

from .SocketDrivers import SimpleSocket

LOGFILE = "XENALOG"


def errexit(msg):
	logging.error(f"Error: { msg }, exiting...")
	sys.exit(1)

# Keepalive thread to ensure TCP connection is kept open
# Do not edit this 
class KeepAliveThread(threading.Thread):
	message = ''
	def __init__(self, connection, interval = 10):
		threading.Thread.__init__(self)
		self.connection = connection
		self.interval = interval
		self.finished = threading.Event()
		self.setDaemon(True)
		logging.info('[KeepAliveThread] Thread initiated, interval %d seconds' % (self.interval))

	def stop (self):
		self.finished.set()
		self.join()

	def run (self):
		while not self.finished.isSet():
			self.finished.wait(self.interval)
			self.connection.Ask(self.message)


# Low level driver for TCP/IP based query
# Do not edit this
class XenaSocketDriver(SimpleSocket):
	def __init__(self, hostname: str, port: int = 22611):
		super(XenaSocketDriver, self).__init__(hostname=hostname, port=port)
		self.set_keepalives()
		self.access_semaphore = threading.Semaphore(1)

	def send_command(self, cmd: str):
		self.access_semaphore.acquire()
		super().send_command(cmd)
		self.access_semaphore.release()

	def ask(self, cmd: str) -> str:
		self.access_semaphore.acquire()
		reply = super().ask(cmd).strip('\n')
		self.access_semaphore.release()
		return reply

	def ask_multi(self, cmd: str, num: int):
		self.access_semaphore.acquire()
		reply = super().ask_multi(cmd, num)
		self.access_semaphore.release()
		return reply


# Xena supplied class example for Scripting via Python3
# Feel free to add functions below
class XenaScriptTools:

	CHASSIS_RESERVATION      = lambda self: f"C_RESERVATION ?"
	CHASSIS_RELEASE          = lambda self: f"C_RESERVATION RELEASE"
	CHASSIS_RELINQUISH       = lambda self: f"C_RESERVATION RELINQUISH"
	CHASSIS_RESERVE          = lambda self: f"C_RESERVATION RESERVE"

	MODULE_RESERVATION      = lambda self, mod: f"{ mod } M_RESERVATION ?"
	MODULE_RELEASE          = lambda self, mod: f"{ mod } M_RESERVATION RELEASE"
	MODULE_RELINQUISH       = lambda self, mod: f"{ mod } M_RESERVATION RELINQUISH"
	MODULE_RESERVE          = lambda self, mod: f"{ mod } M_RESERVATION RESERVE"

	PORT_RESET              = lambda self, port: f"{ port } P_RESET"
	PORT_RESERVATION        = lambda self, port: f"{ port } P_RESERVATION ?"
	PORT_RESERVE            = lambda self, port: f"{ port } P_RESERVATION RESERVE"
	PORT_RELINQUISH         = lambda self, port: f"{ port } P_RESERVATION RELINQUISH"
	PORT_RELEASE            = lambda self, port: f"{ port } P_RESERVATION RELEASE"
	PORT_SPEEDSELECTION     = lambda self, port, speed: f"{ port } P_SPEEDSELECTION {speed}"

	PORT_TRAFFIC_ON            	= lambda self, port: f"{ port } P_TRAFFIC ON"
	PORT_TRAFFIC_OFF            = lambda self, port: f"{ port } P_TRAFFIC OFF"

	def __init__(self, ip):
		self.ip    = ip
		self.debug = 0
		self.halt  = 0 
		self.log   = 0
		self.cmds  = []
		self.logf  = os.environ.get(LOGFILE)
		if self.logf != None:
			self.log = 1

		self.driver= XenaSocketDriver(ip)

	def __del__(self):
		if self.log:
			with open(self.logf, 'w') as log_file:
				for cmd in self.cmds:
					log_file.write(f"{ cmd }\n")
		return

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc, tb):
		self.driver.close()

	## Enable debug - prints commands and errors
	def debug_on(self) -> None:
		self.debug = 1
		logging.basicConfig(format='%(asctime)s.%(msecs)03d %(message)s', datefmt='%m/%d/%Y %I:%M:%S')
		return

	## Disable debug (default) - no printed output
	def debug_off(self) -> None:
		self.debug = 0
		return

	def debug_message(self, msg: str) -> None:
		if self.debug == 1:
			logging.info(f"{time.time()} {msg}")
			print(f"{time.time()} {msg}")

	def log_command(self, cmd:str) -> None:
		if self.log == 1:
			self.cmds.append(cmd)
	
	## Enable halt on error - calls sys.exit(1) upon error
	def halt_on(self) -> None:
		self.halt = 1
		return

	## Disable halt on error (default)
	def halt_off(self) -> None:
		self.halt = 0
		return

	## Print diagnostics msg and halt
	def errexit(self, msg:str):
		if self.halt == 1:
			logging.error(f"\nError: { msg }, exiting...\n")
			sys.exit(1)
		else:
			raise Exception(f"\nError: { msg }, exiting...\n")

#####################################################################
#																	#
#						Send and Expect wrappers					#
#																	#
#####################################################################

	## Send command and return response
	def send(self, cmd:str) -> str:
		res = self.driver.ask(cmd)
		self.debug_message(f"send()         : { cmd }")
		self.debug_message(f"send() received: { res }")
		self.log_command(cmd)
		return res
	
	## Send one command and expect to receive a specified response
	def send_expect(self, cmd:str, resp:str) -> bool:
		"""Send command and expect response (typically <OK>)"""

		self.debug_message(f"send_expect({ resp }): { cmd }")
		self.log_command(cmd)
		try:
			res = self.driver.ask(cmd)
			if res.rstrip('\n') == resp:
				return True
			else:
				self.debug_message("send_expect() failed")
				self.debug_message(f"   Expected: { resp }")
				self.debug_message(f"   Received: { res }")
				# self.errexit(f"Halting in line {inspect.currentframe().f_back.f_lineno}")
				return False
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logging.error(exc_type, fname, exc_tb.tb_lineno)
			return False

	## Send one command and expect to receive <OK> as a response
	def send_expect_ok(self, cmd:str) -> bool:
		""" Send commands and expect <OK> """

		if isinstance(cmd, str):
			return self.send_expect(cmd, "<OK>")
		else:
			return False

	## Send command and match response with specified string
	def send_and_match(self, cmd:str, m_str:str) -> bool:
		self.debug_message(f"send_and_match() : { cmd }")
		self.log_command(cmd)

		res = self.driver.ask(cmd)
		if m_str in res:
			return True
		else:
			self.debug_message("send_and_match() failed")
			self.debug_message(f"   Expected: { m_str }")
			self.debug_message(f"   Got     : { res }")
			self.errexit(f"Halting in line { inspect.currentframe().f_back.f_lineno }")
			return False

	## Send multiple commands in batch and return all responses
	def send_multi_commands(self, cmdlist: list, batch = True) -> list:
		if not isinstance(cmdlist, list):
			raise ValueError('\'cmdlist\' - must be a instance of list')
		cmd = ''
		num = len(cmdlist)
		self.debug_message(f"{num} commands to send to xenaserver")

		if batch == True:
			for command in cmdlist:
				cmd = cmd + command + '\n'

			self.debug_message(f"send()         : { cmd }")
			res = self.driver.ask_multi(cmd, num)
			def mapper(v): return f"{ v[0] }: { v[1] }"
			mes = "\n".join( list( map(mapper, list( zip(cmdlist, res.split('\n')) ) ) ) )
			self.debug_message(f"send() received: { mes }")

			return res
		else:
			results = []
			for command in cmdlist:
				cmd = command
				self.debug_message(f"send()         : { cmd }")

				res = self.driver.ask(cmd)

				self.debug_message(f"send() received: { res }")
				self.log_command(cmd)
				results.append(res)
			return results



#####################################################################
#																	#
#				Xena Scripting API specific commands				#
#																	#
#####################################################################

	#############################################################
	# 						Chassis Commands 					#
	#############################################################

	# Logon
	def log_on(self, pwd: str) -> bool:
		return self.send_expect_ok(f"C_LOGON \"{ pwd }\"")

	# Logoff
	def log_off(self) -> None:
		self.send("C_LOGOFF")


	## Logon and set owner
	def logon_set_owner(self, pwd: str, owner: str) -> bool:
		if self.log_on(pwd):
			return self.send_expect_ok(f"C_OWNER \"{ owner }\"")
		return False

	## Logon to chassis, set user name and password, then reserve ports
	def logon_and_reserve(self, ports: Union[List[str], str], pwd: str, owner: str) -> None:
		if isinstance(ports, str): ports = [ports]
		assert self.logon_set_owner(pwd, owner)
		self.port_reserve(ports)

	# Reserve chassis if it is not mine, else do nothing.
	def chassis_reserve(self):
		res = self.send( self.CHASSIS_RESERVATION() ).split()[1]

		if "RESERVED_BY_OTHER" in res:
			self.debug_message("Chassis is reserved by other - relinquish")
			self.send_expect_ok( self.CHASSIS_RELINQUISH() )
			self.send_expect_ok( self.CHASSIS_RESERVE() )

		elif "RELEASED" in res:
			self.send_expect_ok( self.CHASSIS_RESERVE() )

	# Reserve chassis, release or relinquish first if necessary
	def chassis_release(self):
		res = self.send( self.CHASSIS_RESERVATION() ).split()[1]

		if "RESERVED_BY_YOU" in res:
			self.debug_message("Chassis is reserved by me - release")
			self.send_expect_ok( self.CHASSIS_RELEASE() )

		elif "RESERVED_BY_OTHER" in res:
			self.debug_message("Chassis is reserved by other - relinquish")
			self.send_expect_ok( self.CHASSIS_RELINQUISH() )

		elif "RELEASED" in res:
			self.debug_message("Chassis is released - do nothing")
		else:
			self.errexit(f"Halting in line { inspect.currentframe().f_back.f_lineno }")

	# Start traffic on ports simultaneously
	def chassis_traffic_on(self, ports: Union[List[str], str]):
		if isinstance(ports, str): ports = ports.split()
		param = []
		for port in ports:
			param += port.split("/")

		param = ' '.join([str(elem) for elem in param])
		self.send_expect_ok( f"C_TRAFFIC ON {param}")

	# Start traffic on ports simultaneously
	def chassis_traffic_off(self, ports: Union[List[str], str]):
		if isinstance(ports, str): ports = ports.split()
		param = []
		for port in ports:
			param += port.split("/")

		param = ' '.join([str(elem) for elem in param])
		self.send_expect_ok( f"C_TRAFFIC OFF {param}")


	#############################################################
	# 						Module Commands 					#
	#############################################################

	# Release module from me or relinquish module from others
	def module_release(self, module):
		res = self.send(self.MODULE_RESERVATION(module)).split()[2]

		if "RESERVED_BY_YOU" in res:
			self.debug_message("Module is reserved by me - release")
			self.send_expect_ok(self.MODULE_RELEASE(module))

		elif "RESERVED_BY_OTHER" in res:
			self.debug_message("Module is reserved by other - relinquish")
			self.send_expect_ok(self.MODULE_RELINQUISH(module))

		elif "RELEASED" in res:
			self.debug_message("Module is released - do nothing")

		else:
			self.errexit(f"Halting in line { inspect.currentframe().f_back.f_lineno }")


	def module_reserve(self, module):
		"""
		Reserve the module if it is not mine, else do nothing
		"""
		res = self.send(self.MODULE_RESERVATION(module)).split()[2]

		if "RESERVED_BY_OTHER" in res:
			self.debug_message("Module is reserved by other - relinquish")
			self.send_expect_ok(self.MODULE_RELINQUISH(module))
			self.send_expect_ok( self.MODULE_RESERVE(module) )

		elif "RELEASED" in res:
			self.send_expect_ok( self.MODULE_RESERVE(module) )


	#############################################################
	# 						Port Commands 						#
	#############################################################

	# Wait for port to be 'released' - with timeout of 1 minute
	def port_wait_release(self, ports: Union[List[str], str], timeout_s: int = 63):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			timeout = time.time() + timeout_s # 60sec + total 3sec of slipping time by 1s
			while True:
				res = self.send( self.PORT_RESERVATION(port) )
				if 'RELEASED' in res:
					break
				elif time.time() > timeout:
					raise TimeoutError('port_wait_release: Waiting for changing of port reservation interval is terminated!')
				else:
					time.sleep(0.1)

	# Reserve a port - if port is reserved, release or relinquish, then reserve
	def port_reserve(self, ports: Union[List[str], str]) -> None:
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			res = self.send( self.PORT_RESERVATION(port) )
			if 'RESERVED_BY_OTHER' in res:
				self.debug_message(f"Port { port } is reserved by other - relinquish")
				self.send_expect_ok( self.PORT_RELINQUISH(port) )
				self.port_wait_release(port)
				self.send_expect_ok( self.PORT_RESERVE(port) )
			elif 'RELEASED' in res:
				self.send_expect_ok( self.PORT_RESERVE(port) )

	# Set a port/ports free.
	def port_set_free(self, ports: Union[List[str], str]) -> None:
		if isinstance(ports, str): ports: List[str] = ports.split()
		for port in ports:
			res = self.send( self.PORT_RESERVATION(port) )
			if "RESERVED_BY_OTHER" in res:
				self.send_expect_ok( self.PORT_RELINQUISH(port) )
			if "RESERVED_BY_YOU" in res:
				self.send_expect_ok( self.PORT_RELEASE(port) )

	# Reset a port/ports
	def port_reset(self, ports: Union[List[str], str]) -> None:
		if isinstance(ports, str): ports: List[str] = ports.split()
		self.port_reserve(ports)
		for port in ports:
			res = self.send_expect_ok( self.PORT_RESET(port) )
			
		time.sleep(1)

	## Start traffic on ports 
	def port_traffic_start(self, ports: Union[List[str], str]) -> None:
		if isinstance(ports, str): ports: List[str] = ports.split()
		for port in ports:
			res = self.send_expect_ok(self.PORT_TRAFFIC_ON(port) )

	## Stop traffic on ports 
	def port_traffic_stop(self, ports: Union[List[str], str]) -> None:
		if isinstance(ports, str): ports: List[str] = ports.split()
		for port in ports:
			res = self.send_expect_ok(self.PORT_TRAFFIC_OFF(port) )

	## Port speed selection
	def port_speed_selection(self, ports: Union[List[str], str], speed_mode: str = "AUTO") -> None:
		if isinstance(ports, str): ports: List[str] = ports.split()
		for port in ports:
			res = self.send_expect_ok(self.PORT_SPEEDSELECTION(port, speed_mode) )
	
