#!/usr/bin/python

import os, sys, time, getopt, re, datetime

lib_path = os.path.abspath('testutils')
sys.path.append(lib_path)

from TestUtilsL47 import XenaScriptTools

def helptext():
   print 
   print "Usage: %s ipaddr\n" % (sys.argv[0])
   print
   print "  prints various version and serial numbers."
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

   if len(args) != 1:
      helptext()

   ip_address = args[0]

   xm    = XenaScriptTools(ip_address)

   if c_debug:
      xm.debugOn()
   xm.haltOn()

   xm.Logon("xena")

   # start with CHASSIS   
   s_serial    = xm.Send("C_SERIALNO ?").split()[1]
   versionno   = xm.Send("C_VERSIONNO ?").split()
   s_version1  = versionno[1]
   s_version2  = versionno[2]
   r_model     = re.search( '.*"(.*)"' , xm.Send("C_MODEL ?") )
   s_model     = r_model.group(1)

   # proceed to MODULE
   r_m_status = re.search( '.*"(.*)"', xm.Send(" 1 M4_SYSTEM_STATUS ?") )
   s_m_status = r_m_status.group(1)

   # if module is ok
   if (s_m_status == "OK"):
      s_m_serial  = xm.Send("1 M_SERIALNO ?").split()[2]
      s_m_version = xm.Send("1 M_VERSIONNO ?").split()[2]

      r_m_version = re.search( '.*"(.*) (.*)"', xm.Send("1 M4_VERSIONNO ?") )
      s_m_verstr = r_m_version.group(1)
      s_m_build  = r_m_version.group(2)

      s_m_sysid  = xm.Send(" 1 M4_SYSTEMID ?").split()[2]

   print
   print "Date:                   %s" % (datetime.datetime.today())
   print "Chassis ip address:     %s" % (ip_address)
   print "Chassis model:          %s" % (s_model)
   print "Chassis serial number:  %s (0x%08x)" % (s_serial, int(s_serial))
   if (int(s_serial) >> 24) == 0 or (int(s_serial) >> 24) >= 127:
      print "WARNING"
      print "Serial number indicates new MAC OUI on motherboard"
      print " or misconfiguration as L2-3 chassis"
      print "WARNING"
      return 1

   print "Chassis server version: %s" % (s_version1)
   print "Chassis driver version: %s" % (s_version2)
   if (s_m_status != "OK"):
      print "WARNING"
      print "Module status: %s" % (s_m_status)
      print "WARNING"
      print
      return 1
   print "Module serial number:   %s (0x%08x)" % (s_m_serial, int(s_m_serial))
   print "Module version number:  %s" % (s_m_version)
   print "Module version string:  %s" % (s_m_verstr)
   print "Module status:          %s" % (s_m_status)
   print "Module system id:       %s" % (s_m_sysid)
   print "Module build id:        %s" % (s_m_build)
   print

   return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
