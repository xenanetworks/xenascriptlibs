#!/usr/bin/python

import os, sys, time, getopt

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from TestUtilsL47 import XenaScriptTools

def helptext():
   print 
   print "Usage: %s ipaddr new_ipaddr new_mask new_gateway " % (sys.argv[0])
   print 
   print "Change Chassis IP address and reboot."
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

   if len(args) != 4:
      helptext()

   ip_address = args[0]
   new_ip = args[1]
   new_mask = args[2]
   new_gateway = args[3]

   xm    = XenaScriptTools(ip_address)

   if c_debug:
      xm.debugOn()
   xm.haltOn()

   xm.LogonSetOwner("xena", "user")


   xm.Send("C_RESERVATION relinquish")
   xm.Send("C_RESERVATION reserve")

   c = xm.Send("C_IPADDRESS ?")
   
   print "Chassis IP address: %s" % (c)
   print "Changing to:        %s" % (new_ip)
   print "                    %s" % (new_mask)
   print "                    %s" % (new_gateway)

   xm.Send("C_IPADDRESS " + str(new_ip) + " " + str(new_mask) + " " + str(new_gateway) )

   c = xm.Send("C_IPADDRESS ?")
   print "Chassis IP address: %s" % (c)

   print "===================================="
   print "Rebooting chassis to effectuate new IP address"
   
   xm.SendExpectOK("C_DOWN  -1480937026 restart")
 
   print "DONE"
   print "===================================="

   

if __name__ == '__main__':
    sys.exit(main(sys.argv))
