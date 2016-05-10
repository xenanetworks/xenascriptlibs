#!/usr/bin/env python

"""" Xena stream cap rate calculator and handler """
import os
import sys
import argparse

from testutils.TestUtilsL23 import XenaScriptTools

class CapRateHandler(object):
    def __init__(self):
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

        parser.add_argument('-c', '--caprate', type=float, action='store', required=True,
                            default=1000, help='The cap rate in Mbit/s to use')

        parser.add_argument('-s', '--streamdef', type=str, action='store', required=True,
                            default=None, help='Path to Python file containing stream rate definitions')

        return parser

    def check_arguments(self):
        if not os.path.exists(self.arguments.streamdef):
            self.reportErrorAndExit("File '%s' not found" % self.arguments.streamdef)

        if self.arguments.caprate <= 0.0:
            self.reportErrorAndExit("Cap rate must be larger than zero")

    def get_portmap(self, streamdeflist):
        portmap = {}
        for sdef in streamdeflist:
            portid = "%d/%d" % (sdef["module"], sdef["port"])
            if not portmap.has_key(portid):
                portmap[portid] = {}

                speed = self.xm.Send(portid + " P_SPEED ?").split()[2]
                portmap[portid]["speed"] = float(speed)
                portmap[portid]["streams"] = []

            portmap[portid]["streams"].append(sdef)

        return portmap

    def run(self):
        print("Settings stream rate from %s using caprate %.01f Mbit/s" % (self.arguments.streamdef, self.arguments.caprate))

        parts = os.path.splitext(self.arguments.streamdef)
        defs = __import__(parts[0])

        self.xm = XenaScriptTools(self.arguments.address)
        self.xm.LogonSetOwner("xena", "pyrate")

        self.portmap = self.get_portmap(defs.streams)

        self.xm.PortReserve(self.portmap.keys())

        self.calc_and_set_rates()

        self.xm.PortRelease(self.portmap.keys())

        print("Done!")

    def calc_and_set_rates(self):
        for portid in self.portmap:
            portspeed = self.portmap[portid]["speed"]
            sdeflist = self.portmap[portid]["streams"]
            for sdef in sdeflist:
                realratep = sdef["ratep"] * self.arguments.caprate / portspeed
                self.xm.Send("%s PS_RATEFRACTION [%d] %d" % (portid, sdef["sid"], int(realratep * 10000)))


if __name__ == '__main__':
    handler = CapRateHandler()
    handler.run()
