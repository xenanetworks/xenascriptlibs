#!/usr/bin/python

import os, sys, time, getopt

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from testutils.TestUtilsL23 import XenaScriptTools


def helptext():
   print "Usage: %s [options] IPaddr [portlist]\n" % (sys.argv[0])
   sys.exit(1)

def PortListAll(xm,):
   modules = xm.Send("c_portcounts ?").split()
   for i in range(len(modules)-1):
      print "Module %d" % (i)
      ports = int(modules[i+1])
      if ports != 0:
         for port in range(ports):
            ps    = str(i) + "/" + str(port)
            intfc = " ".join(xm.Send(ps + " P_INTERFACE ?").split()[2:])
            if intfc != "":
               speed = xm.Send(ps + " P_SPEED ?").split()[2]
               print "Port: %d, %s, %s" % (port, intfc, speed)

def PortList(xm,portlist):
   for port in portlist:
      intfc = " ".join(xm.Send(port + " P_INTERFACE ?").split()[2:])
      if intfc != "":
         speed = xm.Send(port + " P_SPEED ?").split()[2]
         print "Port: %s, %s, %s" % (port, intfc, speed)


    
def main(argv):
   c_debug = 0

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
         c_debug = 1

   if len(args) < 1:
      helptext()

   ip_address = args[0]
   

   xm    = XenaScriptTools(ip_address)

   if c_debug:
      xm.debugOn()
   xm.haltOn()

   xm.Logon("xena")

   if len(args) > 1:
      PortList(xm, args[1:])
   else:
      PortListAll(xm)
      

   



if __name__ == '__main__':
    sys.exit(main(sys.argv))
