#!/usr/bin/env python3

from scapy.all import *
from scapy.utils import rdpcap

inputfile = 'output_mac.pcap'
inputfile_dir = 'outputfiles'
outputfile = 'output_payload.pcap'
outputfile_dir = 'outputfiles'

def main():
    pkts_modified = []
    pkts = rdpcap(inputfile_dir + os.sep + inputfile)
    for pkt in pkts:   
        if UDP in pkt:
            pkt[UDP].remove_payload()
        elif TCP in pkt:
            pkt[TCP].remove_payload()
        elif ICMP in pkt:
            pkt[ICMP].remove_payload()
        pkts_modified.append(pkt)

    wrpcap(outputfile_dir + os.sep + outputfile, pkts_modified)

main()
