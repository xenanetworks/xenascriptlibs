import string
import socket
import sys
import time


class SimpleSocket(object):

    def __init__(self, hostname, port = 22611, timeout = 20):
        self.hostname = hostname
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            sys.stderr.write("[Socket connection error] Cannot connect to %s, error: %s\n" % (hostname, msg[0]))
            sys.exit(1)

        self.sock.settimeout(timeout)

        try:
            self.sock.connect((hostname, port))
        except socket.error, msg:
            sys.stderr.write("[Socket connection error] Cannot connect to %s, error: %s\n" % (hostname, msg[0]))
            sys.exit(2)


    def __del__(self):
        self.sock.close()

    def SendCommand(self, cmd):
        self.sock.send(cmd + '\n')

    def Ask(self, cmd):
        self.sock.send(cmd + '\n')
        return self.sock.recv(2048)
    
    def AskMulti(self, cmd, num):
        self.sock.sendall((cmd).encode('utf-8'))

        data1 = self.sock.recv(512).decode('utf_8')
        data = data1
        run = 1
        begin = time.time()
        while True:
            diff = time.time() - begin
            if diff > 0.8:
                return False

            if data.count('\n') < num:
                data2 = self.sock.recv(512).decode('utf_8')
                data = data + data2
            else:
                break

        return data
    
    def set_keepalives(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 2)
