#!/usr/bin/python
import os
import time
import threading

from SocketDrivers import SimpleSocket


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


class XenaSocketDriver(SimpleSocket):
    reply_ok = '<OK>'

    def __init__(self, hostname, port = 22611):
        SimpleSocket.__init__(self, hostname = hostname, port = port)
        SimpleSocket.set_keepalives(self)
        self.access_semaphor = threading.Semaphore(1)

    def ask_verify(self, cmd):
        resp = self.Ask(cmd).strip('\n')
        #print '[ask_verify] %s' % resp
        if resp == self.reply_ok:
            return True
        return False

    def SendCommand(self, cmd):
        self.access_semaphor.acquire()
        SimpleSocket.SendCommand(self, cmd)
        self.access_semaphor.release()

    def Ask(self, cmd):
        self.access_semaphor.acquire()
        reply = SimpleSocket.Ask(self, cmd)
        self.access_semaphor.release()
        return reply

class XenaManager:
    cmd_logon                   = 'c_logon'
    cmd_logoff                  = 'c_logoff'
    cmd_owner                   = 'c_owner'
    cmd_reserve                 = 'p_reservation reserve'
    cmd_release                 = 'p_reservation release'
    cmd_relinquish              = 'p_reservation relinquish'
    cmd_reset                   = 'p_reset'
    cmd_port                    = ';Port:'
    cmd_start_traffic           = 'p_traffic on'
    cmd_stop_traffic            = 'p_traffic off'
    cmd_clear_tx_stats          = 'pt_clear'
    cmd_clear_rx_stats          = 'pr_clear'
    cmd_get_tx_stats            = 'pt_total ?'
    cmd_get_rx_stats            = 'pr_total ?'
    cmd_get_tx_stats_per_stream = 'pt_stream'
    cmd_get_rx_stats_per_tid    = 'pr_tpldtraffic'
    cmd_get_streams_per_port    = 'ps_indices'
    cmd_get_tid_per_stream      = 'ps_tpldid'

    cmd_comment                 = ';'

    def __init__(self, driver, password = 'xena'):
        self.driver = driver
        self.ports = []
        if self.logon(password):
            print '[XenaManager] Connected to %s' % self.driver.hostname
        else:
            print '[XenaManager] Fialed to establish connection'
            return
            #raise
        self.set_owner()

        self.keep_alive_thread = KeepAliveThread(self.driver)
        self.keep_alive_thread.start()

    def __del__(self):
        for module_port in self.ports:
            self.release(module_port)
        self.ports = []
        self.keep_alive_thread.stop()
        self.driver.ask_verify(self.cmd_logoff)
        #del self.keep_alive_thread

    def _compose_str_command(self, cmd, argument):
        command = cmd + ' \"' + argument + '\"'
        return command

    def logon(self, password):
        command = self._compose_str_command(self.cmd_logon, password)
        return self.driver.ask_verify(command)

    def set_owner(self):
        """
        set ports owner, trancated to 8 characters
        """
        computer_name = os.getenv('COMPUTERNAME')[:8]
        command = self._compose_str_command(self.cmd_owner, computer_name)
        return self.driver.ask_verify(command)

    def reserve(self, module_port):
        cmd = module_port + ' ' + self.cmd_reserve
        return self.driver.ask_verify(cmd)

    def release(self, module_port):
        cmd = module_port + ' ' + self.cmd_relinquish
        return self.driver.ask_verify(cmd)
        cmd = module_port + ' ' + self.cmd_release
        return self.driver.ask_verify(cmd)

    def reset(self):
        return self.driver.ask_verify(self.cmd_reset)

    def add_module_port(self, module_port):
        if module_port not in self.ports:
            self.ports.append(module_port)

    def remove_module_port(self, module_port):
        if module_port in self.ports:
            self.ports.remove(module_port)

    def set_module_port(self, module_port):
        self.driver.SendCommand(module_port)

    def load_script(self, filename):
        line_number = 0;
        for line in open(filename, 'r'):
            command = line.strip('\n')
            line_number += 1

            if command.startswith(self.cmd_port):
                t = command.split()
                module_port = t[-1]

                self.release(module_port)
                self.set_module_port(module_port)

                if not self.reserve(module_port):
                    print '[XenaManager] Cannot reserve port %s' % module_port
                else:
                    print '[XenaManager] Port %s reserved' % module_port
                    self.remove_module_port(module_port)
                if not self.reset():
                    print '[XenaManager] Cannot reset port %s' % module_port
                    self.remove_module_port(module_port)
                self.add_module_port(module_port)

            if command.startswith(self.cmd_comment):
                continue

            if not self.driver.ask_verify(command.strip('\n')):
                print '[XenaManager] Error in script in line: %d, [%s]' % (line_number, command)
                print '[XenaManager] Load interrupted!'
                break

        print '[XenaManager] Script [%s] loaded succesfully.' % filename

    def clear_stats_per_port(self, module_port):
        cmd = module_port + ' ' + self.cmd_clear_rx_stats
        resp = self.driver.ask_verify(cmd)
        cmd = module_port + ' ' + self.cmd_clear_tx_stats
        resp = self.driver.ask_verify(cmd)

    def _parse_stats_str(self, s):
        t = s.strip('\n').split()
        return {'packets':int(t[-1]), 'bytes':int(t[-2]), 'pps':int(t[-3]), 'bps':int(t[-4])}

    def get_stats_per_port(self, module_port):
        stats = {}
        cmd = module_port + ' ' + self.cmd_get_rx_stats
        stats['rx'] = self._parse_stats_str(self.driver.Ask(cmd))
        cmd = module_port + ' ' + self.cmd_get_tx_stats
        stats['tx'] = self._parse_stats_str(self.driver.Ask(cmd))
        return stats

    def get_stats_per_stream(self, source_module_port, dest_module_port, stream):
        stats = {}
        cmd = '%s %s [%d] ?' % (source_module_port, self.cmd_get_tx_stats_per_stream, stream)
        stats['tx'] = self._parse_stats_str(self.driver.Ask(cmd))

        tid = self.get_tid_per_stream(source_module_port, stream)
        cmd = '%s %s [%d] ?' % (dest_module_port, self.cmd_get_rx_stats_per_tid, tid)
        stats['rx'] = self._parse_stats_str(self.driver.Ask(cmd))
        return stats

    def start_traffic_per_port(self, module_port):
        cmd = module_port + ' ' + self.cmd_start_traffic
        return self.driver.ask_verify(cmd)

    def stop_traffic_per_port(self, module_port):
        cmd = module_port + ' ' + self.cmd_stop_traffic
        return self.driver.ask_verify(cmd)

    def get_streams_per_port(self, module_port):
        cmd = '%s %s ?' % (module_port, self.cmd_get_streams_per_port)
        resp = self.driver.Ask(cmd).strip('\n').lower().split()
        resp.reverse()
        streams = []
        for e in resp:
            if e == self.cmd_get_streams_per_port:
                return streams
            streams.append(int(e))
        return streams

    def get_tid_per_stream(self, module_port, stream):
        cmd = '%s %s [%d] ?' % (module_port, self.cmd_get_tid_per_stream, stream)
        resp = self.driver.Ask(cmd).strip('\n').lower().split()
        return int(resp[-1])


