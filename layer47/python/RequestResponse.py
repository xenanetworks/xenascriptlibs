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
   print
   print "Usage: TDB"
   sys.exit(1)

    
def main():

   c_debug = 0
   c_pe = 2
   c_repeat = 5

   try:
      opts, args = getopt.getopt(sys.argv[1:], "hde:r:")
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

   lp = LoadProfile(0, 10, 150, 10, "sec")

   print
   print "==CONFIGURATION==========================================="
   print "CFG duration    : %ds" % (lp.duration_sec())
   print "CFG repeats     : %d" % (c_repeat)
   print "CFG pkteng      : %d" % (c_pe)
   print "CFG debug       : %d" % (c_debug)
   print "CFG server ports:" + " ".join(svrs) 
   print "CFG client ports:" + " ".join(clis) 




   print "==TEST EXECUTION=========================================="

   xm.Comment("Logon, reserve and reset ports")
   xm.LogonSetOwner("xena", "s_reqres")
 
   xm.PortReserve(ports)
   xm.PortReset(ports)

   xm.Comment("Configure 1M Clients and 20 Servers - total 20M CC")
   xm.PortAddConnGroup(ports, 1, "10.0.1.1 1000 40001 1000", "11.0.1.1 20 80 1")
   xm.PortRole(svrs, 1, "server")
   xm.PortRole(clis, 1, "client")
   xm.PortAddLoadProfile(ports, 1, lp.shape(), lp.timescale)

   xm.Comment("Configure application")
   for port in ports:
      xm.SendExpectOK(port + " P4E_ALLOCATE 10")
      xm.SendExpectOK(port + " P4G_TEST_APPLICATION [1] raw")
      xm.SendExpectOK(port + " P4G_RAW_TEST_SCENARIO [1] download")
      xm.SendExpectOK(port + " P4G_RAW_HAS_DOWNLOAD_REQ [1] yes")
      xm.SendExpectOK(port + " P4G_RAW_CLOSE_CONN [1] no")
      xm.SendExpectOK(port + " P4G_RAW_TX_DURING_RAMP [1] no no")
      xm.SendExpectOK(port + " P4G_RAW_TX_TIME_OFFSET [1] 100 100")
      xm.SendExpectOK(port + " P4G_RAW_REQUEST_REPEAT [1] FINITE " + str(c_repeat))

   xm.Comment("Configure Request")
   for port in ports:
      xm.SendExpectOK(port + " p4g_raw_download_request [1] 86 0x474554202F706174682F66696C652E68746D6C20485454502F312E300D0A46726F6D3A20736F6D6575736572406A6D61727368616C6C2E636F6D0D0A557365722D4167656E743A2048545450546F6F6C2F312E300D0A")

   xm.Comment("Configure Response")
   for port in svrs:
      xm.SendExpectOK(port + " P4G_RAW_PAYLOAD_TYPE [1] fixed")
      xm.SendExpectOK(port + " P4G_RAW_PAYLOAD_TOTAL_LEN [1] FINITE 1460")
      xm.SendExpectOK(port + " P4G_RAW_PAYLOAD [1]    0 50 0x0001020304050607080910111213141516171819202122232425262728293031323334353637383940414243444546474849")
      xm.SendExpectOK(port + " P4G_RAW_PAYLOAD [1] 1410 50 0x5051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899")

   for port in clis:
      xm.SendExpectOK(port + " P4G_RAW_RX_PAYLOAD_LEN [1] FINITE 1460")

   xm.Comment("Setup utilization and prepare for testrun")
   for port in clis:
      xm.SendExpectOK(port + " P4G_RAW_UTILIZATION [1] 180000")
   for port in svrs:
      xm.SendExpectOK(port + " P4G_RAW_UTILIZATION [1] 999900")

   
   xm.Comment("Prepare ports and run tests, start with servers")
   xm.PortPrepare(ports)

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

   print "==DONE==================================================="
   return 0

if __name__ == '__main__':
   sys.exit(main())
