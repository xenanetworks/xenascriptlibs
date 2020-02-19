#################################################################################
#																				#
# 				This script demonstrates how to run a simple test				#
#																				#
#################################################################################

import os
import sys
import time

from typing import Optional, Callable, Union, List, Dict, Any

from testutils.TestUtilsL23 import XenaScriptTools

def list_all_ports(xm):
	modules = xm.send("C_PORTCOUNTS ?").split()
	for i in range(len(modules)-1):
		print(f"Module {i}")
		ports = int(modules[i+1])
		if ports != 0:
			for port in range(ports):
				ps    = str(i) + "/" + str(port)
				interface = " ".join(xm.send(ps + " P_INTERFACE ?").split()[2:])
				if interface != "":
					speed = xm.send(ps + " P_SPEED ?").split()[2]
					print(f"Port: {ps}, {interface}, {speed}")

def list_port(xm, ports: Union[List[str], str]):
	if isinstance(ports, str): ports = ports.split()
	for port in ports:
		interface = " ".join(xm.send(port + " P_INTERFACE ?").split()[2:])
		if interface != "":
			speed = xm.send(port + " P_SPEED ?").split()[2]
			print(f"Port: {port}, {interface}, {speed}")

def create_stream(xm, ports: Union[List[str], str], number_of_streams: int):
	if isinstance(ports, str): ports = ports.split()
	RATE_FRACTION_PER_STREAM = int(1000000/number_of_streams)
	tpld_id = 0
	for port in ports:
		for i in range(number_of_streams):
			xm.send_expect_ok(f"{port} PS_CREATE [{i}]")
			xm.send_expect_ok(f"{port} PS_TPLDID [{i}] {tpld_id}")
			tpld_id += 1
			xm.send_expect_ok(f"{port} PS_ENABLE [{i}] ON")
			xm.send_expect_ok(f"{port} PS_PACKETLIMIT [{i}] -1")
			xm.send_expect_ok(f"{port} PS_COMMENT [{i}] \"{port} stream id {i}\"")
			xm.send_expect_ok(f"{port} PS_RATEFRACTION [{i}] {RATE_FRACTION_PER_STREAM}")
			xm.send_expect_ok(f"{port} PS_BURST [{i}] -1 100")
			xm.send_expect_ok(f"{port} PS_BURSTGAP [{i}] 0 0")
			
			# setup data for Ethernet header
			smac = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06]
			dmac = [0x11, 0x12, 0x13, 0x14, 0x15, 0x16]
			ethertype = [0xff, 0xff]

			# format Ethernet header data as a hex string
			headerdata = ''.join('{:02x}'.format(x) for x in dmac + smac + ethertype)
			xm.send_expect_ok(f"{port} PS_PACKETHEADER [0] 0x" + headerdata)
			xm.send_expect_ok(f"{port} PS_HEADERPROTOCOL [0] ETHERNET")

			xm.send_expect_ok(f"{port} PS_MODIFIERCOUNT [{i}] 0")
			xm.send_expect_ok(f"{port} PS_PACKETLENGTH [{i}] FIXED 1000 1518")
			xm.send_expect_ok(f"{port} PS_PAYLOAD [{i}] INCREMENTING 0x00")
			xm.send_expect_ok(f"{port} PS_INSERTFCS [{i}] ON")
			xm.send_expect_ok(f"{port} PS_IPV4GATEWAY [{i}] 0.0.0.0")
			xm.send_expect_ok(f"{port} PS_IPV6GATEWAY [{i}] 0x00000000000000000000000000000000")
			
def port_monitor(xm, ports: Union[List[str], str]):
	if isinstance(ports, str): ports = ports.split()
	for port in ports:
		txres = xm.send(f"{port} PT_TOTAL ?")
		rxres = xm.send(f"{port} PR_TOTAL ?")
		print(f"{txres}")
		print(f"{rxres}")
	time.sleep(1)

def stream_monitor(xm, ports: Union[List[str], str]):
	if isinstance(ports, str): ports = ports.split()
	for port in ports:
		print(xm.send(f"{port} PR_ALL ?"))

def stream_indices(xm, ports: Union[List[str], str]) -> Dict[str, List[str]]:
	if isinstance(ports, str): ports = ports.split()
	result = dict()
	for port in ports:
		res = xm.send(f"{port} PS_INDICES ?")
		indices = res.split("PS_INDICES")[-1]
		indices = indices.split(" ")[2:]
		result[f"{port}"] = indices
	return result




def main():
	ip_address = "192.168.1.200"
	test_ports = ["0/0", "0/1"]

	# Create an xenaserver object
	xm = XenaScriptTools(ip_address)	
	# Log on and set username
	xm.logon_set_owner("xena", "test")
	# Debug off/on
	xm.debug_on()
	# Reserve test ports
	xm.port_reserve(test_ports)
	# Reset test ports
	xm.port_reset(test_ports)
	xm.port_speed_selection(test_ports)

	#list_all_ports(xm)
	#list_port(xm, test_ports)

	# Create 10 streams on each port
	create_stream(xm, test_ports, 10)

	# Start port traffic simultaneously
	xm.chassis_traffic_on(test_ports)

	for _ in range(30):
		port_monitor(xm, test_ports)
		stream_monitor(xm, test_ports)

	xm.chassis_traffic_off(test_ports)
	

if __name__ == '__main__':
	main()
