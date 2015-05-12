#! /usr/bin/env python
##Controlador simple utilizado para probar el correcto funcionamiento de la conexión

import os, sys
from socket import *
from fcntl import ioctl
from select import select
import getopt, struct

MAGIC_WORD = "asd"
TUNSETIFF = 0x400454ca
IFF_TAP   = 0x0002
TUNMODE = IFF_TAP
ip=["10.0.0.1/24","10.0.0.2/24","10.0.0.3/24"]

##Help function
def usage(status=0):
    print "Usage: simple.py [-p port]"
    sys.exit(status)

##Parsing the arguments
opts = getopt.getopt(sys.argv[1:],"p:h")

for opt,optarg in opts[0]:
    if opt == "-h":
        usage()
    elif opt == "-p":
        PORT = int(optarg)


##Creating the interface
f = os.open("/dev/net/tun", os.O_RDWR)
ifs = ioctl(f, TUNSETIFF, struct.pack("16sH", "tun%d", TUNMODE))
ifname = ifs[:16].strip("\x00")


#Preparing the socket
s = socket(AF_INET, SOCK_DGRAM)

#Establishing conecction with the host
try:
    s.bind(("", PORT))
    while 1:
        word,peer = s.recvfrom(1500)
        if word == MAGIC_WORD:
            break
        print "Bad magic word for %s:%i" % peer
    s.sendto(MAGIC_WORD, peer)
    ##Sending IP to the host's new interface
    s.sendto(ip[0], peer)
    print "Connection with %s:%i established" % peer
    
    while 1:
        r = select([f,s],[],[])[0][0]
        if r == f:
            s.sendto(os.read(f,1500),peer)
        else:
            buf,p = s.recvfrom(1500)
            if p != peer:
                print "Got packet from %s:%i instead of %s:%i" % (p+peer)
                continue
            os.write(f, buf)
except KeyboardInterrupt:
    print "Stopped by user."

