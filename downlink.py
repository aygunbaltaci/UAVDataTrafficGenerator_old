#!/usr/bin/env python3

#####################################################
# 25.05.2020
#
# This code generates UAV data traffic for
# downlink channel (from UAV to remote controller).
# 
# Prerequisites: pip3 install msvcrt numpy scapy
#
# Author: Aygün Baltaci
# Institution: Technical University of Munich
#
# License: 
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

def pkt_create(payload):
	pkt = IP() / UDP() / Raw(load = payload)
	#pkt = pkt
	pkt.time = time.time() * 100
	pkt[IP].src = ip_source
	pkt[IP].dst = ip_destination
	pkt[UDP].sport = port_source # Add a src port #
	return pkt

# ======== MAIN
def main():
	buffer = ''
	pkt_list, pktTime, pktLen, prevPkt, dataRate = [], [], [], [], []
	i, prevTime, totalPktLen = 0, 0, 0
	
	# frequencies of data generation. Each number corresponds to in how many CPU cycles the parameter is generated
	frequency_buffer = 3 
	frequency_camera_control = 7 
	frequency_land = 3
	frequency_pitch = 2
	frequency_takeoff = 5 
	frequency_throttle = 1 

	# control commands
	camera_control = 'c' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
	land = 'l' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
	takeoff = 'a' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6]) 
	throttle =  't' * 1 + 'r' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
	pitch = 'p' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])

	print("\nPress [Enter] to start/end traffic generation.\n")
	while True: 
		if keyboard.is_pressed('\n'):
			time.sleep(1) # sleep a second to avoid multiple press of Enter
			break 

	firstrun = True
	# main loop
	while True:
		# APPLICATION LAYER. Generate data based on the application
		if i % frequency_throttle == 0:
			buffer += (throttle)
		if i % frequency_pitch == 0:
			buffer += (pitch)
		if i % frequency_land == 0:
			buffer += (land)
		if i % frequency_takeoff == 0:
			buffer += (takeoff)
		if i % frequency_camera_control == 0:
			buffer += (camera_control)
		
		# UDP LAYER. Check the UDP buffer and generate packets
		if i % frequency_buffer == 0: 
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

						pkt = pkt_create(buffer[len(buffer) - 1 - k:]) # add UDP and IP headers
						buffer = buffer[:len(buffer) - 1 - k]
						timeDiff = float(pkt.time - prevTime) * 10 if prevTime != 0 else 0 # multiply by 10 to convert into ms
						pktTime.append(timeDiff)
						pktLen.append(len(pkt))
						if int(prevTime / 100) != int(pkt.time / 100): # divide by 100 to convert into sec
							if not firstrun: dataRate.append(totalPktLen * 8 / 1000) # multiply by 8 to convert bytes to bits, divide by 1000 to convert into kbps
							totalPktLen = 0
							firstrun = False
						else:
							dataRate.append("")
						totalPktLen += len(pkt)	
						print(pkt.show())
						pkt_list.append(pkt) # list_pkt are the generated packets to be sent to the MAC layer for transmission
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
		
		if keyboard.is_pressed('\n'):
			break
		time.sleep(0.1)
	
	wrpcap(outputfolder + os.sep + date + '.pcap', pkt_list)
	print("Packet generation is completed!")

main()