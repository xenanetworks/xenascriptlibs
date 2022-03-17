import os, sys, time, threading, inspect, logging

from typing import Optional, Callable, Union, List, Dict, Any

from .SocketDrivers import SimpleSocket
from .PacketParse import *

LOGFILE         = "XENALOG"

RESET           = " p_reset"
RESERVATION     = " p_reservation ?"
RESERVE         = " p_reservation reserve"
RELINQUISH      = " p_reservation relinquish"
RELEASE         = " p_reservation release"
TRAFFIC         = " p4_traffic "
TRAFFIC_OFF     = " p4_traffic off"
TRAFFIC_STOP    = " p4_traffic stop"
TRAFFIC_PREPARE = " p4_traffic prepare"
STATE           = " p4_state ?"
SPEEDSEL        = " p4_speedselection "
PE_ALLOCATE     = " p4e_allocate "

def errexit(msg):
	print (f"Error: {msg}, exiting...")
	sys.exit(1)


class LoadProfile():

	def __init__(self, t0, t1, t2, t3, timescale):
		self.t0 = t0
		self.t1 = t1
		self.t2 = t2
		self.t3 = t3
		self.timescale = timescale

	def sett0(self, t0):
		self.t0 = t0

	def shape(self):
		return str(self.t0) + " " +  str(self.t1) + " " + str(self.t2) + " " + str(self.t3)

	def scale(self):
		return self.timescale

	def duration_sec(self):
		t = self.t0 + self.t1 + self.t2 + self.t3
		if self.timescale == "msecs":
			return t/1000
		elif self.timescale == "sec":
			return t
		else :
			errexit(f"unknown timescale: {self.timescale}")


## Keepalive thread to ensure tcp connection is kept open
# do not edit this 
class KeepAliveThread(threading.Thread):
	message = ''
	def __init__(self, connection, interval = 10):
		threading.Thread.__init__(self)
		self.connection = connection
		self.interval = interval
		self.finished = threading.Event()
		self.setDaemon(True)
		print(f'[KeepAliveThread] Thread initiated, interval {self.interval} seconds')

	def stop (self):
		self.finished.set()
		self.join()

	def run (self):
		while not self.finished.isSet():
			self.finished.wait(self.interval)
			self.connection.Ask(self.message)


## Low level driver for TCPIP based queried
# do not edit this
class XenaSocketDriver(SimpleSocket):

	def __init__(self, hostname, port = 22611):
		SimpleSocket.__init__(self, hostname = hostname, port = port)
		SimpleSocket.set_keepalives(self)
		self.access_semaphor = threading.Semaphore(1)

	def send_command(self, cmd):
		self.access_semaphor.acquire()
		print(f"Sending command: {cmd}")
		SimpleSocket.send_command(self, cmd)
		self.access_semaphor.release()

	def Ask(self, cmd):
		self.access_semaphor.acquire()
		reply = SimpleSocket.ask(self, cmd).strip('\n')
		self.access_semaphor.release()
		return reply


