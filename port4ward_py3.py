#!/usr/bin/python3

# This is a simple port-forward / proxy, written using only the default python
# library. If you want to make a suggestion or fix something you can contact-me
# at voorloop_at_gmail.com
# Distributed over IDC(I Don't Care) license

# Originally for python-2: http://datareview.info/article/100-strok-koda-proksi-server-na-python/

import socket
import select
import time
import sys
import os

# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 4096
delay = 0.0001
#forward_to = ('smtp.zaz.ufsk.br', 25)
#forward_to = ('www.citforum.ru', 80)
forward_to = [None, None]
default_local_port = 9090
required_parameters_count = 1

def help():
    print("{} <remote_host:remote_port> [local_port] " .format(__file__))
    print("  remote_host:remote_port - remote address")
    print("  default local_port: {}" . format(default_local_port))
    print()


def ParseRemoteResource(name_and_port):
    parts = name_and_port.split(":")
    if len(parts) != 2:
        return None
    try:
        x = int(parts[1])
    except:
        return None
    parts[1] = x
    return parts


class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception as e:
            print(e)
            return False



class TheServer:
    input_list = []
    channel = {}

    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)

    def main_loop(self):
        self.input_list.append(self.server)
        while 1:
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept()
                    break

                self.data = self.s.recv(buffer_size)
                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    self.on_recv()

    def on_accept(self):
        forward = Forward().start(forward_to[0], forward_to[1])
        clientsock, clientaddr = self.server.accept()
        if forward:
            print(clientaddr, "has connected")
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            print("Can't establish connection with remote server.")
            print("Closing connection with client side", clientaddr)
            clientsock.close()

    def on_close(self):
        print(self.s.getpeername(), "has disconnected")
        #remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self):
        data = self.data
        # here we can parse and/or modify the data before send forward
        print(data)
        self.channel[self.s].send(data)

#--------------------------------- main ---------------------------------
if __name__ == '__main__':
        if len(sys.argv) < required_parameters_count+1:
            print("not enought parameters")
            help()
            exit(0)
        param1 = sys.argv[1].lower()
        if param1 == "-h" or param1 == "-help" or param1 == "--help" or param1 == "/?" or param1 == "-?" or param1 == "?":
            help()
            exit(0)
        forward_to = ParseRemoteResource(sys.argv[1])
        if forward_to == None:
            print("Wrong remote address")
            help()
            exit(1)

        local_port = default_local_port
        param_sn = 2
        if len(sys.argv) > param_sn:
            try:
                local_port = int(sys.argv[param_sn])
            except:
                print("Wrong local port [{}]" . format(sys.argv[param_sn]))
                help()
                exit(2)

        server = TheServer('', local_port)
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print("Ctrl C - Stopping server")
            sys.exit(1)
