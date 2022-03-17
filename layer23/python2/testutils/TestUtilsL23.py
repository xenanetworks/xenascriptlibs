import os, sys, time, threading, inspect

from .SocketDrivers import SimpleSocket

LOGFILE = "XENALOG"

RESET           = " p_reset"
RESERVATION     = " p_reservation ?"
RESERVE         = " p_reservation reserve"
RELINQUISH      = " p_reservation relinquish"
RELEASE         = " p_reservation release"

TRAFFIC_ON      = " p_traffic on"
TRAFFIC_OFF     = " p_traffic off"

COMMENT_START   = ';'

def errexit(msg):
    print "Error: " + msg + ", exiting..."
    sys.exit(1)

## Keepalive thread to ensure tcp connection is kept open
# do not edit this 
class KeepAliveThread(threading.Thread):
    message = ''
    def __init__(self, connection, interval = 10):
        threading.Thread.__init__(self)
        self.connection = connection
        self.interval = interval
        self.finished = threading.Event()
        self.setDaemon(True)
        print '[KeepAliveThread] Thread initiated, interval %d seconds' % (self.interval)

    def stop (self):
        self.finished.set()
        self.join()

    def run (self):
        while not self.finished.isSet():
            self.finished.wait(self.interval)
            self.connection.Ask(self.message)


## Low level driver for TCPIP based queried
# do not edit this
class XenaSocketDriver(SimpleSocket):

    def __init__(self, hostname, port = 22611):
        SimpleSocket.__init__(self, hostname = hostname, port = port)
        SimpleSocket.set_keepalives(self)
        self.access_semaphor = threading.Semaphore(1)

    def SendCommand(self, cmd):
        self.access_semaphor.acquire()
        print "Sending command: " + cmd
        SimpleSocket.SendCommand(self, cmd)
        self.access_semaphor.release()

    def Ask(self, cmd):
        self.access_semaphor.acquire()
        reply = SimpleSocket.Ask(self, cmd).strip('\n')
        self.access_semaphor.release()
        return reply


## Xena supplied class example for Scripting via Python
# feel free to add functions below
# 
class XenaScriptTools:

    def __init__(self, ip):
        self.ip    = ip
        self.debug = 0
        self.halt  = 0 
        self.log   = 0
        self.cmds  = []
        self.logf  = os.environ.get(LOGFILE)
        if self.logf != None:
            self.log = 1
        self.driver= XenaSocketDriver(ip)

    def __del__(self):
        if self.log:
            lf = open(self.logf, 'w')
            for cmd in self.cmds:
                lf.write(cmd + "\n")
            lf.close()
        return

    ## Enable debug - prints commands and errors
    def debugOn(self):
        self.debug = 1
        return 

    ## Disable debug (default) - no printed output
    def debugOff(self):
        self.debug = 0
        return 

    def debugMsg(self, msg):
        if self.debug == 1:
            print msg

    def logCmd(self, cmd):
        if self.log == 1:
            self.cmds.append(cmd)
    
    ## Enable halt on error - calls sys.exit(1) upon error
    def haltOn(self):
        self.halt = 1
        return 
 
    ## Disable halt on error (default)
    def haltOff(self):
        self.halt = 0
        return 

    ## Print diagnostics msg and halt
    def errexit(self, msg):
        if self.halt == 1:
            print
            print "Error: " + msg + ", exiting..."
            print
            sys.exit(1)

###############################################
## Send and Expect primitives 
###############################################

    ## Send command and return response
    def Send(self, cmd):
        res = self.driver.Ask(cmd)
        self.debugMsg("Send()         : " + cmd)
        self.debugMsg("Send() received: " + res)
        self.logCmd(cmd)
        return res
    
    ## Send multiple commands and return all responses
    def SendMulti(self, cmdlist):
        cmd = ''
        num = len(cmdlist)
        for i in range (0,num):
            cmd = cmd + cmdlist[i] + '\n'
        
        self.debugMsg("Send()         : " + cmd)
              
        res = self.driver.AskMulti(cmd, num)
            
        self.debugMsg("Send() received: " + str(res))
        self.logCmd(cmd)
        return res

    ## Send command and expect response (typically <OK>)
    def SendExpect(self, cmd, resp):
        self.debugMsg("SendExpect("+resp+"): " + cmd)
        self.logCmd(cmd)

        res = self.driver.Ask(cmd)
        if res.rstrip('\n') == resp:
            return True;
        else:
            self.debugMsg("SendExpect() failed")
            self.debugMsg("   Expected: " + resp)
            self.debugMsg("   Received: " + res)
            self.errexit("Halting in line %d" % (inspect.currentframe().f_back.f_lineno))
            return False


    ## Send commands and expect <OK>
    def SendExpectOK(self, cmd):
        return self.SendExpect(cmd, "<OK>")


    ## Send command and match response with specified string
    def SendAndMatch(self, cmd, str):
        self.debugMsg("SendAndMatch() : " + cmd)
        self.logCmd(cmd)

        res = self.driver.Ask(cmd)
        if res.find(str) != -1:
            return True
        else:
            self.debugMsg("SendAndMatch() failed")
            self.debugMsg("   Expected: " + str)
            self.debugMsg("   Got     : " + res)
            self.errexit("Halting in line %d" % (inspect.currentframe().f_back.f_lineno))
            return False


