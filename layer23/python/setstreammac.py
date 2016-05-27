#!/usr/bin/env python

""" This script demonstrates how to set the fields in a protocol header """

import sys
import argparse

from testutils.TestUtilsL23 import XenaScriptTools


class MacSetter(object):
    def __init__(self):
        self.module_index = None
        self.port_index = None

        self.parser = self.build_parser()
        self.arguments = self.parser.parse_args()
        self.check_arguments()

    def exitScript(self, errcode):
        sys.exit(errcode)

    def reportErrorAndExit(self, errmess, printUsage=True):
        print ""
        print "Error: %s" % errmess
        print ""

        if printUsage:
            self.parser.print_usage()

        self.exitScript(1)

    def build_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-a', '--address', type=str, action='store', required=True,
                            default=None, help='IP address of test chassis')
        parser.add_argument('-p', '--portid', type=str, action='store', required=True,
                            default=None, help='ID of port to use')
        return parser

    def check_arguments(self):
        portparts = self.arguments.portid.split("/")
        if len(portparts) != 2:
            self.reportErrorAndExit("Invalid port ID format - must be <module>/<port>")

        try:
            self.module_index = int(portparts[0])
            self.port_index = int(portparts[1])

        except ValueError, ex:
            self.reportErrorAndExit("Invalid port ID format - must be <module>/<port>")

        except Exception, ex:
            self.reportErrorAndExit(ex.message)

    def run(self):
        portid = self.arguments.portid

        print("Creating streams on %s - port %s with custom SMAC and DMAC" % (self.arguments.address, portid))

        # logon to chassis
        self.xm = XenaScriptTools(self.arguments.address)
        self.xm.LogonSetOwner("xena", "mactest")

        # reserve port
        self.xm.PortReserve(portid)

        # reset port and create one stream
        self.xm.SendExpectOK(portid + " P_RESET")
        self.xm.SendExpectOK(portid + " PS_CREATE [0]")
        self.xm.SendExpectOK(portid + " PS_TPLDID [0] 0")
        self.xm.SendExpectOK(portid + " PS_RATEFRACTION [0] 200000")
        self.xm.SendExpectOK(portid + " PS_ENABLE [0] ON")

        # setup data for Ethernet header
        smac = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06]
        dmac = [0x11, 0x12, 0x13, 0x14, 0x15, 0x16]
        ethertype = [0xff, 0xff]

        # format Ethernet header data as a hex string
        headerdata = ''.join('{:02x}'.format(x) for x in dmac + smac + ethertype)

        # send header data for stream
        self.xm.SendExpectOK(portid + " PS_PACKETHEADER [0] 0x" + headerdata)
        self.xm.SendExpectOK(portid + " PS_HEADERPROTOCOL [0] ETHERNET")

        # release port
        self.xm.PortRelease(portid)

if __name__ == '__main__':
    handler = MacSetter()
    handler.run()
