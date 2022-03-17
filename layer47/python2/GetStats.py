#!/usr/bin/python

import os, sys, time, getopt

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from TestUtilsL47 import XenaScriptTools

def helptext():
   print 
   print "Usage: %s ipaddr port\n" % (sys.argv[0])
   print 
   sys.exit(1)
    
def main(argv):
   c_debug = 0

   try:
      opts, args = getopt.getopt(sys.argv[1:], "dh")
   except getopt.GetoptError:
      helptext()
      return

   for opt, arg in opts:
      if opt == '-h':
         helptext()
         return
      elif opt in ("-d"):
         c_debug=1

   if len(args) != 2:
      helptext()

   ip_address = args[0]
   port = args[1]

   xm    = XenaScriptTools(ip_address)

   if c_debug:
      xm.debugOn()
   xm.haltOn()

   xm.Logon("xena")

   cgs = xm.Send(port + " P4G_INDICES ?").split()[2:]
      
   print "\n==PACKET COUNTS====================="
   xm.PrintPortStatistics(port)
   prx = xm.Send(port + " P4_ETH_RX_COUNTERS ?")
   print prx
   ptx = xm.Send(port + " P4_ETH_TX_COUNTERS ?")
   print ptx
   print "\n==TCP GOODPUT======================="
   for cg in cgs:
      res = xm.Send(port + " P4G_TCP_TX_PAYLOAD_COUNTERS  [" + cg + "] ?")
      print res
      res = xm.Send(port + " P4G_TCP_RX_PAYLOAD_COUNTERS [" + cg + "] ?")
      print res
   print "\n==CONNECTION TIMES=================="
   for cg in cgs:
      res = xm.Send(port + " P4G_TCP_ESTABLISH_HIST [" + cg + "] ?")
      print res
      res = xm.Send(port + " P4G_TCP_CLOSE_HIST [" + cg + "] ?")
      print res
   print


if __name__ == '__main__':
    sys.exit(main(sys.argv))
