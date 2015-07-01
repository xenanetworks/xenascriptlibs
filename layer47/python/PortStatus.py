#!/usr/bin/python

import os, sys, time, getopt

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from TestUtilsL47 import XenaScriptTools

def helptext():
   print "Usage: %s IPaddr\n" % (sys.argv[0])
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

   if len(args) != 1:
      helptext()

   ip_address = args[0]

   portlist = []

   xm    = XenaScriptTools(ip_address)
   if c_debug:
      xm.debugOn()
   xm.haltOn()

   xm.Logon("xena")
     
   # Now for Module
   modules = xm.Send("c_remoteportcounts ?").split()
   
   for i in range(len(modules)-1):
      ports = int(modules[i+1])
      if ports != 0:
         for port in range(ports):
            portlist.append( str(i) + "/" + str(port))

   print
   print "----------------------------------------------------------------------------------"
   print "Port State     Speed     Interface            Speedsel    PE Alloc  AUT 1G 10G 40G"
   print "----------------------------------------------------------------------------------"
   for port in portlist:
       state = xm.Send(port + " P4_STATE ?").split()[2] 
       speed = xm.Send(port + " P_SPEED ?").split()[2]
       ifnam = " ".join(xm.Send(port + " P_INTERFACE ?").split()[2:])
       selec = xm.Send(port + " P_SPEEDSELECTION ?").split()[2]
       alloc = xm.Send(port + " P4E_ALLOCATE ?").split()[2]
       phycaps = xm.Send(port + " P4_CAPABILITIES ?").split()
       cap_aut = int(phycaps[2]) != 0
       cap_1g  = int(phycaps[3]) != 0
       cap_10g = int(phycaps[4]) != 0
       cap_40g = int(phycaps[5]) != 0
       print "%-5s%-8s%8s   %-22s%-10s  %-9s %-4d %d   %d   %d" % (port, state, speed, ifnam, selec, alloc, cap_aut, cap_1g, cap_10g, cap_40g)
   print
   


if __name__ == '__main__':
    sys.exit(main(sys.argv))