#===============================================================================
def get_multistream_stats(xm):
    """ Assumes only two ports were added to XenaManager """
    stats = {}
    ports = xm.ports
    for port_index in range(2):
        streams = xm.get_streams_per_port(ports[port_index])
        stats[ports[port_index]] = []
        for stream in streams:
            tmp_stats = xm.get_stats_per_stream(ports[port_index], ports[(port_index + 1) % 2],  stream)
            tmp_res = tmp_stats['tx']['packets'] == tmp_stats['rx']['packets']
            stats[ports[port_index]].append( (tmp_stats['tx']['packets'], tmp_stats['rx']['packets'], tmp_res) )

    return stats

def get_statistics(xm, period = 300):
    """ Get statistics from all the ports """
    for module_port in xm.ports:
        xm.stop_traffic_per_port(module_port)
        xm.clear_stats_per_port(module_port)

    time.sleep(10)

    print 'Traffic stopped, stats cleared'

    for module_port in xm.ports:
        xm.start_traffic_per_port(module_port)

    print 'Traffic started'
    time.sleep(period)

    for module_port in xm.ports:
        xm.stop_traffic_per_port(module_port)

    time.sleep(10)

    print 'Traffic stopped'
    print 'Stats'

    stats = get_multistream_stats(xm)

    return stats

if __name__ == '__main__':
    driver = XenaSocketDriver('192.168.42.38')
    xm = XenaManager(driver)


    xm.load_script(r'p:\lab\tools\LabUtils\RFLab\ARQTests\port4.xpc')
    xm.load_script(r'p:\lab\tools\LabUtils\RFLab\ARQTests\port5.xpc')

    print get_statistics(xm, 10)
