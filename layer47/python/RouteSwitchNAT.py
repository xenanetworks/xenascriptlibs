#!/usr/bin/python

import os, sys, time, getopt, math

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from TestUtilsL47 import XenaScriptTools

ports= []

def helptext():
    print
    print "Usage: ./RouteSwitchNAT.py [options] ChassisIP cli_ip svr_ip nat_ip p1 p2\n"
    print " Options "
    print "  -d          enable debug (default off)"
    print "  -n conns    number of connections (=ip addresses) (default 1)"
    print "  -l lp       loadprofile as string., ex \"0 1000 5000 1000\"(default)" 
    print "  -e pkteng   number of PE's per port (default 1)"
    print "  --cap=n     display up to n captured packets on each port (default 0)"
    print "  --noarp     do not send arp requests in pre-run"
    print
    print " Note that ip addresses must be on the format 10.0.0 leaving out "
    print " the last number and full-stop"
    print
    print "Example:"
    print " ./RouteSwitchNAT.py  192.168.1.182  12.0.0  8.0.0  0.0.0 7/0  7/1"
    print " client gw is 12.0.0.1, clients start at 12.0.0.2, etc."
    print


def main(argv):
    c_debug  = 0
    c_lp     = "0 1000 5000 1000"
    c_conns  = 1
    c_pe     = 1
    c_cap    = 0
    c_nat    = 0
    c_noarp  = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "dhl:n:e:", ["cap=", "noarp"])
    except getopt.GetoptError:
        helptext()
        return

    for opt, arg in opts:
        if opt == '-h':
            helptext()
            return
        elif opt in ("-d"):
            c_debug=1
        elif opt in ("-e"):
            c_pe=arg
        elif opt in ("--cap"):
            c_cap= int(arg)
        elif opt in ("-n"):
            c_conns=int(arg)
        elif opt in ("--noarp"):
            c_noarp = 1
        elif opt in ("-l"):
            c_lp=arg

    arglen = len(args) 
    if arglen != 6:
        helptext()
        return

    l47_server    = args[0]
    cln_ip        = args[1]
    svr_ip        = args[2]
    nat_ip        = args[3]
    svrp          = args[4]
    clnp          = args[5]

    if cln_ip == svr_ip:
        c_routed = 0
        c_topo = "switched"
    else:
        c_routed = 1
        c_topo = "routed"

    if nat_ip != "0.0.0":
        c_nat = 1
        c_topo = "nat"

    ports = [svrp] + [clnp]

    LOADPROFILE = c_lp

    xm = XenaScriptTools(l47_server)

    if c_debug:
        xm.debugOn()
    xm.haltOn()

    arpps= 1000*c_conns/int(c_lp.split()[1])

    if c_nat:
        if c_routed:
            print "Combination of NAT and Routed NW not supported"
            return

    SVR_GW = svr_ip + ".1"
    SVR_IP = svr_ip + ".2"

    CLN_GW = cln_ip + ".1"
    CLN_IP = cln_ip + ".3"

    NAT_GW = nat_ip + ".1"
    NAT_IP = nat_ip + ".2"

    print "==CONFIGURATION==========================================="
    print "CFG connections     %d" % (c_conns)
    print "CFG loadprofile     %s" % (c_lp)
    print "CFG arp rate        %d" % (arpps)
    print "CFG Suppress ARP    %d" % (c_noarp)
    print "CFG debug           %d" % (c_debug)
    print "CFG ports           %s" % (" ".join(ports))
    print "CFG pkteng          %s" % (c_pe)
    print "CFG capture         %d" % (c_cap)
    print "CFG NW Topo         %s" % (c_topo)
    print "CFG cln_ip          %s" % (CLN_IP) 
    print "CFG svr_ip          %s" % (SVR_IP) 
    
    if c_nat:
        print "CFG NAT_IP          %s" % (NAT_IP)
        print "CFG NAT_GW          %s" % (NAT_GW)
    else:
        if c_routed:
            print "CFG svr_gw          %s" % (SVR_GW)
            print "CFG cln_gw          %s" % (CLN_GW)
    print

    print "==TEST EXECUTION=========================================="

    xm.Comment("Logon and Reserve")

    xm.LogonAndReserve(ports, "xena", "s_route")

    xm.PortReset(ports)

    CLI_RNG = CLN_IP + " " + str(c_conns) + " 10000 1"
    SVR_RNG = SVR_IP + " 1 80 1"
    NAT_RNG = NAT_IP + " 1 80 1"
    
    xm.Comment("Configure")
    xm.PortAddConnGroup(clnp, 1, CLI_RNG, SVR_RNG, 4)
    if c_nat:
        xm.PortAddConnGroup(svrp, 1, CLI_RNG, NAT_RNG, 4)
    else:
        xm.PortAddConnGroup(svrp, 1, CLI_RNG, SVR_RNG, 4)

    xm.PortRole(clnp, 1, "client")
    xm.PortRole(svrp, 1, "server")

    if c_topo == "routed":
        xm.SendExpectOK(clnp + " P4G_L2_GW [1] "+ CLN_GW + " 0x010101010101")
        xm.SendExpectOK(clnp + " P4G_L2_USE_GW [1] YES")
        xm.SendExpectOK(svrp + " P4G_L2_GW [1] "+ SVR_GW + " 0x020202020202")
        xm.SendExpectOK(svrp + " P4G_L2_USE_GW [1] YES")
        if not c_noarp:
            xm.SendExpectOK(clnp + " P4G_L2_USE_ARP [1] YES")
            xm.SendExpectOK(svrp + " P4G_L2_USE_ARP [1] YES")
    elif c_topo == "switched":
        if not c_noarp:
            xm.SendExpectOK(clnp + " P4G_L2_USE_ARP [1] YES")
            xm.SendExpectOK(svrp + " P4G_L2_USE_ARP [1] YES")
    elif c_topo == "nat":
        xm.SendExpectOK(svrp + " P4G_PROXY [1] ON")
        if not c_noarp:
            xm.SendExpectOK(clnp + " P4G_L2_USE_ARP [1] YES")
    else:
        print "Internal Error"
        return

    for port in ports:
        xm.SendExpectOK(port + " P4_ARP_REQUEST " + str(arpps) + " 1000 3");
        xm.SendExpectOK(port + " P4E_ALLOCATE " + str(c_pe))
        xm.PortAddLoadProfile(port, 1, LOADPROFILE, "msec")
        if c_cap:
            xm.SendExpectOK(port + " P4_CAPTURE ON")
        xm.SendExpectOK(port + " P4_CLEAR_COUNTERS")
        xm.SendExpectOK(port + " P4G_TEST_APPLICATION [1] NONE")

    t=0
    for dt in c_lp.split():
        t = t + int(dt)
    slp = t/1000 + 1

    xm.Comment("Prepare and Run")
    print "Traffic PREPARE"
    xm.PortPrepare(ports)
    xm.PortWaitState(ports, "PREPARE_RDY")

    print "Traffic PRERUN"
    xm.PortSetTraffic(ports, "prerun")
    xm.PortWaitState(ports, "PRERUN_RDY")

    print "Traffic ON (servers)"
    xm.PortSetTraffic(svrp, "on")
    xm.PortWaitState(svrp, "RUNNING")

    print "Traffic ON (clients)"
    xm.PortSetTraffic(clnp, "on")
    xm.PortWaitState(clnp, "RUNNING")

    print "Sleeping " + str(slp) + " seconds"
    time.sleep(slp)

    xm.Comment("Stop traffic, and collect statistics")
    print "Traffic STOP"
    xm.PortSetTraffic(ports, "stop")
    xm.PortWaitState(ports, "STOPPED")
    for port in ports:
        if c_cap:
            xm.SendExpectOK(port + " P4_CAPTURE OFF")
    
    print "Getting TCP stats"
    n_est=0
    print "==SERVER======================================="
    stats = xm.Send(svrp + " P4G_TCP_STATE_TOTAL [1] ?")
    n_est = n_est + int(stats.split()[9])
    print stats
    print "==CLIENT======================================="
    stats = xm.Send(clnp + " P4G_TCP_STATE_TOTAL [1] ?")
    n_est = n_est + int(stats.split()[9])
    print stats
    print "Requested conns: %d, established: %d" % (c_conns*len(svrp), n_est/2)
    xm.PrintPortStatistics(ports)

    if c_cap:
        xm.Comment("Extract captured packets")
        print "==CAPTURE============================================"
        xm.PortGetPackets(ports, c_cap)
        for port in ports:
            xm.SendExpectOK(port + " P4_CAPTURE OFF")

    print "==DONE============================================"

    xm.PortStateOff(ports)

    xm.PortRelease(ports)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
