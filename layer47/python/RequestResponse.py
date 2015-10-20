#!/usr/bin/python

import os, sys, time, getopt

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from TestUtilsL47 import XenaScriptTools
from TestUtilsL47 import LoadProfile

svrs = []
clis = []
ports= []

def helptext():
   print "Usage: RequestResponse.py [options] ipaddress p1 p2 [p3 p4]+"
   print
   print "Options"
   print "-d         debug"
   print "-r repcnt  number of repeats"
   print "-e pkteng  number of packet engines" 
   print "-n conns   number of connections"
   print "-s size    length of payload"
   sys.exit(1)

    
def main():
   c_debug  = 0
   c_pe     = 2
   c_repeat = 0 
   c_conn   = 1000
   c_len    = 1460

   try:
      opts, args = getopt.getopt(sys.argv[1:], "hde:r:n:s:")
   except getopt.GetoptError:
      helptext()

   for opt, arg in opts:
       if opt == '-h':
          helptext()
       elif opt in ("-d"):
          c_debug = 1
       elif opt in ("-e"):
          c_pe = int(arg)
       elif opt in ("-r"):
          c_repeat = int(arg)
       elif opt in ("-n"):
          c_conn= int(arg)
       elif opt in ("-s"):
          c_len= int(arg)

   arglen = len(args) 
   if arglen < 3 or (arglen-1)%2 != 0:
      helptext()

   ip_address = args[0]

   # Build list of server and client ports
   for i in range(arglen-1):
      if i%2 == 0:
         svrs.append(args[i+1])
      else:
         clis.append(args[i+1])

   ports = svrs + clis

   xm    = XenaScriptTools(ip_address)
   if c_debug:
      xm.debugOn()
   xm.haltOn()

   lp = LoadProfile(0, 1000, 8000, 1000, "msecs")

   s_repeat = str(c_repeat)
   if c_repeat == 0:
      s_repeat = "INFINITE"

   print
   print "==CONFIGURATION==========================================="
   print "CFG connections : %d" % (c_conn)
   print "CFG server ports: " + " ".join(svrs)
   print "CFG client ports: " + " ".join(clis)
   print "CFG repeats     : %s" % (s_repeat)
   print "CFG payload size: %d" % (c_len)
   print "CFG duration    : %ds" % (lp.duration_sec())
   print "CFG pkteng      : %d" % (c_pe)
   print "CFG debug       : %d" % (c_debug)
   print

   print "==TEST EXECUTION=========================================="

   xm.Comment("Logon, reserve and reset ports")
   xm.LogonSetOwner("xena", "s_reqres")
 
   xm.PortReserve(ports)
   xm.PortReset(ports)

   xm.Comment("Configure %d clients - total %d CC" % (c_conn, c_conn))
   xm.PortAddConnGroup(ports, 1, "10.0.1.1 " + str(c_conn) + " 40001 1", "11.0.1.1 1 80 1", 4)
   xm.PortRole(svrs, 1, "server")
   xm.PortRole(clis, 1, "client")
   xm.PortAddLoadProfile(ports, 1, lp.shape(), lp.timescale)

   xm.Comment("Configure application")
   for port in ports:
      xm.SendExpectOK(port + " P4E_ALLOCATE " + str(c_pe))
      xm.SendExpectOK(port + " P4G_TEST_APPLICATION [1] raw")
      xm.SendExpectOK(port + " P4G_RAW_TEST_SCENARIO [1] download")
      xm.SendExpectOK(port + " P4G_RAW_HAS_DOWNLOAD_REQ [1] yes")
      xm.SendExpectOK(port + " P4G_RAW_CLOSE_CONN [1] no")
      xm.SendExpectOK(port + " P4G_RAW_TX_DURING_RAMP [1] no no")
      xm.SendExpectOK(port + " P4G_RAW_TX_TIME_OFFSET [1] 100 100")
      if c_repeat:
         xm.SendExpectOK(port + " P4G_RAW_REQUEST_REPEAT [1] FINITE " + str(c_repeat))
      else:
         xm.SendExpectOK(port + " P4G_RAW_REQUEST_REPEAT [1] INFINITE 1")
      xm.SendExpectOK(port + " P4G_RAW_PAYLOAD_TYPE [1] fixed")
      xm.SendExpectOK(port + " P4G_RAW_PAYLOAD_TOTAL_LEN [1] FINITE " + str(c_len))
      xm.SendExpectOK(port + " P4G_RAW_PAYLOAD_REPEAT_LEN [1] 1")

   xm.Comment("Configure Request")
   for port in ports:
      #xm.SendExpectOK(port + " p4g_raw_download_request [1] 86 0x474554202F706174682F66696C652E68746D6C20485454502F312E300D0A46726F6D3A20736F6D6575736572406A6D61727368616C6C2E636F6D0D0A557365722D4167656E743A2048545450546F6F6C2F312E300D0A")
      xm.SendExpectOK(port + " p4g_raw_download_request [1] 1 0xCC")

   xm.Comment("Configure Response")
   for port in svrs:
      xm.SendExpectOK(port + " P4G_RAW_PAYLOAD [1] 0 1 0xAA")
      if c_len > 1:
         xm.SendExpectOK(port + " P4G_RAW_PAYLOAD [1] " + str(c_len -1) + " 1 0xBB")

   for port in clis:
      xm.SendExpectOK(port + " P4G_RAW_RX_PAYLOAD_LEN [1] FINITE " + str(c_len))

   xm.Comment("Setup utilization and prepare for testrun")
   for port in clis:
      xm.SendExpectOK(port + " P4G_RAW_UTILIZATION [1] 999900")
   for port in svrs:
      xm.SendExpectOK(port + " P4G_RAW_UTILIZATION [1] 999900")

   xm.Comment("Prepare ports and run tests, start with servers")
   xm.PortPrepare(ports)

   xm.PortSetTraffic(ports, "prerun")
   xm.PortWaitState(ports, "PRERUN_RDY")

   xm.PortSetTraffic(svrs, "ON")
   xm.PortWaitState(svrs, "RUNNING")
   xm.PortSetTraffic(clis, "ON")

   waitsec = lp.duration_sec() + 2
   while waitsec != 0:
      acc = 0
      rate = 0
      for port in clis:
         trans = xm.Send(port + " p4g_app_transaction_counters [1] ?").split()
         acc  = int(trans[5])
         rate = int(trans[6])
         print "Port %s: Transactions: %12u, Rate: %12u " % (port, acc, rate)

      time.sleep(1)
      waitsec-=1

   for port in ports:
      xm.Send(port + " P4_TRAFFIC stop")

   #xm.PortRelease(ports)
   print "==DONE==================================================="


   return 0

if __name__ == '__main__':
   sys.exit(main())
