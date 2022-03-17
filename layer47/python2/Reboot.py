#!/usr/bin/python

import os, sys, time, getopt

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from TestUtilsL47 import XenaScriptTools

def helptext():
   print 
   print "Usage: %s ipaddr [halt]" % (sys.argv[0])
   print 
   print "Reboot or powerdown a chassis"
   print 
   sys.exit(1)

def main(argv):
   c_debug = 0
   c_what = "restart"

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

   if len(args) != 1 and len(args) != 2:
      helptext()

   ip_address = args[0]
   if len(args) == 2:
      c_what = "poweroff"

   xm = XenaScriptTools(ip_address)

   if c_debug:
      xm.debugOn()
   xm.haltOn()

   xm.LogonSetOwner("xena", "s_upload")

   xm.Send("C_RESERVATION relinquish")
   xm.Send("C_RESERVATION reserve")
      
   print "====================================="
   xm.SendExpectOK("C_DOWN  -1480937026 " + c_what)

   print "DONE"
   print "===================================="

   

if __name__ == '__main__':
      sys.exit(main(sys.argv))
