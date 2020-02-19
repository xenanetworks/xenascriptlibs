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
      opts, args = getopt.getopt(sys.argv[1:], "dhn")
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

   # Start with CHASSIS   
   s_serial    = xm.Send("C_SERIALNO ?").split()[1]
   versionno   = xm.Send("C_VERSIONNO ?").split()
   s_version1  = versionno[1]
   s_version2  = versionno[2]
   r_model     = re.search( '.*"(.*)"' , xm.Send("C_MODEL ?") )
   s_model     = r_model.group(1)

   # License stuff
   res = xm.Send("1 M4_LICENSE_INFO ?")
   s_lic_pes   = res.split()[2]
   s_lic_pes_inuse = res.split()[3]
   s_lic_port_type_1   = res.split()[4]
   s_lic_port_type_1_inuse   = res.split()[5]
   s_lic_port_type_2  = res.split()[6]
   s_lic_port_type_2_inuse  = res.split()[7]
   s_lic_port_type_3  = res.split()[8]
   s_lic_port_type_3_inuse  = res.split()[9]
   s_lic_port_type_4  = res.split()[10]
   s_lic_port_type_4_inuse  = res.split()[11]

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

   print "Chassis server version: %s" % (s_version1)
   print "Chassis driver version: %s" % (s_version2)

   print "Module serial number:   %s (0x%08x)" % (s_m_serial, int(s_m_serial))
   print "Module version number:  %s" % (s_m_version)
   print "Module version string:  %s" % (s_m_verstr)
   print "Module status:          %s" % (s_m_status)
   print "Module system id:       %s" % (s_m_sysid)

   print "Licensed PE's:                  %s (%s in use)" % (s_lic_pes, s_lic_pes_inuse)
   print "Licensed 1G/10G ports:          %s (%s in use)" % (s_lic_port_type_1, s_lic_port_type_1_inuse)
   print "Licensed 1G/2.5G/5G/10G ports:  %s (%s in use)" % (s_lic_port_type_2, s_lic_port_type_2_inuse)
   print "Licensed 1G/10G/25G ports:      %s (%s in use)" % (s_lic_port_type_3, s_lic_port_type_3_inuse)
   print "Licensed 40G ports:             %s (%s in use)" % (s_lic_port_type_4, s_lic_port_type_4_inuse)
   
   print "Module build id:        %s" % (s_m_build)
   print

   return 0

if __name__ == '__main__':
      sys.exit(main(sys.argv))
