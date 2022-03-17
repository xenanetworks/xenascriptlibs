#!/usr/bin/python

import os, sys, time, getopt

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from TestUtilsL47 import XenaScriptTools

ports= []

def helptext():
	print
	print "Usage: %s [options] ipaddr nb_ipaddr nb_ports ramp_max ramp_min svr_port cli_port" % (sys.argv[0]) 
	print
	print "The total number of connections is nb_ipaddr*nb_ports"
	print "ramp_max and ramp_min are in miliseconds"
	print 'portlist must be of the form "m1/p1", "m2/p2" . For example'
	print 
	print '> ./Bisect.py 192.168.1.182 1000 1000 3000 600 1/0 1/1'
	print
	print "will create 1M tcp connections with port 0 on module 1 as server port"
	print "and port 1 on module 1 as client port. Ramp will start at 3000 ms and "
	print "iterates down to 600 ms, or lowest ramp time that passes"
	print
	print "Options:"
	print " -r res           resolution in ms for pass criteria"
	print " -n --nat         enable NAT (default OFF)"
	print " -e --pkteng=n    number of PE's allocated per port"
	print " -d               enable verbose debug "
	print " -a --arp         use arp in pre-run"
	print " -6               use ipv6 instead of ipv4"
	sys.exit(0)

def clientport():
   	return [ports[1]]

def serverport():
   	return [ports[0]]

def errexit(text):
	print "Status FAILED: " + text
	sys.exit(0)

def pollstats(xm, cg_id, t0, duration, fieldid, text, n, errtext):
	t1  = t0 
	retx = 0
	while t1-t0 < duration:
		time.sleep(0.2)
		stats = xm.Send(ports[0] + " P4G_TCP_STATE_CURRENT [{0}] ?".format(cg_id)).split()
		curr = int(stats[fieldid])
		sys.stdout.write("\r%6dms: %-12s %8d/%d [%-20s]\n" % (t1-t0, text, curr, n, "="*(20*curr/n)))
		sys.stdout.flush()
		t1 = int(stats[3])
		if curr == n:
			break

	for p in ports:
		tcpctr = xm.Send(p + " P4G_TCP_RETRANSMIT_COUNTERS [{0}] ?".format(cg_id)).split()
		retx = retx + int(tcpctr[10])
		retx = retx + int(tcpctr[11])

	if stats[fieldid] == str(n) and retx == 0:
		print " -- " + errtext + " - PASS"
		res = 1
	else:
		print " -- " + errtext + " - FAIL"
		res = 0

	return res

def oneramp(xm, cg_id, up, pause, down, n):
	global ports

	LOADPROFILE = "0 " + str(up) + " " + str(pause) + " " + str(down)

	xm.PortAddLoadProfile(clientport(), cg_id, LOADPROFILE, "msecs")
	xm.PortAddLoadProfile(serverport(), cg_id, LOADPROFILE, "msecs")

	for p in ports:
		xm.SendExpectOK(p + " P4G_CLEAR_COUNTERS [{0}]".format(cg_id))

	xm.PortPrepare(ports)

	xm.PortSetTraffic(ports, "prerun")
	xm.PortWaitState(ports, "PRERUN_RDY")

	xm.PortSetTraffic(serverport(), "on")
	xm.PortWaitState(serverport(), "RUNNING")
	xm.PortSetTraffic(clientport(), "on")
	xm.PortWaitState(clientport(), "RUNNING")

	time.sleep(0.1)

	stats = xm.Send(ports[0] + " P4G_TCP_STATE_CURRENT [{0}] ?".format(cg_id)).split()
	t0  = int(stats[3])
	
	stat_up = pollstats(xm, cg_id, t0, up + pause/2, 9, "ESTABLISHED", n, "RAMP UP")

	stat_dn = 0
	if stat_up == 1:
		stat_dn = pollstats(xm, cg_id, t0, up + pause + down + 2000, 5, "CLOSED", n, "RAMP DOWN")

	xm.PortStateOff(ports)

	return stat_up, stat_dn


