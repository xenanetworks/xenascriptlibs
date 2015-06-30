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
   print " -p --proxy       enable proxy (default OFF)"
   print " -e --pkteng=n    number of PE's allocated per port"
   print " -d               enable verbose debug "
   print " -a --arp         use arp in pre-run"
   sys.exit(0)

def clientport():
   return [ports[1]]

def serverport():
   return [ports[0]]

def errexit(text):
    print "Status FAILED: " + text
    sys.exit(0)

def pollstats(xm, t0, duration, fieldid, text, n, errtext):
    t1  = t0 
    retx = 0
    while t1-t0 < duration:
        time.sleep(0.2)
        stats = xm.Send(ports[0] + " P4G_TCP_STATE_CURRENT [1] ?").split()
        curr = int(stats[fieldid])
        sys.stdout.write("\r%6dms: %-12s %8d/%d [%-20s]" % (t1-t0, text, curr, n, "="*(20*curr/n)))
        sys.stdout.flush()
        t1 = int(stats[3])
        if curr == n:
            break

    for p in ports:
        retx = retx + int(xm.Send(p + " P4G_TCP_RETRANSMIT_COUNTERS [1] ?").split()[10])
        retx = retx + int(xm.Send(p + " P4G_TCP_RETRANSMIT_COUNTERS [1] ?").split()[11])

    if stats[fieldid] == str(n) and retx == 0:
        print " -- " + errtext + " - PASS"
        res = 1
    else:
        print " -- " + errtext + " - FAIL"
        res = 0

    return res

def oneramp(xm, up, pause, down, n):
    global ports

    LOADPROFILE = "0 " + str(up) + " " + str(pause) + " " + str(down)

    xm.PortAddLoadProfile(clientport(), 1, LOADPROFILE, "msecs")
    xm.PortAddLoadProfile(serverport(), 1, LOADPROFILE, "msecs")

    for p in ports:
        xm.SendExpectOK(p + " P4G_CLEAR_COUNTERS [1]")

    xm.PortPrepare(ports)

    xm.PortSetTraffic(ports, "prerun")
    xm.PortWaitState(ports, "PRERUN_RDY")

    xm.PortSetTraffic(serverport(), "on")
    xm.PortWaitState(serverport(), "RUNNING")
    xm.PortSetTraffic(clientport(), "on")
    xm.PortWaitState(clientport(), "RUNNING")

    time.sleep(0.1)

    stats = xm.Send(ports[0] + " P4G_TCP_STATE_CURRENT [1] ?").split()
    t0  = int(stats[3])
    
    stat_up = pollstats(xm, t0, up + pause/2, 9, "ESTABLISHED", n, "RAMP UP")

    stat_dn = 0
    if stat_up == 1:
       stat_dn = pollstats(xm, t0, up + pause + down + 2000, 5, "CLOSED", n, "RAMP DOWN")

    xm.PortStateOff(ports)

    return stat_up, stat_dn


def main():
    global ports
    c_res   = 5
    c_proxy = 0
    c_pe    = 2
    c_debug = 0
    c_arp   = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "adhr:pe:", ["proxy", "pkteng=", "arp"])
    except getopt.GetoptError:
        helptext()
        return

    for opt, arg in opts:
        if opt == '-h':
            helptext()
            return
        elif opt in ("-r"):
            c_res = int(arg)
        elif opt in ("-p", "--proxy"):
            c_proxy = 1
        elif opt in ("-a", "--arp"):
            c_arp = 1
        elif opt in ("-d"):
            c_debug = 1
        elif opt in ("-e", "--pkteng"):
            c_pe = int(arg)

    if len(args) !=7:
        helptext()

    ports.append(args[5])
    ports.append(args[6])

    print "==CONFIGURATION==========================================="
    print "CFG Resolution: " + str(c_res)
    print "CFG Proxy:      " + str(c_proxy)
    print "CFG Pkteng/Port:" + str(c_pe)
    print "CFG Prerun arp: " + str(c_arp)
    print "CFG Debug:      " + str(c_debug)
    print "CFG Ports:      " + " ".join(ports)
    print


    ip_address = args[0]
    nip = int(args[1])
    nprt= int(args[2])
    n   = nip*nprt
    ru_max = max(int(args[3]), int(args[4]))
    ru_min = min(int(args[3]), int(args[4]))
    rd_max = ru_max
    rd_min = ru_min

    xm = XenaScriptTools(ip_address)
    if c_debug:
        xm.debugOn()
    xm.haltOn()

    print "==PREPARATION==========================================="

    xm.LogonSetOwner("xena", "s_bisect")
    xm.PortReserve(ports)
    xm.PortReset(ports)

    xm.PortAddConnGroup(ports, 1, "10.0.1.1 " + str(nip) + " 10000 " + str(nprt) , "10.0.0.1 1 80 1")
    xm.PortRole(ports[1], 1, "client")
    xm.PortRole(ports[0], 1, "server")
    if c_proxy:
       xm.SendExpectOK(ports[0] + " P4G_PROXY [1] on")

    for port in ports:
       #xm.SendExpectOK(port + " P4G_TCP_SYN_RTO [1] 10000 1 3")
       ##xm.SendExpectOK(port + " P4G_TCP_RTO [1] static 10000 1 3")
       if c_arp:
          xm.SendExpectOK(port + " P4G_L2_USE_ARP [1] YES")
       xm.SendExpectOK(port + " P4G_LP_TIME_SCALE [1] msec")
       xm.SendExpectOK(port + " P4G_TEST_APPLICATION [1] NONE")
       xm.SendExpectOK(port + " P4E_ALLOCATE " + str(c_pe))

    print "==EXECUTION==========================================="

    print "== Phase 1: Fast Limit   ==             - Ramp up   %d CPS (%s ms)" % (n*1000/ru_min, ru_min)
    print "                                          Ramp down %d CPS (%d ms)" % (n*1000/rd_min, rd_min)
    res = oneramp(xm, ru_min, 2000, ru_min, n)

    if res[0] == 1:
        errexit("Max ramp up   (fastest ramp passed) - rerun")
    if res[1] == 1:
        errexit("Max ramp down (fastest ramp passed) - rerun")

    ru = ru_max 
    rd = rd_max 
 
    for i in range(1, 21):
        print "== Phase 2: Ramp Up - iteration %2d ==   - Ramp up   %d CPS (%d ms)" % (i, n*1000/ru, ru)
        print "                                          Ramp down %d CPS (%d ms)" % (   n*1000/rd, rd)
        res = oneramp(xm, ru, 2000, rd, n)
   
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
        print "== Phase 3: Ramp Down - iteration %2d == - Ramp down %d CPS (%d ms)" % (i , n*1000/rd, rd)

        res = oneramp(xm, ru_max + 1000, 2000, rd, n)
   
        if (res[1] == 1):
            rd_max = rd
        else:
            rd_min = rd
        rd = (rd_max + rd_min)/2

        if (rd_max - rd_min) <= c_res :
            break;

        print 

    if (i == 20):
        errexit("Status FAILED: Max iterations reached - rerun")

    if rd_max ==  rd and res[1] == 0:
        errexit("Max ramp down (slowest ramp failed) - rerun")

    print "==RESULT=================================================="
    print "Max ramp up    %d CPS (%d ms)" % (n*1000/ru_max, ru_max)
    print "Max ramp down  %d CPS (%d ms)" % (n*1000/rd_max, rd_max)
    print "=========================================================="
    print "Status PASSED"
    
if __name__ == '__main__':
    sys.exit(main())