###############################################
## Xena Scripting API specific commands
###############################################

    ##############################
    # Chassis and Logon Commands 
    ##############################

    ## Logon
    def Logon(self, pwd):
        self.SendExpectOK("c_logon \"" + pwd  + "\"")

    ## Logon and set owner
    def LogonSetOwner(self, pwd, owner):
        self.Logon(pwd)
        self.SendExpectOK("c_owner \"" + owner + "\"")


    ## Logon to chassis, set user name and password, then reserve ports
    def LogonAndReserve(self, ports, pwd, owner):
        if type(ports) == type(str()):
            ports = [ports]
        self.LogonSetOwner(pwd, owner)
        self.PortReserve(ports)

    # Reserve chassis, release or relinquish first if necessary
    def ChassisReserve(self):
        self.ChassisRelease()
        self.SendExpectOK("C_RESERVATION reserve")

    # Reserve chassis, release or relinquish first if necessary
    def ChassisRelease(self):
        res = self.Send("C_RESERVATION ?").split()[1]
        if res.find("RESERVED_BY_YOU") != -1:
            self.debugMsg("Chassis is reserved by me - release")
            self.SendExpectOK("C_RESERVATION release")
        elif res.find("RESERVED_BY_OTHER") != -1:
            self.debugMsg("Chassis is reserved by other - relinquish")
            self.SendExpectOK("C_RESERVATION relinquish")
        elif res.find("RELEASED") != -1:
            self.debugMsg("Chassis is released - do nothing")
        else:
            self.errexit("Halting in line %d" % (inspect.currentframe().f_back.f_lineno))

    ##############################
    # Misc Commands
    ##############################
    def Comment(self, text):
        self.Send("; ######################################")
        self.Send("; " + text)
        self.Send("; ######################################")

    ##############################
    # Port Commands
    ##############################

    ## Reserve a port - if port is reserved, release or relinquish, then reserve
    def PortReserve(self, ports):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            res = self.Send(port + RESERVATION)
            if res.find("RESERVED_BY_OTHER") != -1:
                self.debugMsg("Port " + port + " is reserved by other - relinquish")
                self.SendExpectOK(port + RELINQUISH)
                self.SendExpectOK(port + RESERVE)
            elif res.find("RESERVED_BY_YOU") != -1:
                self.debugMsg("Port " + port + " is reserved by me - do nothing")
            else:
                self.SendExpectOK(port + RESERVE)

    def PortRelease(self, ports):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            res = self.Send(port + RESERVATION)
            if res.find("RESERVED_BY_YOU") != -1:
                self.SendExpectOK(port + RELEASE)

    def PortRelinquish(self, ports):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            res = self.Send(port + RESERVATION)
            if res.find("RESERVED_BY_OTHER") != -1:
                self.SendExpectOK(port + RELINQUISH)

    ## Start traffic on ports 
    def PortTrafficStart(self, ports):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            res = self.SendExpectOK(port + TRAFFIC_ON)

    ## Stop traffic on ports 
    def PortTrafficStop(self, ports):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            res = self.SendExpectOK(port + TRAFFIC_OFF)

    def get_module_port_prefix(self, moduleIndex, portIndex):
        return "%d/%d" % (moduleIndex, portIndex)

    def load_script(self, filename, moduleIndex, portIndex, israwlines=False):
        module_port_prefix = self.get_module_port_prefix(moduleIndex, portIndex)
        self.PortReserve(module_port_prefix)

        if not israwlines:
            self.driver.SendCommand(module_port_prefix)

        line_number = 0;
        send_count = 0;

        for line in open(filename, 'r'):
            command = line.strip('\n')
            line_number += 1

            if command.startswith(COMMENT_START):
                continue

            success = self.SendExpectOK(command.strip('\n'))
            if not success:
                print '[XenaManager] Error in script at line: %d, [%s]' % (line_number, command)
                print '[XenaManager] Load interrupted!'
                return

            send_count += 1
            if send_count % 100 == 0:
                print "\r[XenaManager] (Sent %d commands ...)" % send_count,

        print "\r[XenaManager] Script '%s' (%d commands) loaded succesfully." % (filename, send_count)
