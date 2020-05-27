#!/usr/bin/env python3

#####################################################
# 25.05.2020
#
# This code generates UAV data traffic according to
# distribution models based on actual UAV data. 
# 
# Prerequisites: pip3 install keyboard numpy scapy
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

# ======== variables - modify them as you wish =========
outputfolder = "outputfiles"
ip_source = "10.0.0.201" 
ip_destination = "10.0.0.208" 
port_source = 47813 
port_destination = 47814
pkt_length_maximum = 1486
date = datetime.now().strftime('%Y%m%d_%H%M%S')
# ========================================
# Frequencies of data generation. 
# Each number corresponds to in how many CPU 
# cycles the parameter is generated.
# ========================================
# downlink
frequency_buffer = 3 
frequency_camera_control_record_video = 7 
frequency_land_takeoff = 3
frequency_pitch_roll = 2
frequency_return_home_trim = 5
frequency_throttle_yaw = 1
# uplink
frequency_batterystatus_camerastatus = 6
frequency_buffer = 3
frequency_imustatus_rotorstatus = 2
frequency_video = 1

def pkt_create(payload):
	pkt = IP() / UDP() / Raw(load = payload)
	pkt[IP].src = ip_source
	pkt[IP].dst = ip_destination
	pkt[UDP].sport = port_source 
	pkt[UDP].dport = port_destination
	return pkt

def generate_stats(datarate, firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous):
	time_difference = float(pkt.time - time_previous) * 1000 if time_previous != 0 else 0 # multiply by 1000 to convert into ms
	pkt_interarrival.append(time_difference)
	pkt_length.append(len(pkt))
	if int(time_previous) != int(pkt.time): # divide by 100 to convert into sec
		if not firstrun: datarate.append(pkt_length_total * 8 / 1000) # multiply by 8 to convert bytes to bits, divide by 1000 to convert into kbps
		pkt_length_total = 0
		firstrun = False
	else:
		datarate.append("")
	pkt_length_total += len(pkt)	
	pkt_list.append(pkt) # list_pkt are the generated packets to be sent to the MAC layer for transmission
	time_previous = pkt.time
	return datarate, firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous

# ======== MAIN
def main():
	buffer = ''
	pkt_list, pkt_interarrival, pkt_length, pkt_previous, datarate = [], [], [], [], []
	i, time_previous, pkt_length_total = 0, 0, 0
	downlink, uplink = False, False

	# ask user for which channel to generate data
	while True: 
		user_input = input("Select channel. Enter [d] for downlink (UAV -> RC) and [u] for uplink (RC -> UAV).\n")
		if user_input in ['d', 'D']:
			downlink = True
			filename_extension = '_downlink'
			break
		elif user_input in ['u', 'U']:
			uplink = True
			filename_extension = '_uplink'
			break
		else:
			print("Your input is NOT valid.")

	print("\nPress [Enter] to start/end traffic generation.\n")
	while True: 
		if keyboard.is_pressed('\n'):
			time.sleep(1) # sleep a second to avoid multiple press of Enter
			break 

	firstrun = True
	# main loop
	while True:
		# APPLICATION LAYER. Generate data based on the application
		if downlink:
			# control data
			camera_control = 'c' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
			land = 't' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
			pitch = 'r' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
			return_home = 'h' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
			record_video = 'c' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
			roll = 'r' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
			takeoff = 't' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6]) 
			throttle =  'l' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
			trim = 'h' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
			yaw =  'l' * np.random.choice([2**1, 2**2, 2**3, 2**4, 2**5, 2**6])
			
			# add data to UDP buffer
			if i % frequency_throttle_yaw == 0:
				buffer += (throttle)
				buffer += (yaw)
			if i % frequency_pitch_roll == 0:
				buffer += (pitch)
				buffer += (roll)
			if i % frequency_land_takeoff == 0:
				buffer += (land)
				buffer += (takeoff)
			if i % frequency_return_home_trim == 0:
				buffer += (return_home)
				buffer += (trim)
			if i % frequency_camera_control_record_video == 0:
				buffer += (camera_control)
				buffer += (record_video)
		else:
			# telemetry data
			rotorstatus = 'o' * np.random.choice([2**5, 2**6, 2**7])
			camerastatus = 'm' * np.random.choice([2**5, 2**6, 2**7])
			batterystatus =  'b' * np.random.choice([2**5, 2**6, 2**7])
			imustatus = 'i' * np.random.choice([2**5, 2**6, 2**7])

			# video data
			video = 'v' * int(np.random.uniform(5000, 8000)) # range is based on the actual measured video data from DJI Spark

			# add data to UDP buffer
			if i % frequency_video == 0:
				buffer += (video)
			if i % frequency_imustatus_rotorstatus == 0:
				buffer += (rotorstatus)
				buffer += (imustatus)
			if i % frequency_batterystatus_camerastatus == 0:
				buffer += (camerastatus)
				buffer += (batterystatus)
		
		# UDP LAYER. Check the UDP buffer and generate packets
		if i % frequency_buffer == 0: 
				j, k = 0, 0

				buffer_length = len(buffer)
				while True:
					if (downlink and (k == len(buffer) or len(buffer) == 0)) or (uplink and (j == math.ceil(buffer_length / pkt_length_maximum))):
						break
					delayProb = np.random.uniform(0, 1)
					
					#if buffer[len(buffer) - 1 - k] == 't' and buffer[len(buffer) - 2 - k] != 't':
					if (downlink and (buffer[len(buffer) - 1 - k] != buffer[len(buffer) - 2 - k])) or uplink:
						if delayProb > 0.8:
							time_sleep = np.random.uniform(0, frequency_buffer / 10)
							time.sleep(time_sleep)

					if downlink and (buffer[len(buffer) - 1 - k] != buffer[len(buffer) - 2 - k]):
						pkt = pkt_create(buffer[len(buffer) - 1 - k:]) # add UDP and IP headers
						buffer = buffer[:len(buffer) - 1 - k]
						datarate, firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous = generate_stats(datarate, 
								firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous)
						k = 0
					elif downlink: 
						k += 1
					elif uplink:
						pkt = pkt_create(buffer[len(buffer) - 1 - pkt_length_maximum:]) # add UDP and IP headers
						buffer = buffer[:len(buffer) - 1 - pkt_length_maximum]
						datarate, firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous = generate_stats(datarate, 
								firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous)
						j += 1
				print("Num of gen. pkts: %d" %len(pkt_interarrival))
		i += 1
		
		if keyboard.is_pressed('\n'):
			break
		time.sleep(0.1)
	
	# save pkts to a pcap file
	wrpcap(outputfolder + os.sep + date + filename_extension + '.pcap', pkt_list)
	# save stats to a csv file
	with open(outputfolder + os.sep + date + filename_extension + '.csv', 'w') as outputfile: 
		outputfile.write("{}, {}, {}\n".format("Packet Inter-arrival (ms)", "Packet Length (bytes)", "Data Rate (kbps)"))
		for x in zip(pkt_interarrival, pkt_length, datarate):
			outputfile.write("{}, {}, {}\n".format(x[0], x[1], x[2]))
	print("Packet generation is completed!")

main()