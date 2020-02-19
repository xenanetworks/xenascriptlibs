#!/usr/bin/env python

"""" Xena stream cap rate calculator and handler

This Python 2 script will assist you in setting the rates of a number of
streams to match a given cap rate. Each stream rate is expressed a priori
as a percentage. The script will then calculate the resulting stream rate
given a certain cap rate, where the cap rate is <= the port physical rate.

All streams must be defined on the test chassis before the script is called.

Usage: <python.exe path> streamcaprates.py -a ADDRESS -c CAPRATE -s STREAMDEF

where:
    ADDRESS :   The IP address of your Xena tester
    CAPRATE :   The desired cap rate for the ports in Mbit/s.
    STREAMDEF : Path to a python file containing stream definitions

The format of the STREAMDEF file is as follows:

streams = [
    {
        "module" : 7,
        "port" : 0,
        "sid" : 0,
        "ratep" : 5.5
    },
    {
        "module" : 7,
        "port" : 0,
        "sid": 1,
        "ratep": 14.5
    },

    # Add more stream definitions here
]

The 'streams' element is a list of information for all defined streams that you want to control.
Each information element contains the following items:

    module  :   The module index
    port    :   The port index
    sid     :   The zero-based stream ID
    ratep   :   The desired rate of this stream in percent of the port rate.

"""

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


    def calc_and_set_rates(self):
        for portid in self.portmap:
            portspeed = self.portmap[portid]["speed"]
            sdeflist = self.portmap[portid]["streams"]
            for sdef in sdeflist:
                realratep = sdef["ratep"] * self.arguments.caprate / portspeed
                print "Setting rate for stream %s [%d] to %.01f %%" % (portid, sdef["sid"], realratep)
                self.xm.Send("%s PS_RATEFRACTION [%d] %d" % (portid, sdef["sid"], int(realratep * 10000)))


if __name__ == '__main__':
    handler = CapRateHandler()
    handler.run()
