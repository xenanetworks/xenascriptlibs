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
   print " -f filltype  payload fill type: FIXED, INCREMENT, RANDOM, LONGRANDOM"
   print " -l profile   specify load profile in ms. Ex. '0 1000 2000 1000'"
   print " -p --proxy   enable proxy (default is 0)"
   print " -a           use arp for address resolution"
   print " -t           tx during ramp up/down"
   print " -e N         allocate N PE's per port (default is 1)"
   print " -n conns     specify the number of requested connections"
   print " -u util      specify payload utilization in ppm (100% == 1000000)"
   print " -w N         sets the TCP window"
   print " -v tci       enable VLAN with tcp specified as hex (example -v 0x1234)"
   print " -m MSS       sets the MSS value - default is 1460"
   print " -6           Use IPv6 instead of IPv4"
   print " -c N         Enable packet capture, display N packets"
   print " --pkteng=N   same as -e"
   print " -d           enable debug (default is 0)"
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
      res = xm.Send(p + " P4G_TCP_RETRANSMIT_COUNTERS [0] ?").split()
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
   c_nat = 0
   c_pe    = 1
   c_lp    = "0 5000 5000 5000"
   c_conns = 1000000
   c_util  = 1000000
   c_tcp_wnd  = 65535
   c_tcp_mss  = 1460
   c_scenario = "BOTH"
   c_ipver = 4
   c_cap = 0
   c_tx_ramp = 0
   c_fill = "FIXED"
   c_vlan = 0
   c_vlan_tci = 0
   c_arp = 0

   try:
      opts, args = getopt.getopt(sys.argv[1:], "6hac:dptv:f:e:l:n:u:w:s:m:", ["nat", "pkteng=", "loadprofile=", "scenario=", "mss="])
   except getopt.GetoptError:
      helptext()
      return

   for opt, arg in opts:
       if opt == '-h':
          helptext()
          return
       elif opt in ("-b", "--nat"):
          c_nat=1
       elif opt in ("-d"):
          c_debug=1
       elif opt in ("-a"):
          c_arp=1
       elif opt in ("-c"):
          c_cap= int(arg)
       elif opt in ("-e", "--pkteng"):
          c_pe = int(arg)
       elif opt in ("-l", "--loadprofile"):
          c_lp = arg
       elif opt in ("-s", "--scenario"):
          c_scenario = arg 
       elif opt in ("-m", "--mss"):
          c_tcp_mss = int(arg)
       elif opt in ("-f"):
          c_fill = arg
       elif opt in ("-v"):
          c_vlan = 1
          c_vlan_tci = arg
       elif opt in ("-u"):
          c_util=int(arg)
       elif opt in ("-6"):
          c_ipver = 6
       elif opt in ("-t"):
          c_tx_ramp = 1
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

   MSSWARN=""
   if c_ipver == 6 and c_tcp_mss > 1440:
      MSSWARN = " <<< WARNING - MSS too large for IPv6 >>>"
   elif c_ipver == 4 and c_tcp_mss > 1460:
      MSSWARN = "<<< WARNING - MSS too large for IPv4 >>>"

   print
   print "==CONFIGURATION==========================================="
   print "CFG load profile: %s (duration %d)" % (c_lp, duration)
   print "CFG connections : %d" % (c_conns)
   print "CFG server ports: " + " ".join(svrs)
   print "CFG client ports: " + " ".join(clis)
   print "CFG IPversion   : %d" % (c_ipver)
   print "CFG Payload     : %s" % (c_fill)
   print "CFG Arp         : %d" % (c_arp)
   if c_vlan:
      print "CFG VLAN        : %s" % (c_vlan_tci)
   print "CFG NAT       : %d" % (c_nat)
   print "CFG TCP window  : %d" % (c_tcp_wnd)
   print "CFG TCP MSS     : %s %s" % (c_tcp_mss, MSSWARN)
   print "CFG scenario    : %s" % (c_scenario)
   print "CFG utilization : %d" % (c_util)
   print "CFG pkteng      : %d" % (c_pe)
   if c_cap:
      print "CFG capture     : %d" % (c_cap)
   print "CFG debug       : %d" % (c_debug)

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

   if c_ipver == 6:
      CLIENT_RANGE = "0xaa01aa02aa03aa04aa05aa06aa07aa08 " + str(c_conns) +" 40000 1 65535"
      SERVER_RANGE = "0xbb01bb02bb03bb04bb05bb06bb07bb08 1 50000 1"
   else:
      CLIENT_RANGE = "10.0.0.2 " + str(c_conns) +" 40000 1 65535"
      SERVER_RANGE = "10.0.0.1 1 50000 1"

   xm.PortAddConnGroup(ports, 1, CLIENT_RANGE, SERVER_RANGE, c_ipver)
   xm.PortRole(clis, 0, "client")
   xm.PortRole(svrs, 0, "server")

   if c_nat:
      for port in svrs:
         xm.SendExpectOK(port + " P4G_NAT [0] on")

   for port in ports:
      xm.SendExpectOK(port + " P4_CLEAR_COUNTERS")
   nports=0
   for port in ports:
      nports = nports + 1
      xm.SendExpectOK(port + " P4E_ALLOCATE " + str(c_pe))
      xm.SendExpectOK(port + " P4G_LP_TIME_SCALE [0] msec")
      xm.SendExpectOK(port + " P4G_TEST_APPLICATION [0] RAW")
      xm.SendExpectOK(port + " P4G_RAW_TEST_SCENARIO [0] " + c_scenario)
      xm.SendExpectOK(port + " P4G_RAW_PAYLOAD_TYPE [0] " + c_fill)
      xm.SendExpectOK(port + " P4G_RAW_HAS_DOWNLOAD_REQ [0] NO")
      xm.SendExpectOK(port + " P4G_RAW_CLOSE_CONN [0] NO")
      xm.SendExpectOK(port + " P4G_RAW_PAYLOAD_TOTAL_LEN [0] INFINITE 0")
      xm.SendExpectOK(port + " P4G_RAW_UTILIZATION [0] " + str(c_util))
      xm.SendExpectOK(port + " P4G_TCP_WINDOW_SIZE [0] " + str(c_tcp_wnd))
      xm.SendExpectOK(port + " P4G_TCP_MSS_VALUE [0] "   + str(c_tcp_mss))
      if c_cap:
         xm.SendExpectOK(port + " P4_CAPTURE ON")

      if c_tx_ramp:
         xm.SendExpectOK(port + " P4G_RAW_TX_DURING_RAMP [0] YES YES")

      if c_vlan:
         xm.SendExpectOK(port + " P4G_VLAN_ENABLE [0] YES")
         xm.SendExpectOK(port + " P4G_VLAN_TCI [0] " + c_vlan_tci)

      if c_arp:
         xm.SendExpectOK(port + " P4G_L2_USE_ARP [0] YES")

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
         rx = xm.Send(p + " P4_ETH_RX_COUNTERS ?").split()
         rxbyte = rxbyte + int(rx[6])
         rxbps  = rxbps  + int(rx[4])
      for p in ports_tx:
         tx = xm.Send(p + " P4_ETH_TX_COUNTERS ?").split()
         txbyte = txbyte + int(tx[6])
         txbps  = txbps  + int(tx[4])

      if rxbps > rxbps_max:
         rxbps_max = rxbps

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
      res = xm.Send(p + " P4G_TCP_STATE_TOTAL [0] ?")
      est_conn = est_conn + int(res.split()[9])

   # Be careful when changing text, as output is parsed by other scripts
   print "Requested %d connection, established %d" % ((rxports)*c_conns, est_conn/2)

   getrtxstat(xm, ports)

   xm.PortSetTraffic(ports, "stop")
   xm.PortWaitState(ports, "STOPPED")
   for port in ports:
      if c_cap:
         xm.PortGetPackets(port, c_cap)
         xm.SendExpectOK(port + " P4_CAPTURE OFF")

   xm.PortRelease(ports)

   # Be careful when changing text, as output is parsed by other scripts
   print "Max average Rx rate %d (%5.2f Gbps)" % (rxbps_max, rxbps_max/1000000000.0)
   print "Max average Tx rate %d (%5.2f Gbps)" % (txbps_max, txbps_max/1000000000.0)
   print "==DONE===================================================="


   return 0

if __name__ == '__main__':
    sys.exit(main())
