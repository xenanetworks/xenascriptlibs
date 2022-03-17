#!/usr/bin/python

import os, sys, time, getopt

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from TestUtilsL47 import XenaScriptTools


def helptext():
   print "Display various port information for a chassis"
   print
   print "Usage: %s [options] IPaddr [portlist]" % (sys.argv[0])
   print
   print "Options"
   print " -d   display debug information"
   print " -r   show port reservations"
   sys.exit(1)


def printReservations(xm, portlist):
   print
   print "-------------------------------------------------------------------------------------"
   print "Port State          Reservation         Reservedby                                         "
   print "-------------------------------------------------------------------------------------"
   for port in portlist:
       state = xm.Send(port + " P4_STATE ?").split()[2]
       resv  = xm.Send(port + " P_RESERVATION ?").split()[2]
       resby=""
       if resv.find("RESERVED_BY_OTHER") != -1:
         resby = xm.Send(port + " P_RESERVEDBY ?").split()[2]
       print "%-5s%-15s%-20s%-12s" % (port, state, resv, resby)


def printPortStates(xm, portlist):
   print
   print "-------------------------------------------------------------------------------------"
   print "Port State        Speed     Interface            Speedsel    PE Alloc  AUT 1G 10G 40G"
   print "-------------------------------------------------------------------------------------"
   for port in portlist:
       state = xm.Send(port + " P4_STATE ?").split()[2]
       speed = xm.Send(port + " P_SPEED ?").split()[2]
       ifnam = " ".join(xm.Send(port + " P_INTERFACE ?").split()[2:])
       selec = xm.Send(port + " P4_SPEEDSELECTION ?").split()[2]
       alloc = xm.Send(port + " P4E_ALLOCATE ?").split()[2]
       phycaps = xm.Send(port + " P4_CAPABILITIES ?").split()
       cap_aut = int(phycaps[2]) != 0
       cap_1g  = int(phycaps[3]) != 0
       cap_10g = int(phycaps[4]) != 0
       cap_40g = int(phycaps[5]) != 0
       print "%-5s%-11s%8s   %-22s%-10s  %-9s %-4d %d   %d   %d" % (port, state, speed, ifnam, selec, alloc, cap_aut, cap_1g, cap_10g, cap_40g)
   print
    
def main(argv):
   c_debug = 0
   c_res = 0

   try:
      opts, args = getopt.getopt(sys.argv[1:], "dhr")
   except getopt.GetoptError:
      helptext()
      return

   for opt, arg in opts:
      if opt == '-h':
         helptext()
         return
      elif opt in ("-d"):
         c_debug = 1
      elif opt in ("-r"):
         c_res = 1

   arglen = len(args)
   if arglen < 1 or (arglen > 1 and (arglen-1)%2 != 0):
      helptext()

   ip_address = args[0]
   if arglen > 1:
      portlist = args[1:]
   else:
      portlist = []

   xm    = XenaScriptTools(ip_address)

   if c_debug:
      xm.debugOn()
   xm.haltOn()

   xm.Logon("xena")

   if arglen == 1:
      modules = xm.Send("c_remoteportcounts ?").split()

      for i in range(len(modules)-1):
         ports = int(modules[i+1])
         if ports != 0:
            for port in range(ports):
               portlist.append( str(i) + "/" + str(port))

   if c_res:
      printReservations(xm, portlist)
   else:
      printPortStates(xm, portlist)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
