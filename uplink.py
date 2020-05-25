#!/usr/bin/env python3

#####################################################
# 25.05.2020
# 
# This code generates UAV data traffic for
# uplink channel (from remote controller to UAV).
# 
# Prerequisites: pip3 install msvcrt numpy scapy
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
import keyboard
import time
import numpy as np

# ======== variables
outputfolder = "outputfiles"
ip_source = "10.0.0.201" 
ip_destination = "10.0.0.208" 
port_source = 47813 
date = datetime.now().strftime('%Y%m%d_%H%M%S')
buffercheck_frequency = 3 # in how many CPU cycles the buffer to be checked

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
	
	
	maxPktLen = 1486

	while True:
		rotorstatus = 'r' * int(np.random.uniform(25, 125))
		camerastatus = 'v' * int(np.random.uniform(25, 125)) 
		batterystatus =  'b' * int(np.random.uniform(25, 125))
		imustatus = 'i' * int(np.random.uniform(25, 125))
		videoInformation = 'v' * int(np.random.uniform(5000, 8000))
		if i % 1 == 0:
			buffer += (videoInformation)
		if i % 2 == 0:
			buffer += (rotorstatus)
			buffer += (imustatus)
		if i % 6 == 0:
			buffer += (camerastatus)
			buffer += (batterystatus)
		
		if i % buffercheck_frequency == 0: # (not throttle is None or not pitch is None or cameraControl) and 
			k = 0
				
			for j in range(math.ceil(len(buffer) / maxPktLen)):
				delayProb = np.random.uniform(0, 1)
				if delayProb > 0.8:
					sleepTime = np.random.uniform(0, buffercheck_frequency / 10)
					time.sleep(sleepTime)

				time.sleep(0.1) # TODO need this? 
					
				pkt = buffer[len(buffer) - 1 - maxPktLen:]
				buffer = buffer[:len(buffer) - 1 - maxPktLen]
				pkt = pkt_addLayers(pkt)
				timeDiff = float(pkt.time - prevTime) if prevTime != 0 else 0
				pktTime.append(timeDiff)
				pktLen.append(len(pkt))
				if int(prevTime / 100) != int(pkt.time / 100):
					#print(int(prevTime / 100), int(pkt.time / 100))
					dataRate.append(totalPktLen * 8) # multiply by 8 to convert bytes to bits
					totalPktLen = 0
				else:
					dataRate.append("")
				totalPktLen += len(pkt)	
				pktList.append(pkt)
				prevTime = pkt.time
			print("Num of gen. pkts: %d" %len(pktTime))
		i += 1
		
		with open(outputfolder + os.sep + date + '.csv', 'w') as outputFile:
			outputFile.write("{}, {}, {}\n".format("Packet Inter-arrival (ms)", "Packet Length (bytes)", "Data Rate (bps)"))
			for x in zip(pktTime, pktLen, dataRate):
				outputFile.write("{}, {}, {}\n".format(x[0], x[1], x[2]))
		
		if msvcrt.kbhit():
			break
		time.sleep(0.1)

	print("Packet generation is completed!")

main()
