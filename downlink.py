#!/usr/bin/env python3

#####################################################
# 25.05.2020
#
# This code generates UAV data traffic for
# downlink channel (from UAV to remote controller).
#  
# Author: Aygün Baltaci
# Institution: Technical University of Munich
#
# Licence: 
#
#####################################################

from scapy.all import *
from scapy.utils import rdpcap
import time
from datetime import datetime
import math
import msvcrt
import numpy as np

# ======== variables
inputFileName = "straightAscend_flight1_downlink_cut.pcap"
outputfolder = "outputfiles"
srcIP = "10.0.0.201" # !!! UPDATE !!! UPDATE THIS LINE EVERYTIME CLIENT HAS NEW IP !!! OTHERWISE, PACKETS MAY NOT REACH TO SERVER SIDE.
dstIP = "10.0.0.208" # !!! UPDATE !!! IP addr of server
srcPort = 47813 # UDP port at client
dstPort = 47811 # UDP port at server
date = datetime.now().strftime('%Y%m%d_%H%M%S')
buffercheck_frequency = 3

def pkt_addLayers(pkt):
	pkt = UDP()/pkt
	pkt = IP()/pkt # 13082019
	pkt.time = time.time() * 100
	pkt[IP].src = srcIP
	pkt[IP].dst = dstIP
	pkt[UDP].sport = srcPort # Add a src port #
	
	return pkt

# ======== MAIN
def main():
	buffer, pkt = '', ''
	pktList, pktTime, pktLen, prevPkt, dataRate = [], [], [], [], []
	i, prevTime, totalPktLen = 0, 0, 0
	cameraControl = 'c' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
	land = 'l' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
	takeOff = 'a' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6]) 
	throttle =  't' * 1 + 'r' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
	pitch = 'p' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])


	while True:
		if i % 1 == 0:
			buffer += (throttle)
		if i % 2 == 0:
			buffer += (pitch)
		if i % 3 == 0:
			buffer += (land)
		if i % 5 == 0:
			buffer += (takeOff)
		if i % 7 == 0:
			buffer += (cameraControl)
		
		if i % buffercheck_frequency == 0: # (not throttle is None or not pitch is None or cameraControl) and 
				k = 0
				while True:
					if k == len(buffer) or len(buffer) == 0:
						break
					delayProb = np.random.uniform(0, 1)
					
					#if buffer[len(buffer) - 1 - k] == 't' and buffer[len(buffer) - 2 - k] != 't':
					if buffer[len(buffer) - 1 - k] != buffer[len(buffer) - 2 - k]:
						if delayProb > 0.8:
							sleepTime = np.random.uniform(0, buffercheck_frequency / 10)
							time.sleep(sleepTime)

						pkt = buffer[len(buffer) - 1 - k:]
						buffer = buffer[:len(buffer) - 1 - k]
						pkt = pkt_addLayers(pkt)
						timeDiff = float(pkt.time - prevTime) * 10 if prevTime != 0 else 0 # multiply by 10 to convert into ms
						pktTime.append(timeDiff)
						pktLen.append(len(pkt))
						if int(prevTime / 100) != int(pkt.time / 100): # divide by 100 to convert into sec
							#print(int(prevTime / 100), int(pkt.time / 100))
							dataRate.append(totalPktLen * 8) # multiply by 8 to convert bytes to bits, divide by 1000 to convert into kbps
							totalPktLen = 0
						else:
							dataRate.append("")
						totalPktLen += len(pkt)	
						pktList.append(pkt)
						prevTime = pkt.time
						k = 0
					else: 
						k += 1
				print("Num of gen. pkts: %d" %len(pktTime))
		i += 1
		
		with open(outputfolder + os.sep + date + '.csv', 'w') as outputFile:
			outputFile.write("{}, {}, {}\n".format("Packet Inter-arrival (ms)", "Packet Length (bytes)", "Data Rate (kbps)"))
			for x in zip(pktTime, pktLen, dataRate):
				outputFile.write("{}, {}, {}\n".format(x[0], x[1], x[2]))
		
		if msvcrt.kbhit():
			break
		time.sleep(0.1)

	#wrpcap(outputFileName, pktList)
	print("Packet generation is completed!")

main()

############## USEFUL COMMANDS
'''
tcpreplay at client: sudo tcpreplay -q --preload-pcap -i cscotun0 straightAscend_flight1_downlink_scapyModified.pcap
tcpdump at client: sudo tcpdump -i cscotun0 -n udp port 2399 -vv -X -w test.pcap
tcpdump at server: sudo tcpdump -i 1 -n udp port 2399 -vv -X -w test3.pcap
scp at server: sudo scp test3.pcap ubuntulaptop@129.187.212.33:
increase mtu at client: sudo ifconfig cscotun0 mtu 1500
OTHER USEFUL SCAPY COMMANDS
print(pkt.summary()+"\n") # Print the layers of a packet
REMOVING A LAYER (IPv6ExtHdrRouting) FROM A PACKET, taken from https://stackoverflow.com/questions/46876196/how-to-remove-a-layer-from-a-packet-in-python-using-scapy
#pkt=IPv6()/IPv6ExtHdrRouting()/ICMPv6EchoRequest()
#pkt2=pkt[ICMPv6EchoRequest]
#pkt[IPv6].remove_payload()
#pkt /=pkt2
Generate packet from raw bytes: https://stackoverflow.com/questions/27262291/how-to-create-a-scapy-packet-from-raw-bytes
'''