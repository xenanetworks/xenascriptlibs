#!/usr/bin/python

import os, sys, time, getopt

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from TestUtilsL47 import XenaScriptTools

svrs = []
clis = []
ports= []

def helptext():
   print
   print "Usage: %s [options] IPaddr svr_port1 cli_port1 [svr_port2 cli_port2]*\n" % (sys.argv[0])
   print "Ramps conns up and down according to load profile, and sends payload" 
   print "Default is 1M connections, load profile (ms) \"0 5000 5000 5000\", utilization 1000000 (== 100%)"
   print
   print "Options"
   print " -s scenario  raw mode test scenario: DOWNLOAD/BOTH"
   print " -d           enable debug (default is 0)"
   print " -p           enable proxy (default is 0)"
   print " -proxy       same as -p"
   print " -e N         allocate N PE's per port (default is 1)"
   print " -n conns     specify the number of requested connections"
   print " -u util      specify payload utilization in ppm (100% == 1000000)"
   print " --pkteng=N   same as -e"
   print " -w N         sets the TCP window"
   print " -m MSS       sets the MSS value - default is 1460"
   return


def getrtxstat(xm, ports):
   s_dupack=0
   s_ooseg=0
   s_rtxevt=0
   s_rtxseg=0
   s_rto=0
   s_syn=0
   s_fin=0
   for p in ports:
      res = xm.Send(p + " P4G_TCP_RETRANSMIT_COUNTERS [1] ?").split()
      s_dupack = s_dupack + int(res[5]) 
      s_ooseg  = s_ooseg  + int(res[6]) 
      s_rtxevt = s_rtxevt + int(res[7]) 
      s_rtxseg = s_rtxseg + int(res[8]) 
      s_rto    = s_rto    + int(res[9]) 
      s_syn    = s_syn    + int(res[10]) 
      s_fin    = s_fin    + int(res[11]) 

   print "RTX Stats: rx-dupack: %d  r-ooseg: %d  fast-rtx-events: %d  fast-rtx-seg: %d  rto-rtx: %d  syn-rtx: %d  fin-rtx: %d" % \
     (s_dupack, s_ooseg, s_rtxevt, s_rtxseg, s_rto, s_syn, s_fin)

   return 
   
    
def main():

   c_debug = 0
   c_proxy = 0
   c_pe    = 1
   c_lp    = "0 5000 5000 5000"
   c_conns = 1000000
   c_util  = 948400
#   c_util  = 1000000
   c_tcp_wnd  = 65535
   c_tcp_mss  = 1460
   c_scenario = "BOTH"

   try:
      opts, args = getopt.getopt(sys.argv[1:], "hdpe:l:n:u:w:s:m:", ["proxy", "pkteng=", "loadprofile=", "scenario=", "mss="])
   except getopt.GetoptError:
      helptext()
      return

   for opt, arg in opts:
       if opt == '-h':
          helptext()
          return
       elif opt in ("-p", "--proxy"):
          c_proxy=1
       elif opt in ("-d"):
          c_debug=1
       elif opt in ("-e", "--pkteng"):
          c_pe = int(arg)
       elif opt in ("-l", "--loadprofile"):
          c_lp = arg
       elif opt in ("-s", "--scenario"):
          c_scenario = arg 
       elif opt in ("-m", "--mss"):
          c_tcp_mss = arg 
       elif opt in ("-u"):
          c_util=int(arg)
       elif opt in ("-n"):
          c_conns = int(arg)
       elif opt in ("-w"):
          c_tcp_wnd = int(arg)

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

   duration=0
   for dt in c_lp.split():
      duration = duration + int(dt)

   print
   print "==CONFIGURATION==========================================="
   print "CFG connections : %d" % (c_conns)
   print "CFG utilization : %d" % (c_util)
   print "CFG load profile: %s" % (c_lp)
   print "CFG scenario    : %s" % (c_scenario)
   print "CFG duration    : %d" % (duration)
   print "CFG pkteng      : %d" % (c_pe)
   print "CFG proxy       : %d" % (c_proxy)
   print "CFG TCP window  : %d" % (c_tcp_wnd)
   print "CFG TCP MSS     : %s" % (c_tcp_mss)
   print "CFG debug       : %d" % (c_debug)
   print "CFG server ports:" + " ".join(svrs) 
   print "CFG client ports:" + " ".join(clis) 

   ports = svrs + clis

   if c_scenario == "DOWNLOAD":
      ports_rx = clis
      ports_tx = svrs
   elif c_scenario == "BOTH":
      ports_rx = ports
      ports_tx = ports 
   else:
      ports_rx = ""
      ports_tx = ""

   xm    = XenaScriptTools(ip_address)
   if c_debug:
      xm.debugOn()
   xm.haltOn()

   LOADPROFILE = c_lp

   print "==TEST EXECUTION=========================================="

   xm.LogonSetOwner("xena", "s_payl")
 
   xm.PortReserve(ports)
   xm.PortReset(ports)

   xm.PortAddConnGroup(ports, 1, "10.0.0.2 " + str(c_conns) +" 40000 1", "10.0.0.1 1 50000 1")
   xm.PortRole(clis, 1, "client")
   xm.PortRole(svrs, 1, "server")
   if c_proxy:
      for port in svrs:
         xm.SendExpectOK(port + " P4G_PROXY [1] on")
   for port in ports:
      xm.SendExpectOK(port + " P4_CLEAR_COUNTERS")
   nports=0
   for port in ports:
      nports = nports + 1
      xm.SendExpectOK(port + " P4E_ALLOCATE " + str(c_pe))
      xm.SendExpectOK(port + " P4G_LP_TIME_SCALE [1] msec")
      xm.SendExpectOK(port + " P4G_TEST_APPLICATION [1] RAW")
      xm.SendExpectOK(port + " P4G_RAW_TEST_SCENARIO [1] " + c_scenario)
      xm.SendExpectOK(port + " P4G_RAW_PAYLOAD_TYPE [1] INCREMENT")
