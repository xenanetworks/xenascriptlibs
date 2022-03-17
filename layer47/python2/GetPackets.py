#!/usr/bin/python

import os
import sys 
import time

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from TestUtilsL47 import XenaScriptTools
    
def main(argv):

   if len(argv) != 4:
      sys.stderr.write("Usage: %s IPaddr port nb_pkts\n" % (argv[0]))
      return 1

   ip_address = argv[1]
   port = argv[2] 
   n =  int(argv[3])

   xm    = XenaScriptTools(ip_address)
   #xm.debugOn()
   xm.haltOn()

   xm.LogonSetOwner("xena", "s_pkts")

   xm.PortGetPackets(port, n) 


if __name__ == '__main__':
    sys.exit(main(sys.argv))