def main():
	global ports
	c_res   = 5
	c_nat = 0
	c_pe    = 2
	c_debug = 0
	c_arp   = 0
	c_ipver = 4
	s_ipver = "IPv4"
	
	cg_id = 0

	try:
		opts, args = getopt.getopt(sys.argv[1:], "46adhr:pe:", ["nat", "pkteng=", "arp"])
	except getopt.GetoptError:
		helptext()
		return

	for opt, arg in opts:
		if opt == '-h':
			helptext()
			return
		elif opt in ("-r"):
			c_res = int(arg)
		elif opt in ("-n", "--nat"):
			c_nat = 1
		elif opt in ("-a", "--arp"):
			c_arp = 1
		elif opt in ("-d"):
			c_debug = 1
		elif opt in ("-6"):
			c_ipver = 6
			s_ipver = "IPv6"
		elif opt in ("-4"):
			c_ipver = 4
			s_ipver = "IPv4"
		elif opt in ("-e", "--pkteng"):
			c_pe = int(arg)

	if len(args) !=7:
		helptext()

	ports.append(args[5])
	ports.append(args[6])



	ip_address = args[0]
	nip = int(args[1])
	nprt= int(args[2])
	n   = nip*nprt
	ru_max = max(int(args[3]), int(args[4]))
	ru_min = min(int(args[3]), int(args[4]))
	rd_max = ru_max
	rd_min = ru_min

	print "==CONFIGURATION==========================================="
	print "CFG Ports:       " + " ".join(ports)
	print "CFG Connections: " + str(n)
	print "CFG IPversion:   " + s_ipver
	print "CFG NAT:       " + str(c_nat)
	print "CFG Prerun arp:  " + str(c_arp)
	print "CFG Resolution:  " + str(c_res)
	print "CFG Pkteng/Port: " + str(c_pe)
	print "CFG Debug:       " + str(c_debug)
	print

	xm = XenaScriptTools(ip_address)
	if c_debug:
		xm.debugOn()
	xm.haltOn()

	print "==PREPARATION==========================================="
	xm.Comment("Preparation")

	xm.LogonSetOwner("xena", "s_bisect")
	xm.PortReserve(ports)
	xm.PortReset(ports)
	
	if c_ipver == 6:
		CLIENT_RANGE = "0xaa01aa02aa03aa04aa05aa060a000001 " + str(nip) +" 10000 " + str(nprt) + " 65535"
		SERVER_RANGE = "0xbb01bb02bb03bb04bb05bb06bb07bb08 1 80 1"
	else:
		CLIENT_RANGE = "10.0.1.2 " + str(nip) +" 10000 " + str(nprt) + " 65535"
		SERVER_RANGE = "10.0.0.1 1 80 1"
	
	xm.PortAddConnGroup(ports, cg_id, CLIENT_RANGE, SERVER_RANGE, c_ipver)

	xm.PortRole(ports[1], cg_id, "client")
	xm.PortRole(ports[0], cg_id, "server")
	if c_nat:
		xm.SendExpectOK(ports[0] + " P4G_NAT [{0}] on".format(cg_id))

	xm.PortAllocatePE(ports, str(c_pe))
	
	for port in ports:
		#xm.SendExpectOK(port + " P4G_TCP_SYN_RTO [1] 10000 1 3")
		##xm.SendExpectOK(port + " P4G_TCP_RTO [1] static 10000 1 3")
		if c_arp:
			xm.SendExpectOK(port + " P4G_L2_USE_ADDRESS_RES [{0}] YES".format(cg_id))
		xm.SendExpectOK(port + " P4G_LP_TIME_SCALE [{0}] msec".format(cg_id))
		xm.SendExpectOK(port + " P4G_TEST_APPLICATION [{0}] NONE".format(cg_id))

	print "==EXECUTION==========================================="
	xm.Comment("Fast limit")

	print "== Phase 1: Fast Limit   ==             - Ramp up   %d CPS (%s ms)" % (n*1000/ru_min, ru_min)
	print "                                          Ramp down %d CPS (%d ms)" % (n*1000/rd_min, rd_min)
	res = oneramp(xm, cg_id, ru_min, 2000, ru_min, n)

	if res[0] == 1:
		errexit("Max ramp up   (fastest ramp passed) - rerun")
	if res[1] == 1:
		errexit("Max ramp down (fastest ramp passed) - rerun")

	ru = ru_max 
	rd = rd_max 

	for i in range(1, 21):
		xm.Comment("Ramp Up - Iteration %2d" % (i))
		print "== Phase 2: Ramp Up - iteration %2d ==   - Ramp up   %d CPS (%d ms)" % (i, n*1000/ru, ru)
		print "                                          Ramp down %d CPS (%d ms)" % (   n*1000/rd, rd)
		res = oneramp(xm, cg_id, ru, 2000, rd, n)

		if res[0] == 1:
			if res[1] == 1:
				rd_max = rd
			else:
				if rd == rd_max:
					errexit("Max ramp down (slowest ramp failed)")
				rd_min = rd
			rd = (rd_max + rd_min)/2
			ru_max = ru
		else:
			ru_min = ru
		ru = (ru_max + ru_min)/2

		if  (ru_max - ru_min) <= c_res :
			break;

		print 

	if (i == 20):
		errexit("Max Iterations reached")

	if ru_max == ru and res[0] == 0:
		errexit("Max ramp up (slowest ramp failed) - rerun")

	print
	for i in range(1, 21):
		xm.Comment("Ramp Down -Iteration %2d" % (i))
		print "== Phase 3: Ramp Down - iteration %2d == - Ramp down %d CPS (%d ms)" % (i , n*1000/rd, rd)

		res = oneramp(xm, cg_id, ru_max + 1000, 2000, rd, n)

		if (res[1] == 1):
			rd_max = rd
		else:
			rd_min = rd
		rd = (rd_max + rd_min)/2

		if (rd_max - rd_min) <= c_res :
			break;

		print 

	xm.Comment("Done")
	if (i == 20):
		errexit("Status FAILED: Max iterations reached - rerun")

	if rd_max ==  rd and res[1] == 0:
		errexit("Max ramp down (slowest ramp failed) - rerun")

	xm.PortRelease(ports)

	print "==RESULT=================================================="
	print "Max ramp up    %d CPS (%d ms)" % (n*1000/ru_max, ru_max)
	print "Max ramp down  %d CPS (%d ms)" % (n*1000/rd_max, rd_max)
	print "=========================================================="
	print "Status PASSED"

	
if __name__ == '__main__':
	sys.exit(main())
