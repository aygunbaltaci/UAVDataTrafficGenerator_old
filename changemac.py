#!/usr/bin/env python3

from scapy.all import *
from scapy.utils import rdpcap

inputfile = 'dji_mavicair.pcap'
inputfile_dir = 'uav_datatraces'
outputfile = 'output_mac.pcap'
outputfile_dir = 'outputfiles'

def main():
    pkts_modified = []
    pkts = rdpcap(inputfile_dir + os.sep + inputfile)
    for pkt in pkts: 
        #src = pkt[Ether].src
        #pkt[Ether].src = src
        pkt[Ether].dst = '00:00:00:00:00:00'
        pkt[Ether].src = '00:00:00:00:00:00'
        #print(pkt[Ether].src)
        
        # if UDP in pkt:
        #     pkt[UDP].remove_payload()
        # elif TCP in pkt:
        #     pkt[TCP].remove_payload()
        # elif ICMP in pkt:
        #     pkt[ICMP].remove_payload()

        pkts_modified.append(pkt)

    wrpcap(outputfile_dir + os.sep + outputfile, pkts_modified)

main()
