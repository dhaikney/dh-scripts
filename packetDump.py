#!/usr/bin/env python2.6

import dpkt
import sys
import socket, struct
from pprint import pprint

if len(sys.argv) != 2:
        print "Usage: " + sys.argv[0] + "  PCAP Filename"
        sys.exit()

filename = sys.argv[1]


f = open(filename)
pcap = dpkt.pcap.Reader(f)

for ts, buf in pcap:
    eth = dpkt.ethernet.Ethernet(buf)
    ip = eth.data
    tcp = ip.data
    if hasattr(tcp, 'sport'):
        if tcp.sport == 11210:
            print "DEST: {0}.{1}.{2}.{3}".format(ord(ip.dst[0]),ord(ip.dst[1]),ord(ip.dst[2]),ord(ip.dst[3]))
            print tcp.data
f.close()
