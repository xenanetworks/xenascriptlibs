#!/usr/bin/python

import os, sys, time, getopt

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from TestUtilsL47 import XenaScriptTools
from TestUtilsL47 import LoadProfile

def helptext():
   print 
   print "Usage: %s [options] ipaddr" % (sys.argv[0])
   print 
   print "Setup one IPv6 connection"
   print "Options"
   print "  -n conns  set number of connections to conns"
   print "  -t class  set traffic class (8 bit)"
   print "  -f flow   set flow label (20 bit)"
   print "  -c        enable packet capture"
   print "  -e pes    assigned PEs per port"
   print
   sys.exit(1)
    
def main(argv):
   c_debug = 0
   c_owner = "s_ip64"
   c_conns = "1"
   c_cap = 0
   c_tc = "0x00"
   c_fl = "0x00000000" 
   c_pe = 2

   try:
      opts, args = getopt.getopt(sys.argv[1:], "dhcn:f:t:e:")
   except getopt.GetoptError:
      helptext()
      return

   for opt, arg in opts:
      if opt == '-h':
         helptext()
         return
      elif opt in ("-d"):
         c_debug=1
      elif opt in ("-c"):
         c_cap=1
      elif opt in ("-4"):
         c_v4=1
      elif opt in ("-n"):
         c_conns = arg
      elif opt in ("-f"):
         c_fl = arg
      elif opt in ("-e"):
         c_pe = int(arg)
      elif opt in ("-t"):
         c_tc = arg


   if len(args) != 1:
      helptext()

   ip_address = args[0]

   xm    = XenaScriptTools(ip_address)

   if c_debug:
      xm.debugOn()
   xm.haltOn()

   server = "1/0"
   client = "1/1"
   ports = [server, client]

   lp = LoadProfile(0, 2000, 2000, 2000, "msecs")

   xm.LogonSetOwner("xena", c_owner)
   xm.PortReserve(ports)
   xm.PortReset(ports)

   for port in ports:
     xm.SendExpectOK(port + " P4E_ALLOCATE " + str(c_pe))
     xm.SendExpectOK(port + " P4G_CREATE [0]")
     xm.SendExpectOK(port + " P4G_TEST_APPLICATION [0] RAW")
     xm.SendExpectOK(port + " P4G_RAW_TEST_SCENARIO [0] DOWNLOAD")
     xm.SendExpectOK(port + " P4G_RAW_PAYLOAD_TOTAL_LEN [0] INFINITE 1")
     if c_cap:
       xm.SendExpectOK(port + "P4_CAPTURE ON")

     xm.SendExpectOK(port + " P4G_CLIENT_RANGE [0] 10.1.10.2 " + c_conns + " 40000 1 65535")
     xm.SendExpectOK(port + " P4G_SERVER_RANGE [0] 11.1.11.2 1 50000 1")

     xm.SendExpectOK(port + " P4G_CREATE [1]")
     xm.SendExpectOK(port + " P4G_TEST_APPLICATION [1] RAW")
     xm.SendExpectOK(port + " P4G_RAW_TEST_SCENARIO [1] DOWNLOAD")
     xm.SendExpectOK(port + " P4G_RAW_PAYLOAD_TOTAL_LEN [1] INFINITE 1")

     xm.SendExpectOK(port + " P4G_IP_VERSION [1] IPV6")
     xm.SendExpectOK(port + " P4G_IPV6_TRAFFIC_CLASS [1] " + c_tc)
     xm.SendExpectOK(port + " P4G_IPV6_FLOW_LABEL [1] "    + c_fl)
     xm.SendExpectOK(port + " P4G_IPV6_CLIENT_RANGE [1] 0xaa01aa02aa03aa04aa05aa06aa07aa08 " + c_conns + " 40000 1 65535")
     xm.SendExpectOK(port + " P4G_IPV6_SERVER_RANGE [1] 0xbb01bb02bb03bb04bb05bb06bb07bb08 1 50000 1")

   xm.SendExpectOK(server + " P4G_ROLE [0] server")
   xm.SendExpectOK(server + " P4G_ROLE [1] server")
   xm.PortAddLoadProfile(ports, 0, lp.shape(), lp.timescale)
   xm.PortAddLoadProfile(ports, 1, lp.shape(), lp.timescale)


   for port in ports:
      print xm.Send(port + " P4_STATE ?")

   xm.PortPrepare(ports)


   xm.PortSetTraffic(ports, "prerun")
   xm.PortWaitState(ports, "PRERUN_RDY")

   xm.PortSetTraffic(server, "on")
   xm.PortWaitState(server, "RUNNING")
   xm.PortSetTraffic(client, "on")
   xm.PortWaitState(client, "RUNNING")


   slp = lp.duration_sec() +1
   for i in range(slp):
      print "Sleep %d/%d" %(i, slp)
      time.sleep(1)

   for port in ports:
      res = xm.Send(port + " P4G_TCP_STATE_TOTAL [0] ?")
      est_conn = int(res.split()[9])
      print "Port: %s, group [0] conns: %d" % (port, est_conn)
      res = xm.Send(port + " P4G_TCP_STATE_TOTAL [1] ?")
      est_conn = int(res.split()[9])
      print "Port: %s, group [1] conns: %d" % (port, est_conn)

   xm.PrintPortStatistics(ports)

   xm.PortSetTraffic(ports, "stop")
   xm.PortWaitState(ports, "STOPPED")
   for port in ports:
      if c_cap:
         xm.SendExpectOK(port + " P4_CAPTURE OFF")

   #xm.PortRelease(ports)
   print "DONE"
   

if __name__ == '__main__':
    sys.exit(main(sys.argv))
