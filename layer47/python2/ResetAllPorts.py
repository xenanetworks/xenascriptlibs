#!/usr/bin/python

import os, sys, time, getopt

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from TestUtilsL47 import XenaScriptTools


def helptext():
    print
    print "Usage: ./ResetAllPorts.py options IPaddr [ports]"
    print
    print "  resets specified ports - if no ports are specified, reset all"
    print
    sys.exit(1)


def main(argv):
   c_debug = 0
   c_all = 0
   portlist = []

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

   if len(args) < 1:
      helptext()

   ip_address = args[0]

   if len(args) == 1:
      c_all = 1
   else:
      portlist = args[1:]

   xm = XenaScriptTools(ip_address)
   if c_debug:
       xm.debugOn()
   xm.haltOn()

   xm.LogonSetOwner("xena", "s_reset")
     
   # Now for Module
   modules = xm.Send("c_remoteportcounts ?").split()

   if c_all:   
      for i in range(len(modules)-1):
         ports = int(modules[i+1])
         if ports != 0:
            for port in range(ports):
               portlist.append( str(i) + "/" + str(port))

   print "The following ports will be reset"
   print portlist

   xm.PortReserve(portlist)
   xm.PortReset(portlist)
   xm.PortRelease(portlist)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
