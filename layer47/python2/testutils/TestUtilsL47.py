import os, sys, time, threading, inspect

from .SocketDrivers import SimpleSocket
from .PacketParse import *

LOGFILE         = "XENALOG"

RESET           = " p_reset"
RESERVATION     = " p_reservation ?"
RESERVE         = " p_reservation reserve"
RELINQUISH      = " p_reservation relinquish"
RELEASE         = " p_reservation release"
TRAFFIC         = " p4_traffic "
TRAFFIC_OFF     = " p4_traffic off"
TRAFFIC_STOP    = " p4_traffic stop"
TRAFFIC_PREPARE = " p4_traffic prepare"
STATE           = " p4_state ?"
SPEEDSEL        = " p4_speedselection "
PE_ALLOCATE     = " p4e_allocate "

def errexit(msg):
    print "Error: " + msg + ", exiting..."
    sys.exit(1)


class LoadProfile():

    def __init__(self, t0, t1, t2, t3, timescale):
        self.t0 = t0
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.timescale = timescale

    def sett0(self, t0):
        self.t0 = t0

    def shape(self):
        return str(self.t0) + " " +  str(self.t1) + " " + str(self.t2) + " " + str(self.t3)

    def scale(self):
        return self.timescale

    def duration_sec(self):
        t = self.t0 + self.t1 + self.t2 + self.t3
        if self.timescale == "msecs":
            return t/1000
        elif self.timescale == "sec":
            return t
        else :
            errexit("unknown timescale: %s" % (timescale))
        
   

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
        SimpleSocket.send_command(self, cmd)
        self.access_semaphor.release()

    def Ask(self, cmd):
        self.access_semaphor.acquire()
        reply = SimpleSocket.ask(self, cmd).strip('\n')
        self.access_semaphor.release()
        return reply