#      xm.SendExpectOK(port + " P4G_RAW_PAYLOAD_TYPE [1] FIXED")
      xm.SendExpectOK(port + " P4G_RAW_HAS_DOWNLOAD_REQ [1] NO")
      xm.SendExpectOK(port + " P4G_RAW_CLOSE_CONN [1] NO")
      xm.SendExpectOK(port + " P4G_RAW_PAYLOAD_TOTAL_LEN [1] INFINITE 0")
      xm.SendExpectOK(port + " P4G_RAW_UTILIZATION [1] " + str(c_util))
      xm.SendExpectOK(port + " P4G_TCP_WINDOW_SIZE [1] " + str(c_tcp_wnd))
      xm.SendExpectOK(port + " P4G_TCP_MSS_VALUE [1] "   + str(c_tcp_mss))

   rxports = nports/2
   txports = nports/2


   xm.PortAddLoadProfile(ports, 1, LOADPROFILE, "msecs")

   xm.PortPrepare(ports)
   xm.PortSetTraffic(svrs, "on")
   xm.PortWaitState(svrs, "RUNNING")
   xm.PortSetTraffic(clis, "on")
   xm.PortWaitState(clis, "RUNNING")

   waitsec = 2 + int(duration)/1000
   t0_milli = int(round(time.time() * 1000))
   rxbyte = 0
   txbyte = 0
   rxbps_max=0
   txbps_max=0
   while waitsec != 0:
      print "Waitsec: %d" % (waitsec)
      oldrx = rxbyte
      oldtx = txbyte
      rxbyte = 0
      txbyte = 0
      rxbps = 0
      txbps = 0
      for p in ports_rx:
         rx = xm.Send(p + " P4_RX_ETH_COUNTERS ?").split()
         rxbyte = rxbyte + int(rx[6])
         rxbps  = rxbps  + int(rx[4])
      for p in ports_tx:
         tx = xm.Send(p + " P4_TX_ETH_COUNTERS ?").split()
         txbyte = txbyte + int(tx[6])
         txbps  = txbps  + int(tx[4])

      rxbps = rxbps/rxports  
      if rxbps > rxbps_max:
         rxbps_max = rxbps

      txbps = txbps/txports 
      if txbps > txbps_max:
         txbps_max = txbps

      print "Total Rx Bytes: %d [%8.2f GB] (%5.2f Gbps)" % (rxbyte, rxbyte/1000000000.0, rxbps/1000000000.0)
      print "Total Tx Bytes: %d [%8.2f GB] (%5.2f Gbps)" % (txbyte, txbyte/1000000000.0, txbps/1000000000.0)
      time.sleep(1)
      waitsec-=1

   print "Stopping traffic..."
   for p in ports:
      xm.SendExpectOK(port + " P4_TRAFFIC stop")

   print "==STATS==================================================="
   est_conn=0
   for p in ports:
      res = xm.Send(p + " P4G_TCP_STATE_TOTAL [1] ?")
      est_conn = est_conn + int(res.split()[9])

   # Be careful when changing text, as output is parsed by other scripts
   print "Requested %d connection, established %d" % ((rxports)*c_conns, est_conn/2)

   getrtxstat(xm, ports)

   xm.PortStateOff(ports)
   # Be careful when changing text, as output is parsed by other scripts
   print "Max average Rx rate %d (%5.2f Gbps)" % (rxbps_max, rxbps_max/1000000000.0)
   print "Max average Tx rate %d (%5.2f Gbps)" % (txbps_max, txbps_max/1000000000.0)
   print "==DONE===================================================="
   return 0

if __name__ == '__main__':
    sys.exit(main())
