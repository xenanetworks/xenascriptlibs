#!/usr/bin/python

import os, sys, time, getopt, math

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from TestUtilsL47 import XenaScriptTools

svrs = []
clis = []
ports= []

def helptext():
    print
    print "Usage: ./Ramp.py [options] IPaddr p1 p2 [p3 p4]*\n"
    print " Options "
    print "  -d        enable debug (default off)"
    print "  -n conns  number of connections (=ip addresses)"
    print "  -l lp     loadprofile as string., ex \"0 1000 5000 1000\"" 
    print "  -e n      number of PE's per port"
    print "  -t time   set retransmission timers"
    print "  -a --arp  use arp (ndp) in pre-run"
    print "  -g        use gw"
    print "  -6        use ipv6"
    print "  --cap=n   display up to n captured packets on each port"
    print

    
def main(argv):
    c_debug = 0
    c_lp    = "0 1000 5000 1000"
    c_conns = 1
    c_pe    = 1
    c_rto   = 0
    c_arp   = 0
    c_cap   = 0
    c_ipver = 4
    c_gw = 0
    
    cg_id = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "6adghl:n:e:t:", ["arp", "cap="])
    except getopt.GetoptError:
        helptext()
        return

    for opt, arg in opts:
        if opt == '-h':
            helptext()
            return
        elif opt in ("-d"):
            c_debug=1
        elif opt in ("-6"):
            c_ipver = 6
        elif opt in ("-g"):
            c_gw = 1
        elif opt in ("-a", "--arp"):
            c_arp=1
        elif opt in ("-e"):
            c_pe=arg
        elif opt in ("--cap"):
            c_cap= int(arg)
        elif opt in ("-n"):
            c_conns=int(arg)
        elif opt in ("-l"):
            c_lp=arg
        elif opt in ("-t"):
            c_rto=arg

    arglen = len(args) 
    if arglen < 3 or (arglen-1)%2 != 0:
        helptext()
        return

    ip_address = args[0]

    # Build list of server and client ports
    for i in range(arglen-1):
        if i%2 == 0:
            svrs.append(args[i+1])
        else:
            clis.append(args[i+1])

    ports = svrs + clis

    LOADPROFILE = c_lp

    xm = XenaScriptTools(ip_address)

    if c_debug:
        xm.debugOn()
    xm.haltOn()

    arpps= 1000*c_conns/int(c_lp.split()[1])

    print "==CONFIGURATION==========================================="
    
    print "CFG connections   %d" % (c_conns)
    print "CFG loadprofile   %s" % (c_lp)
    if c_arp:
      print "CFG arp           " + str(c_arp)
      print "CFG arp rate      %d" % (arpps)
    print "CFG debug         %d" % (c_debug)
    print "CFG ports         " + " ".join(ports)
    print "CFG pkteng        %s" % (c_pe)
    print "CFG capture       %d" % (c_cap)
    print


    
    if c_ipver == 6:
        #client_starting_ip = "0xaa01aa02aa03aa04aa05aa06aa07aa08"
        #server_starting_ip = "0xbb01bb02bb03bb04bb05bb06bb07bb08"
        #client_starting_port = "49152"
        #server_starting_port = "80"
       CLIENT_RANGE = "0xaa01aa02aa03aa04aa05aa06aa07aa08 " + str(c_conns) +" 49152 1 65535"
       SERVER_RANGE = "0xbb01bb02bb03bb04bb05bb06bb07bb08 1 80 1"
    else:
        #client_starting_ip = "10.0.0.2"
        #server_starting_ip = "11.0.0.2"
        #client_starting_port = "49152"
        #server_starting_port = "80"
       CLIENT_RANGE = "10.0.0.2 " + str(c_conns) +" 49152 1 65535"
       SERVER_RANGE = "11.0.0.2 1 80 1"

    print "==TEST EXECUTION=========================================="

    xm.LogonSetOwner("xena", "s_ramp")

    xm.PortReserve(ports)

    xm.PortReset(ports)

    xm.PortAddConnGroup(ports, cg_id, CLIENT_RANGE, SERVER_RANGE, c_ipver)
    xm.PortRole(clis, cg_id, "client")
    xm.PortRole(svrs, cg_id, "server")
    xm.PortAllocatePE(ports, str(c_pe))
    
    for port in ports:
        xm.SendExpectOK(port + " P4G_LP_TIME_SCALE [{0}] msec".format(cg_id))
        xm.PortAddLoadProfile(port, cg_id, LOADPROFILE, "msec")
        if c_cap:
            xm.SendExpectOK(port + " P4_CAPTURE ON")
        if c_arp:
            xm.SendExpectOK(port + " P4_ARP_REQUEST {0} 1000 3".format(arpps))
            xm.SendExpectOK(port + " P4G_L2_USE_ADDRESS_RES [{0}] YES".format(cg_id))
            xm.SendExpectOK(port + " P4_ARP_REQUEST 1000 1000 1")
        if c_gw:
            xm.SendExpectOK(port + " P4G_L2_USE_GW [{0}] YES".format(cg_id))
        if c_rto != 0:
            xm.SendExpectOK(port + " P4G_TCP_SYN_RTO [{0}] {1} 32 3".format(cg_id, c_rto))
            xm.SendExpectOK(port + " P4G_TCP_RTO [{0}] static {1} 32 3".format(cg_id, c_rto))
        xm.SendExpectOK(port + " P4_CLEAR_COUNTERS")
        xm.SendExpectOK(port + " P4G_TEST_APPLICATION [{0}] NONE".format(cg_id))

    t=0
    for dt in c_lp.split():
        t = t + int(dt)
    slp = t/1000 + 1

    print "Traffic PREPARE"
    xm.PortPrepare(ports)
    xm.PortWaitState(ports, "PREPARE_RDY")

    print "Traffic PRERUN"
    xm.PortSetTraffic(ports, "prerun")
    xm.PortWaitState(ports, "PRERUN_RDY")

    print "Traffic ON (servers)"
    xm.PortSetTraffic(svrs, "on")
    xm.PortWaitState(svrs, "RUNNING")

    print "Traffic ON (clients)"
    xm.PortSetTraffic(clis, "on")
    xm.PortWaitState(clis, "RUNNING")

    print "Sleeping " + str(slp) + " seconds"
    time.sleep(slp)

    print "Traffic STOP"
    xm.PortSetTraffic(ports, "stop")
    xm.PortWaitState(ports, "STOPPED")
    
    print "Getting TCP stats"
    n_est=0
    print "==SERVER======================================="
    for port in svrs:
        stats = xm.Send(port + " P4G_TCP_STATE_TOTAL [{0}] ?".format(cg_id))
        n_est = n_est + int(stats.split()[9])
        print "CLOSED: {0}".format(int(stats.split()[5]))
        print "LISTEN: {0}".format(int(stats.split()[6]))
        print "SYN_SENT: {0}".format(int(stats.split()[7]))
        print "SYN_RCVD: {0}".format(int(stats.split()[8]))                                  
        print "ESTABLISHED: {0}".format(int(stats.split()[9]))
        print "FIN_WAIT_1: {0}".format(int(stats.split()[10]))
        print "FIN_WAIT_2: {0}".format(int(stats.split()[11]))
        print "CLOSE_WAIT: {0}".format(int(stats.split()[12]))
        print "CLOSING: {0}".format(int(stats.split()[13]))
        print "LAST_ACK: {0}".format(int(stats.split()[14]))
        print "TIME_WAIT: {0}".format(int(stats.split()[15]))
    print "==CLIENT======================================="
    for port in clis:
        stats = xm.Send(port + " P4G_TCP_STATE_TOTAL [{0}] ?".format(cg_id))
        n_est = n_est + int(stats.split()[9])
        print "CLOSED: {0}".format(int(stats.split()[5]))
        print "LISTEN: {0}".format(int(stats.split()[6]))
        print "SYN_SENT: {0}".format(int(stats.split()[7]))
        print "SYN_RCVD: {0}".format(int(stats.split()[8]))                                  
        print "ESTABLISHED: {0}".format(int(stats.split()[9]))
        print "FIN_WAIT_1: {0}".format(int(stats.split()[10]))
        print "FIN_WAIT_2: {0}".format(int(stats.split()[11]))
        print "CLOSE_WAIT: {0}".format(int(stats.split()[12]))
        print "CLOSING: {0}".format(int(stats.split()[13]))
        print "LAST_ACK: {0}".format(int(stats.split()[14]))
        print "TIME_WAIT: {0}".format(int(stats.split()[15]))
    print "Requested conns: %d, established: %d" % (c_conns*len(svrs), n_est/2)

    if c_cap:
        print "==CAPTURE============================================"
        xm.PortGetPackets(ports, c_cap)

    xm.PrintPortStatistics(ports)
    print "==DONE============================================"

if __name__ == '__main__':
    sys.exit(main(sys.argv))