## Xena supplied class example for Scripting via Python
# feel free to add functions below
# 
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

	PORT_L47_TRAFFIC_ON     = lambda self, port: f"{ port } P4_TRAFFIC ON"
	PORT_L47_TRAFFIC_OFF    = lambda self, port: f"{ port } P4_TRAFFIC OFF"
	PORT_L47_TRAFFIC_STOP   = lambda self, port: f"{ port } P4_TRAFFIC STOP"
	PORT_L47_TRAFFIC_PREPARE   = lambda self, port: f"{ port } P4_TRAFFIC PREPARE"
	PORT_L47_TRAFFIC_PRERUN    = lambda self, port: f"{ port } P4_TRAFFIC PRERUN"

	states_passive = ["STOPPED", "OFF", "PREPARE", "PREPARE_RDY" ]
	states_active  = ["RUNNING", "PRERUN_RDY", "PRERUN" ]


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
			lf = open(self.logf, 'w')
			for cmd in self.cmds:
				lf.write(cmd + "\n")
			lf.close()
		return

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
				self.debug_message(f"send_expect() failed")
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
			self.debug_message(f"send_and_match() failed")
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
		self.send(f"C_LOGOFF")


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
			self.debug_message(f"Chassis is reserved by other - relinquish")
			self.send_expect_ok( self.CHASSIS_RELINQUISH() )
			self.send_expect_ok( self.CHASSIS_RESERVE() )

		elif "RELEASED" in res:
			self.send_expect_ok( self.CHASSIS_RESERVE() )

	# Reserve chassis, release or relinquish first if necessary
	def chassis_release(self):
		res = self.send( self.CHASSIS_RESERVATION() ).split()[1]

		if "RESERVED_BY_YOU" in res:
			self.debug_message(f"Chassis is reserved by me - release")
			self.send_expect_ok( self.CHASSIS_RELEASE() )

		elif "RESERVED_BY_OTHER" in res:
			self.debug_message(f"Chassis is reserved by other - relinquish")
			self.send_expect_ok( self.CHASSIS_RELINQUISH() )

		elif "RELEASED" in res:
			self.debug_message(f"Chassis is released - do nothing")

		else:
			self.errexit(f"Halting in line { inspect.currentframe().f_back.f_lineno }")


	#############################################################
	# 						Misc Commands 						#
	#############################################################
	def comment(self, text):
		self.send(f"; ######################################")
		self.send(f"; {text}")
		self.send(f"; ######################################")


	#############################################################
	# 						Module Commands 					#
	############################################################

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

	# Reserve the module
	def module_reserve(self, module):
		self.module_release(module)
		mod = str(module)
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
		
	## Release a port/ports
	def port_release(self, ports: Union[List[str], str]):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			res = self.send_expect_ok( self.PORT_RELEASE(port) )


	## Wait for port to be in state 'state' - warning can hang forever!
	def port_wait_state(self, ports: Union[List[str], str], state: str):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			running = 1
			while running:
				res = self.send(port + STATE)
				if res.find(state) != -1:
					running = 0
				else:
					time.sleep(0.1)

	## Set port in state OFF - valid from any port state
	def port_state_off(self, ports: Union[List[str], str]):
		if isinstance(ports, str): ports = ports.split()
		for port in ports: 
			res = self.send(port + STATE).split()[2]
			if res in self.states_active:
				self.send(port + TRAFFIC_STOP)
				self.port_wait_state(port, "STOPPED")
		for port in ports:
			self.send(port + TRAFFIC_OFF)
			self.port_wait_state(port, "OFF")


	## Set port state to 'state' - assume ports are in relevant state
	def port_set_traffic(self, ports: Union[List[str], str], state):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			self.send_expect_ok(port + TRAFFIC + state) 

	## Set port speed
	def port_set_speed(self, ports: Union[List[str], str], speed):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			self.send_expect_ok(port + SPEEDSEL + speed)

	## Verify port speed
	def port_verify_speed(self, ports: Union[List[str], str], speed):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			res = self.send(port + SPEEDSEL + "?").split()[2]
			if res.find(speed) == -1:
				self.errexit(f"Port Speed mismatch on port {port}, expected {speed}, but got {res}")


	## Reset ports -  - valid from any port state
	def port_reset(self, ports: Union[List[str], str]):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			self.send_expect_ok(port + RESET)
			self.port_wait_state(port, "OFF")


	## Send traffic Prepare - assume ports are in state OFF 
	def port_prepare(self, ports: Union[List[str], str]):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			self.send_expect_ok(port + TRAFFIC_PREPARE)
			self.port_wait_state(port, "PREPARE_RDY")


	## Set port role - assume ports are in state OFF
	def port_role(self, ports: Union[List[str], str], id, role):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			SID = " [" + str(id) + "] "
			self.send_expect_ok(port + " P4G_ROLE " + SID + " " + role)

	## Allocate PEs
	def port_allocate_pe(self, ports: Union[List[str], str], nbpe: int):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			self.send_expect_ok(port + PE_ALLOCATE + str(nbpe))


	#############################################################
	# 			Connection Group Commands 						#
	#############################################################

	def port_add_conn_group(self, ports: Union[List[str], str], id, clients, servers, ipver):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			self.send_expect_ok(f"{port} P4G_CREATE [{id}]")
			if ipver == 6:
				PREFIX="IPV6_"
				self.send_expect_ok(f"{port} P4G_IP_VERSION [{id}] IPV6")
			else:
				PREFIX=""

			self.send_expect_ok(f"{port} P4G_{PREFIX}CLIENT_RANGE [{id}] {clients}")
			self.send_expect_ok(f"{port} P4G_{PREFIX}SERVER_RANGE [{id}] {servers}")
			


	def port_add_load_profile(self, ports: Union[List[str], str], id, lp_shape, lp_timescale):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			self.send_expect_ok(f"{port} P4G_LP_SHAPE [{id}] {lp_shape}")
			self.send_expect_ok(f"{port} P4G_LP_TIME_SCALE [{id}] {lp_timescale}")


	def port_set_role(self, ports: Union[List[str], str], id, role):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			self.send_expect_ok(f"{port} P4G_ROLE [{id}] {role}")
		

	def port_get_packets(self, ports: Union[List[str], str], n):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			first=1
			pp = PacketParse()
			print (f"Port: {port}")
			for i in range(n):
				if first:
					res = self.send(f"{port} P4_CAPTURE_GET_FIRST ?")
					first=0
				else:
					res = self.send(f"{port} P4_CAPTURE_GET_NEXT ?")
				pp.parse(res)

	def port_get_rx_packets(self, port):
		res = self.send(f"{port} P4_ETH_RX_COUNTERS ?")
		packets = int(res.split()[7])
		return packets, res


	def port_clear_counters(self, ports: Union[List[str], str]):
		if isinstance(ports, str): ports = ports.split()
		for port in ports:
			self.send_expect_ok("{port} P4_CLEAR_COUNTERS")
		

	def print_port_statistics(self, ports: Union[List[str], str]):
		if isinstance(ports, str): ports = ports.split()

		print("%-5s %-3s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s" % ("Port", "Dir", "Pkts", "IP", "ARPREQ", "ARPREP", "IP6", "NDPREQ", "NDPREP", "TCP"))

		for port in ports:
			for dir in ["RX", "TX"]:
				eth    = self.send(f"{port} P4_ETH_{dir}_COUNTERS ?").split()
				pkt    = eth[7]
				
				proto  = self.send(f"{port} P4_IPV4_{dir}_COUNTERS ?").split()
				ip     = proto[4]
				
				proto  = self.send(f"{port} P4_ARP_{dir}_COUNTERS ?").split()
				arpreq = proto[4]
				arprep = proto[5]
				
				proto  = self.send(f"{port} P4_TCP_{dir}_COUNTERS ?").split()
				tcp    = proto[4]

				proto6  = self.send(f"{port} P4_IPV6_{dir}_COUNTERS ?").split()
				ip6    = proto6[4]
				
				proto6  = self.send(f"{port} P4_NDP_{dir}_COUNTERS ?").split()
				ndpreq = proto6[4]
				ndprep = proto6[5]
				print("%-5s %-3s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s" % (port, dir, pkt, ip, arpreq, arprep, ip6, ndpreq, ndprep, tcp))



	#########################################################################
	# 			Regression Testing Helper Functions 						#
	#########################################################################

	def test_pre(self, ports: Union[List[str], str]):
		print("TestPre()")

		print("  Reserve ports " + " ".join(ports))
		self.port_reserve(ports)

		print("  Reset ports")
		self.port_reset(ports)

		self.port_allocate_pe(ports, 2)


	def test_post(self, ports: Union[List[str], str]):
		print("TestPost()")
		print("  Set ports to off")
		self.port_state_off(ports)


	def test_prepare_and_start(self, servers, clients):
		ports = servers + clients
		print("  Prepare ports")
		self.port_prepare(ports)

		print("  Start servers")
		self.port_set_traffic(servers, "ON")
		self.port_wait_state(servers, "RUNNING")

		print("  Start clients")
		self.port_set_traffic(clients, "ON")
		self.port_wait_state(clients, "RUNNING")


	def test_validate_goodput_rx(self, cgis, ports: Union[List[str], str], bytes_pr_cg):
		self.test_validate_goodput(cgis, ports, 1, bytes_pr_cg)


	def test_validate_goodput_tx(self, cgis, ports: Union[List[str], str], bytes_pr_cg):
		self.test_validate_goodput(cgis, ports, 0, bytes_pr_cg)


	def test_validate_goodput(self, cgis, ports: Union[List[str], str], rx, bytes_pr_cg):
		if rx == 1:
			CMD = "P4G_TCP_RX_PAYLOAD_COUNTERS"
			TXT = "Rx"
		elif rx == 0:
			CMD = "P4G_TCP_TX_PAYLOAD_COUNTERS"
			TXT = "Tx"
		else:
			self.errexit(f"TestValidateGoodPut() invalid value of rx: {rx}")

		print("    validating goodput bytes ({TXT})")

		good_bytes=0
		nb_ports = len(ports)
		for port in ports:
			for cgi in range(cgis):
				sres = self.send(port + CMD + "[" + str(cgi) + "] ?").split()[7]
				res = int(sres)
				if res != bytes_pr_cg:
					print(f"    [{cgi}] {TXT} {rex} bytes, expected {bytes_pr_cg}")
				good_bytes = good_bytes + res

		if good_bytes != nb_ports * cgis * bytes_pr_cg:
			 self.errexit(f"{TXT} Failed: Expected {cgis * bytes_pr_cg} bytes, got {good_bytes}")
	


	def test_setup_application_raw(self, ports: Union[List[str], str], cgi, scenario, utilization, len):
		print("      [%02d] Appl: raw, Scen: %s, Util: %d, Len: %d" % (cgi, scenario, utilization, len))
		for port in ports:
			self.send_expect_ok(f"{port} P4G_TEST_APPLICATION [{cgi}] RAW")
			self.send_expect_ok(f"{port} P4G_RAW_TEST_SCENARIO [{cgi}] {scenario}")
			self.send_expect_ok(f"{port} P4G_RAW_PAYLOAD_TYPE [{cgi}] INCREMENT")
			self.send_expect_ok(f"{port} P4G_RAW_PAYLOAD_TOTAL_LEN [{cgi}] FINITE {str(len)}")
			self.send_expect_ok(f"{port} P4G_RAW_HAS_DOWNLOAD_REQ [{cgi}] NO")
			self.send_expect_ok(f"{port} P4G_RAW_CLOSE_CONN [{cgi}] NO")
			self.send_expect_ok(f"{port} P4G_RAW_TX_DURING_RAMP [{cgi}] NO NO")
			self.send_expect_ok(f"{port} P4G_RAW_UTILIZATION [{cgi}] {str(utilization)}")
			self.send_expect_ok(f"{port} P4G_TCP_WINDOW_SIZE [{cgi}] 65535")
			self.send_expect_ok(f"{port} P4G_TCP_MSS_VALUE [{cgi}] 1460")