## Xena supplied class example for Scripting via Python
# feel free to add functions below
# 
class XenaScriptTools:

    states_passive = ["STOPPED", "OFF", "PREPARE", "PREPARE_RDY" ]
    states_active  = ["RUNNING", "PRERUN_RDY", "PRERUN" ]


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


    ## Send command and expect response (typically <OK>)
    def SendExpect(self, cmd, resp):
        self.debugMsg("SendExpect("+resp+"): " + cmd)
        self.logCmd(cmd)

        res = self.driver.Ask(cmd)
        if res.rstrip('\n') == resp:
            return True
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
    # Module Commands
    ##############################

    # Reserve module, release or relinquish first if necessary
    def ModuleRelease(self, module):
        mod = str(module)
        res = self.Send(mod + " M_RESERVATION ?").split()[2]
        if res.find("RESERVED_BY_YOU") != -1:
            self.debugMsg("Module is reserved by me - release")
            self.SendExpectOK(mod + " M_RESERVATION release")
        elif res.find("RESERVED_BY_OTHER") != -1:
            self.debugMsg("Chassis is reserved by other - relinquish")
            self.SendExpectOK(mod + " M_RESERVATION relinquish")
        elif res.find("RELEASED") != -1:
            self.debugMsg("Chassis is released - do nothing")
        else:
            self.errexit("Halting in line %d" % (inspect.currentframe().f_back.f_lineno))


    def ModuleReserve(self, module):
        self.ModuleRelease(module)
        mod = str(module)
        self.SendExpectOK(mod + " M_RESERVATION reserve")


    ###########################
    # Port Commands
    ###########################

    ## Wait for port to be 'released' - warning can hang forever!
    def PortWaitReleased(self, ports):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            reserved = 1
            while reserved:
                res = self.Send(port + RESERVATION)
                if res.find("RELEASED") != -1:
                    reserved = 0
                else:
                    time.sleep(0.1)

    ## Reserve a port - if port is reserved, release or relinquish, then reserve
    def PortReserve(self, ports):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            res = self.Send(port + RESERVATION)
            if res.find("RESERVED_BY_OTHER") != -1:
                self.debugMsg("Port " + port + " is reserved by other - relinquish")
                self.SendExpectOK(port + RELINQUISH)
                self.PortWaitReleased(port)
            self.SendExpectOK(port + RESERVE)

    ## Release a port/ports
    def PortRelease(self, ports):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            self.SendExpectOK(port + " P_RESERVATION release")


    ## Wait for port to be in state 'state' - warning can hang forever!
    def PortWaitState(self, ports, state):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            running = 1
            while running:
                res = self.Send(port + STATE)
                if res.find(state) != -1:
                   running = 0
                else:
                   time.sleep(0.1)

    ## Set port in state OFF - valid from any port state
    def PortStateOff(self, ports):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports: 
            res = self.Send(port + STATE).split()[2]
            if res in self.states_active:
                self.Send(port + TRAFFIC_STOP)
                self.PortWaitState(port, "STOPPED")
        for port in ports:
            self.Send(port + TRAFFIC_OFF)
            self.PortWaitState(port, "OFF")


    ## Set port state to 'state' - assume ports are in relevant state
    def PortSetTraffic(self, ports, state):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            self.SendExpectOK(port + TRAFFIC + state) 

    ## Set port speed
    def PortSetSpeed(self, ports, speed):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            self.SendExpectOK(port + SPEEDSEL + speed)

    ## Verify port speed
    def PortVerifySpeed(self, ports, speed):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            res = self.Send(port + SPEEDSEL + "?").split()[2]
            if res.find(speed) == -1:
                self.errexit("PortSpeed mismatch on port %s, expected %s, got %s" % (port, speed, res))


    ## Reset ports -  - valid from any port state
    def PortReset(self, ports):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            self.SendExpectOK(port + RESET)
            self.PortWaitState(port, "OFF")

   
    ## Send traffic Prepare - assume ports are in state OFF 
    def PortPrepare(self, ports):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            self.SendExpectOK(port + TRAFFIC_PREPARE)
            self.PortWaitState(port, "PREPARE_RDY")


    ## Set port role - assume ports are in state OFF
    def PortRole(self, ports, id, role):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            SID = " [" + str(id) + "] "
            self.SendExpectOK(port + " P4G_ROLE " + SID + " " + role)

    ## Allocate PEs
    def PortAllocatePE(self, ports, nbpe):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            self.SendExpectOK(port + PE_ALLOCATE + str(nbpe))


    #############################
    # Connection Group Commands 
    #############################

    def PortAddConnGroup(self, ports, id, clients, servers, ipver):
        if type(ports) == type(str()):
            ports = [ports]
        SID = " [" + str(id) + "] "
        for port in ports:
            self.SendExpectOK(port + " P4G_CREATE " + SID)
            if ipver == 6:
              PREFIX="IPV6_"
              self.SendExpectOK(port + " P4G_IP_VERSION " + SID + "IPV6")
            else:
              PREFIX=""
            self.SendExpectOK(port + " P4G_"+PREFIX+"CLIENT_RANGE " + SID + " " + clients)
            self.SendExpectOK(port + " P4G_"+PREFIX+"SERVER_RANGE " + SID + " " + servers)


    def PortAddLoadProfile(self, ports, id, lp_shape, lp_timescale):
        if type(ports) == type(str()):
            ports = [ports]
        SID = " [" + str(id) + "] "
        for port in ports:
            self.SendExpectOK(port + " P4G_LP_SHAPE "      + SID + " " + lp_shape)
            self.SendExpectOK(port + " P4G_LP_TIME_SCALE " + SID + " " + lp_timescale)


    def PortSetRole(self, ports, id, role):
        if type(ports) == type(str()):
            ports = [ports]
        SID = " [" + str(id) + "] "
        for port in ports:
            self.SendExpectOK(port + " P4G_ROLE " + SID + " " + role)
        

    def PortGetPackets(self, ports, n):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            first=1
            pp = PacketParse()
            print "Port: " + port
            for i in range(n):
                if first:
                    res = self.Send(port + " P4_CAPTURE_GET_FIRST ?")
                    first=0
                else:
                    res = self.Send(port + " P4_CAPTURE_GET_NEXT ?")
                pp.Parse(res)

    def PortGetRxPackets(self, port):
        res = self.Send(port + " P4_ETH_RX_COUNTERS ?")
        packets = int(res.split()[7])
        return packets, res


    def PortClearCounters(self, ports):
        if type(ports) == type(str()):
            ports = [ports]
        for port in ports:
            self.SendExpectOK(port + " P4_CLEAR_COUNTERS ")
        

    def PrintPortStatistics(self, ports):
        if type(ports) == type(str()):
            ports = [ports]
        print "%-5s %-3s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s" % ("Port", "Dir", "Pkts", "IP", "ARPREQ", "ARPREP", "IP6", "NDPREQ", "NDPREP", "TCP")
        for port in ports:
            for dir in ["RX", "TX"]:
               eth    = self.Send(port + " P4_ETH_" + dir + "_COUNTERS ?").split()
               pkt    = eth[7]
               
               proto  = self.Send(port + " P4_IPV4_" + dir + "_COUNTERS ?").split()
               ip     = proto[4]
               
               proto  = self.Send(port + " P4_ARP_" + dir + "_COUNTERS ?").split()
               arpreq = proto[4]
               arprep = proto[5]
               
               proto  = self.Send(port + " P4_TCP_" + dir + "_COUNTERS ?").split()
               tcp    = proto[4]

               proto6  = self.Send(port + " P4_IPV6_" + dir + "_COUNTERS ?").split()
               ip6    = proto6[4]
               
               proto6  = self.Send(port + " P4_NDP_" + dir + "_COUNTERS ?").split()
               ndpreq = proto6[4]
               ndprep = proto6[5]
               print "%-5s %-3s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s" % (port, dir, pkt, ip, arpreq, arprep, ip6, ndpreq, ndprep, tcp)


    #######################################
    # Regression Testing Helper Functions
    #######################################

    def TestPre(self, ports):
        print "TestPre()"

        print "  Reserve ports " + " ".join(ports)
        self.PortReserve(ports)

        print "  Reset ports"
        self.PortReset(ports)

        self.PortAllocatePE(ports, 2)


    def TestPost(self, ports):
        print "TestPost()"
        print "  Set ports to off"
        self.PortStateOff(ports)


    def TestPrepareAndStart(self, servers, clients):
        ports = servers + clients
        print "  Prepare ports"
        self.PortPrepare(ports)

        print "  Start servers"
        self.PortSetTraffic(servers, "ON")
        self.PortWaitState(servers, "RUNNING")

        print "  Start clients"
        self.PortSetTraffic(clients, "ON")
        self.PortWaitState(clients, "RUNNING")


    def TestValidateGoodputRx(self, cgis, ports, bytes_pr_cg):
        self.TestValidateGoodput(cgis, ports, 1, bytes_pr_cg)


    def TestValidateGoodputTx(self, cgis, ports, bytes_pr_cg):
        self.TestValidateGoodput(cgis, ports, 0, bytes_pr_cg)


    def TestValidateGoodput(self, cgis, ports, rx, bytes_pr_cg):
        if rx == 1:
            CMD = "P4G_TCP_RX_PAYLOAD_COUNTERS"
            TXT = "Rx"
        elif rx == 0:
            CMD = "P4G_TCP_TX_PAYLOAD_COUNTERS"
            TXT = "Tx"
        else:
            self.errexit("TestValidateGoodPut() invalid value of rx: %d" % (rx))

        print "    validating goodput bytes (%s)" % (TXT)

        good_bytes=0
        nb_ports = len(ports)
        for port in ports:
            for cgi in range(cgis):
                sres = self.Send(port + CMD + "[" + str(cgi) + "] ?").split()[7]
                res = int(sres)
                if res != bytes_pr_cg:
                    print "    [%d] %s %d bytes, expected %d" % (cgi, TXT, res, bytes_pr_cg)
                good_bytes = good_bytes + res

        if good_bytes != nb_ports * cgis * bytes_pr_cg:
             self.errexit("%s Failed: Expected %d bytes, got %d" % (TXT, cgis * bytes_pr_cg, good_bytes))
    


    def TestSetupApplicationRaw(self, ports, cgi, scenario, utilization, len):
        CGI = "[" + str(cgi) + "] "
        print "      [%02d] Appl: raw, Scen: %s, Util: %d, Len: %d" % (cgi, scenario, utilization, len)    
        for port in ports:
            self.SendExpectOK(port + " P4G_TEST_APPLICATION "      + CGI + "RAW")
            self.SendExpectOK(port + " P4G_RAW_TEST_SCENARIO "     + CGI +  scenario)
            self.SendExpectOK(port + " P4G_RAW_PAYLOAD_TYPE "      + CGI + "INCREMENT")
            self.SendExpectOK(port + " P4G_RAW_PAYLOAD_TOTAL_LEN " + CGI + "FINITE " + str(len))
            self.SendExpectOK(port + " P4G_RAW_HAS_DOWNLOAD_REQ "  + CGI + "NO")
            self.SendExpectOK(port + " P4G_RAW_CLOSE_CONN "        + CGI + "NO")
            self.SendExpectOK(port + " P4G_RAW_TX_DURING_RAMP "    + CGI + "NO NO")
            #self.SendExpectOK(port + " P4G_RAW_TX_TIME_OFFSET "    + CGI + "50 50 ")
            self.SendExpectOK(port + " P4G_RAW_UTILIZATION "       + CGI +  str(utilization))
            self.SendExpectOK(port + " P4G_TCP_WINDOW_SIZE "       + CGI + "65535")
            self.SendExpectOK(port + " P4G_TCP_MSS_VALUE "         + CGI + "1460")

  ####################################################################

    def TestPortSpeedChange(self, portlist):
        print "TestPortSpeedChange()"

        self.TestPre(portlist)

        speeds = [ "F1G", "F10G" ]

        for speed in speeds:
            print "  Setting portspeed to " + speed
            self.PortSetSpeed(portlist, speed)
            time.sleep(1)

            print "  Verifying portspeed " + speed
            self.PortVerifySpeed(portlist, speed)
            time.sleep(1)

        self.TestPost(portlist)
        print "PASS"

  ####################################################################

    def TestConnectionGroups(self, n, conn_pr_cg, clients, servers):
        print "TestConnectionGroups()"

        ports = clients + servers
        if n > 200:
            errexit("Too many (%d) Connection Groups (max 200)" % (n))

        if n * conn_pr_cg > 4000000:
            errexit("Number of connections (%d) exceed 4M" % (n * conn_pr_cg))

        print "  %d connection groups requested" % (n)

        self.TestPre(ports)
 
        bytes_pr_conn   = 1000
        ramp = (n*conn_pr_cg*1000)/500000 + 1

        cln_rng_t = ".0.0.2 " + str(conn_pr_cg) + " 40000 1"
        svr_rng_t = ".0.0.1 1 80 1"
        lp = LoadProfile(0, ramp, 6000, ramp, "msecs")
   
        print "    setting up connection groups"
        for cgi in range(n):
            client_range = str(10 + cgi) + cln_rng_t
            server_range = str(10 + cgi) + svr_rng_t
            print "      [%2d] client: %s, server: %s, lp_shape: \"%s\" %s" % (cgi, client_range, server_range, lp.shape(), lp.scale())
            self.PortAddConnGroup(ports, cgi, client_range, server_range)

            print "      [%2d] clients: %s, servers: %s" % (cgi, " ".join(clients), " ".join(servers))
            self.PortSetRole(clients, cgi, "client")
            self.PortSetRole(servers, cgi, "server")

            self.PortAddLoadProfile(ports, cgi, lp.shape(), lp.scale())

        print "    verifying created connection groups"
        for port in ports:
            print "      verifying connection groups on port %s" % (port)
            cg = self.Send(port + " P4G_INDICES ?").split()
            if len(cg) != n + 2:
                self.errexit("number of cgs (%d) does not match expected (%d)" % (len(cg)-2, n))

        util = int(1000000/n/2)
        print "    setting application RAW, DOWNLAOD, Utilization %d" % (util)
        for cgi in range(n):
            self.TestSetupApplicationRaw(ports, cgi, "DOWNLOAD", util, bytes_pr_conn)

        self.TestPrepareAndStart(servers, clients)

        duration = lp.duration_sec() + 3
        for i in range(duration):
            time.sleep(1)
            for port in ports:
                res = self.PortGetRxPackets(port)
                print "%3ds %s" % (duration -i, res[1])

        #print "  Stopping Ports"
        self.PortSetTraffic(ports, "STOP")

        self.TestValidateGoodputTx(n, servers, bytes_pr_conn * conn_pr_cg)
        self.TestValidateGoodputRx(n, clients, bytes_pr_conn * conn_pr_cg)


        self.TestPost(ports)
        print "PASS"

    #######################################
    # Regression Testing Main Functions
    #######################################


    def RegressionTestSpeed(self, portlist):
        print "Regression test Portspeed"
        print "Logging on to chassis %s" % (self.ip)

        self.Logon("xena")
        self.TestPortSpeedChange(portlist)


    def RegressionTest(self, portpairs, nb_cgs, conn_pr_cg):
        servers = []
        clients = []

        print
        print "Regression test"

        if len(portpairs)%2 != 0:
            self.errexit("portpair list is odd")

        for i in range(len(portpairs)):
            if i%2 == 0:
                servers.append(portpairs[i])
            else:
                clients.append(portpairs[i])

        self.debugMsg("Clients " + " ".join(clients))
        self.debugMsg("Servers " + " ".join(servers))

        print "Logging on to chassis %s" % (self.ip)
        self.Logon("xena")

        self.TestConnectionGroups(nb_cgs, conn_pr_cg, clients, servers)

        print "DONE" 
