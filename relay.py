import threading
import socket


class Relay(object):

    def __init__(self, relayType, clientSock, clientInfo, targetRelay='', targetRelayPort=''):
        self.targetRelayPort = targetRelayPort
        self.targetRelay = targetRelay
        self.clientInfo = clientInfo
        self.clientSock = clientSock
        self.relayType = relayType

        if self.relayType == 'c':

            self.serverSock = socket.socket()

            try:
                self.serverSock.connect((self.targetRelay, self.targetRelayPort))
            except:
                print('Could not connect to relay')
                self.clientSock.close()
                self.serverSock.close()
                return

            self.targetServ = raw_input('Target server IP\n> ')

            try:
                self.serverSock.send(self.targetServ)
            except:
                print('Peer disconnected')
                self.clientSock.close()
                self.serverSock.close()
                return

            if self.serverSock.recv(3) != 'OK':
                print('Target relay exited due to bad IP')
                self.serverSock.close()
                self.clientSock.close()
                return

            self.targetServPort = raw_input('Target server port\n> ')

            try:
                self.serverSock.send(self.targetServPort)
            except:
                print('Peer disconnected')
                self.clientSock.close()
                self.serverSock.close()
                return

            if self.serverSock.recv(3) != 'OK':
                print('Target relay exited due to bad port')
                self.serverSock.close()
                self.clientSock.close()
                return

            self.start()

        elif self.relayType == 'r':

            self.targetServ = self.clientSock.recv(120)

            try:
                socket.inet_aton(self.targetServ)
                self.clientSock.send('OK')
            except:
                try:
                    self.targetServ = socket.gethostbyname(self.targetServ)
                    self.clientSock.send('OK')
                except:
                    print('Client sent invalid destination IP address')
                    self.clientSock.send('ERR')
                    self.clientSock.close()
                    return

            self.targetServPort = self.clientSock.recv(5)

            try:
                self.targetServPort = int(self.targetServPort)
            except:
                print('Client sent invalid destination port')
                self.clientSock.send('ERR')
                self.clientSock.close()
                return

            if (self.targetServPort < 1) or (self.targetServPort > 65535):
                print('Client sent invalid destination port')
                self.clientSock.send('ERR')
                self.clientSock.close()
                return

            try:
                self.clientSock.send('OK')
            except:
                print('Peer diisconnected')
                self.clientSock.close()
                return

            self.serverSock = socket.socket()

            try:
                self.serverSock.connect((self.targetServ, self.targetServPort))
            except:
                print('Could not connect to server')
                self.serverSock.close()
                self.clientSock.close()
                return

            self.start()

    class Send(threading.Thread):

        def __init__(self, clientsock, serversock):
            threading.Thread.__init__(self)

            self.clientsock = clientsock
            self.serversock = serversock

        def run(self):
            while True:
                try:
                    self.serversock.send(self.clientsock.recv(10000))
                except:
                    print('Peer disconnected')
                    return

    class Recv(threading.Thread):

        def __init__(self, clientsock, serversock):
            threading.Thread.__init__(self)

            self.clientsock = clientsock
            self.serversock = serversock

        def run(self):
            while True:
                try:
                    self.clientsock.send(self.serversock.recv(10000))
                except:
                    print('Peer disconnected')
                    return

    def start(self):

        self.Send(self.clientSock, self.serverSock).start()
        self.Recv(self.clientSock, self.serverSock).start()


if __name__ == '__main__':
    mainsock = socket.socket()


    relayType = raw_input('Client or Relay? [C]/R\n> ').lower()

    if relayType == '':
        relayType = 'c'

    if relayType not in ('c', 'r'):
        print('Please enter either "C" or "R"')
        exit()

    if relayType == 'c':
        targetRelay = raw_input('Target relay IP\n> ')

        try:
            socket.inet_aton(targetRelay)
        except:
            try:
                socket.gethostbyname(targetRelay)
            except:
                print('Client sent invalid destination IP address')
                exit()

        targetRelayPort = raw_input('Target relay port\n> ')

        try:
            targetRelayPort = int(targetRelayPort)
        except:
            print('Invalid relay port')
            exit()

        if (targetRelayPort < 1) or (targetRelayPort > 65535):
            print('Invalid relay IP supplied')
            exit()


    listenIp = raw_input('Which IP should this relay listen on?\n> ')

    try:
        listenPort = int(raw_input('Which port should this relay listen on?\n> '))
    except:
        print('Please enter an integer between 1 and 65535')
        exit()

    if (listenPort < 1) or (listenPort > 65535):
        print('Please enter an integer between 1 and 65535')
        exit()

    try:
        mainsock.bind((listenIp, listenPort))
    except:
        print('Address %s:%d cannot be used; it is either invalid or already in use.' % (listenIp, listenPort))
        exit()

    mainsock.listen(5)

    while True:
        clientSock, clientInfo = mainsock.accept()

        if relayType == 'c':
            Relay(relayType, clientSock, clientInfo, targetRelay=targetRelay, targetRelayPort=targetRelayPort)
        else:
            Relay(relayType, clientSock, clientInfo)
