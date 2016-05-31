import os
import sys
from optparse import OptionParser

import datetime

from testutils.TestUtilsL23 import XenaScriptTools


class ScriptLoaderApp(object):
    """
    Script loader application
    """

    def __init__(self):
        self.parser = self.buildParser()
        (self.options, args) = self.parser.parse_args()

        self.checkArguments()

    def exitScript(self, errcode):
        sys.exit(errcode)

    def reportErrorAndExit(self, errmess, printUsage=True):
        print ""
        print "Error: " + errmess
        print ""

        if printUsage:
            print self.parser.get_usage()
            print self.parser.format_option_help()

        self.exitScript(1)

    def buildParser(self):
        parser = OptionParser()

        parser.add_option("-a", "--address", dest="address",
                          help="The Xena chassis IP address",
                          default = None)
        parser.add_option("-p", "--portno", dest="portno",
                          help="Chassis TCP port number (optional, default 22611)", default = 22611)
        parser.add_option("-s", "--script", dest="scriptpath", help="Path to scriptfile", default = None)
        parser.add_option("-t", "--target", dest="target", help="Target module/port for scriptfile", default = None)
        parser.add_option("-r", "--rawlines", dest="rawlines", action="store_true", default=False,
                          help="Expect raw lines instead of a port config")

        usage = "Usage: %prog {options}"
        parser.set_usage(usage)

        return parser

    def checkArguments(self):
        if self.options.address is None:
            self.reportErrorAndExit("You must specify a address!")

        if self.options.scriptpath is None:
            self.reportErrorAndExit("You must specify a script file!")

        self.scriptpath = os.path.normpath(self.options.scriptpath)
        if not os.path.exists(self.scriptpath):
            self.reportErrorAndExit("Unable to find scriptfile '%s'!" % self.scriptpath)

        if self.options.target is None:
            self.reportErrorAndExit("You must specify a module/port target!")

        targetList = self.options.target.split('/')
        self.moduleIndex = int(targetList[0])
        self.portIndex = int(targetList[1])


    def loadScript(self):
        self.xm = XenaScriptTools(self.options.address)
        self.xm.LogonSetOwner("xena", "loader")

        starttime = datetime.datetime.now();
        self.xm.load_script(self.scriptpath, self.moduleIndex, self.portIndex, self.options.rawlines)
        endtime = datetime.datetime.now();

        print "Loaded script in %s" % (endtime - starttime)

if __name__ == '__main__':
    myApp = ScriptLoaderApp()
    myApp.loadScript()