####################################################################

	def test_port_speed_change(self, portlist):
		print("test_port_speed_change()")

		self.test_pre(portlist)

		speeds = [ "F1G", "F10G" ]

		for speed in speeds:
			print(f"  Setting portspeed to {speed}")
			self.port_set_speed(portlist, speed)
			time.sleep(1)

			print(f"  Verifying portspeed {speed}")
			self.port_verify_speed(portlist, speed)
			time.sleep(1)

		self.test_post(portlist)
		print("PASS")

####################################################################

	def test_connection_groups(self, n, conn_pr_cg, clients, servers):
		print("test_connection_groups()")

		ports = clients + servers
		if n > 200:
			errexit(f"Too many ({n}) Connection Groups (max 200)")

		if n * conn_pr_cg > 4000000:
			errexit(f"Number of connections ({n * conn_pr_cg}) exceed 4M")

		print (f"  {n} connection groups requested")

		self.test_pre(ports)

		bytes_pr_conn   = 1000
		ramp = (n*conn_pr_cg*1000)/500000 + 1

		cln_rng_t = ".0.0.2 " + str(conn_pr_cg) + " 40000 1"
		svr_rng_t = ".0.0.1 1 80 1"
		lp = LoadProfile(0, ramp, 6000, ramp, "msecs")

		print(f"    setting up connection groups")
		for cgi in range(n):
			client_range = str(10 + cgi) + cln_rng_t
			server_range = str(10 + cgi) + svr_rng_t
			print(f"      [%2d] client: %s, server: %s, lp_shape: \"%s\" %s" % (cgi, client_range, server_range, lp.shape(), lp.scale()))
			self.port_add_conn_group(ports, cgi, client_range, server_range)

			print("      [%2d] clients: %s, servers: %s" % (cgi, " ".join(clients), " ".join(servers)))
			self.port_set_role(clients, cgi, "client")
			self.port_set_role(servers, cgi, "server")

			self.port_add_load_profile(ports, cgi, lp.shape(), lp.scale())

		print("    verifying created connection groups")
		for port in ports:
			print("      verifying connection groups on port {port}")
			cg = self.send(f"{port} P4G_INDICES ?").split()
			if len(cg) != n + 2:
				self.errexit(f"number of cgs ({len(cg)-2, n}) does not match expected (%d)")

		util = int(1000000/n/2)
		print(f"    setting application RAW, DOWNLAOD, Utilization {util}")
		for cgi in range(n):
			self.test_setup_application_raw(ports, cgi, "DOWNLOAD", util, bytes_pr_conn)

		self.test_prepare_and_start(servers, clients)

		duration = lp.duration_sec() + 3
		for i in range(duration):
			time.sleep(1)
			for port in ports:
				res = self.port_get_rx_packets(port)
				print("%3ds %s" % (duration -i, res[1]))

		#print "  Stopping Ports"
		self.port_set_traffic(ports, "STOP")

		self.test_validate_goodput_tx(n, servers, bytes_pr_conn * conn_pr_cg)
		self.test_validate_goodput_rx(n, clients, bytes_pr_conn * conn_pr_cg)

		self.test_post(ports)
		print("PASS")

	#########################################################################
	# 			Regression Testing Main Functions   						#
	#########################################################################


	def regression_test_speed(self, portlist):
		print("Regression test port speed")
		print(f"Logging on to chassis {self.ip}")

		self.log_on("xena")
		self.test_port_speed_change(portlist)


	def RegressionTest(self, portpairs, nb_cgs, conn_pr_cg):
		servers = []
		clients = []

		print()
		print("Regression test")

		if len(portpairs)%2 != 0:
			self.errexit("portpair list is odd")

		for i in range(len(portpairs)):
			if i%2 == 0:
				servers.append(portpairs[i])
			else:
				clients.append(portpairs[i])

		self.debug_message("Clients " + " ".join(clients))
		self.debug_message("Servers " + " ".join(servers))

		print(f"Logging on to chassis {self.ip}")
		self.log_on("xena")

		self.test_connection_groups(nb_cgs, conn_pr_cg, clients, servers)

		print("DONE")
