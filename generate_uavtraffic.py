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
import matplotlib
import matplotlib.pyplot as plt
import keyboard
import time
import numpy as np
import config_matplotlibrc

# ======== variables - modify them as you wish =========
date = datetime.now().strftime('%Y%m%d_%H%M%S')

# graph-related
figure_dimensions = (25.6, 14.4)
figure_format = 'pdf'
label_x = ['Data Rate (kbps)', 'Packet Inter-arrival (ms)', 'Packet Length (bytes)']
label_y = 'Density'
legend = 'Simulated data'
legend_location = (0.5, 0.05)
numofbins = [15, 15, 10] # recommended for dl: [25, 25, 10], for ul: []
xticks = [np.arange(2, 11, 2), np.arange(0, 601, 200), np.arange(0, 201, 50)] # recommended for dl: [np.arange(2, 11, 2), np.arange(0, 601, 200), np.arange(0, 201, 50)], recommended for ul: [np.arange(0, 351, 50), np.arange(0, 601, 200), np.arange(0, 1551, 250)]
title = 'Downlink'
transparency = 0.65

# outputfiles-related
outputfile_packets_extension = 'pcap'
outputfile_statistics_extension = 'csv'
outputfile_statistics_headernames = ['Packet Inter-arrival (ms)', 'Packet Length (bytes)', 'Data Rate (kbps)']
outputfolder = 'outputfiles'

# packet-related 
ip_source = '10.0.0.201'
ip_destination = '10.0.0.208'
pkt_length_maximum = 1486
port_source = 47813 
port_destination = 47814

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

# ======== Ask user for which channel to generate data
def ask_channel(downlink, uplink):
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
	return downlink, filename_extension, uplink

# ======== Send downlink data to UDP buffer
def data_to_buffer_downlink(buffer, camera_control, i, land, pitch, return_home, 
		record_video, roll, takeoff, throttle, trim, yaw):
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
	return buffer

# ======== Send uplink data to UDP buffer
def data_to_buffer_uplink(batterystatus, buffer, camerastatus, 
				i, imustatus, rotorstatus, video):
	# add data to UDP buffer
	if i % frequency_video == 0:
		buffer += (video)
	if i % frequency_imustatus_rotorstatus == 0:
		buffer += (rotorstatus)
		buffer += (imustatus)
	if i % frequency_batterystatus_camerastatus == 0:
		buffer += (camerastatus)
		buffer += (batterystatus)
	return buffer

# ======== Generate data for downlink channel
def generate_data_downlink():
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
	return camera_control, land, pitch, return_home, record_video, roll, takeoff, throttle, trim, yaw

# ======== Generate data for uplink channel
def generate_data_uplink():
	# telemetry data
	batterystatus =  'b' * np.random.choice([2**5, 2**6, 2**7])
	camerastatus = 'm' * np.random.choice([2**5, 2**6, 2**7])
	imustatus = 'i' * np.random.choice([2**5, 2**6, 2**7])
	rotorstatus = 'o' * np.random.choice([2**5, 2**6, 2**7])

	# video data
	video = 'v' * int(np.random.uniform(5000, 8000)) # range is based on the actual measured video data from DJI Spark
	return batterystatus, camerastatus, imustatus, rotorstatus, video

# ======== Generate distribution graphs
def graph_generate(datarate, downlink, filename_extension, pkt_interarrival, pkt_length):
	cnt = 0
	fig, host = prepare_graph()
	datarate = list(filter(None, datarate)) # remove empty entries
	for i in [datarate, pkt_interarrival, pkt_length]:
		host[0, cnt] = histogram(numofbins[cnt], i, label_x[cnt], label_y, host[0, cnt], xticks[cnt])
		cnt += 1
	return fig

# ======== Generate histogram plot
def histogram(bins, data, label_x, label_y, plot, xticks):
	plot.hist(
			data,
			bins = bins,
			color = 'steelblue',
			edgecolor = 'dimgrey',
			density = True,
			bottom = 0,
			align = 'left',
			label = legend,
			orientation = 'vertical', 
			alpha = transparency)
	plot.set_xlabel(label_x)
	plot.set_ylabel(label_y)
	ticks_start, ticks_end = plot.get_xlim()
	round_distance = int((ticks_end - ticks_start) / 5)
	plot.xaxis.set_ticks(np.arange(round_up(ticks_start, round_distance), round_up(ticks_end, round_distance), round_distance))
	return plot

# ======== Application layer - Generate data based on the applications
def layer_application(buffer, downlink, i, uplink):
	if downlink:
		camera_control, land, pitch, return_home, record_video, roll, takeoff, throttle, trim, yaw = generate_data_downlink()
		buffer = data_to_buffer_downlink(buffer, camera_control, i,
				land, pitch, return_home, record_video, roll, takeoff, throttle, trim, yaw)
	else:
		batterystatus, camerastatus, imustatus, rotorstatus, video = generate_data_uplink()
		buffer = data_to_buffer_uplink(batterystatus, buffer, camerastatus, i,
				imustatus, rotorstatus, video)
	return buffer

# ======== Transport layer - Check the UDP buffer and generate packets
def layer_transport(buffer, datarate, downlink, firstrun, i, 
		pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous, uplink):
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
					datarate, firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous = statistics_results(datarate, 
							firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous)
					k = 0
				elif downlink: 
					k += 1
				elif uplink:
					pkt = pkt_create(buffer[len(buffer) - 1 - pkt_length_maximum:]) # add UDP and IP headers
					buffer = buffer[:len(buffer) - 1 - pkt_length_maximum]
					datarate, firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous = statistics_results(datarate, 
							firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous)
					j += 1
			print("# of pkts: %d" %len(pkt_interarrival))
	return buffer, datarate, firstrun, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous

# ======== Main function
def main():
	buffer = ''
	pkt_list, pkt_interarrival, pkt_length, pkt_previous, datarate = [], [], [], [], []
	i, time_previous, pkt_length_total = 0, 0, 0
	downlink, uplink = False, False

	downlink, filename_extension, uplink = ask_channel(downlink, uplink)
	time.sleep(0.5) # sleep half a second to avoid multiple press of Enter
	firstrun = True
	# main loop
	while True:
		buffer = layer_application(buffer, downlink, i, uplink)
		buffer, datarate, firstrun, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous = layer_transport(
				buffer, datarate, downlink, firstrun, i, pkt_interarrival, pkt_length, 
				pkt_length_total, pkt_list, time_previous, uplink)
		i += 1
		if keyboard.is_pressed('\n'):
			break
		time.sleep(0.1)
	print("\nPacket generation is completed!\nGraph is being prepared, please hold on...")
	
	fig = graph_generate(datarate, downlink, filename_extension, pkt_interarrival, pkt_length)
	save_output(datarate, fig, filename_extension, pkt_interarrival, pkt_length, pkt_list)
	show_graph()
	

# ======== Create packet
def pkt_create(payload):
	pkt = IP() / UDP() / Raw(load = payload)
	pkt[IP].src = ip_source
	pkt[IP].dst = ip_destination
	pkt[UDP].sport = port_source 
	pkt[UDP].dport = port_destination
	return pkt

# ======== Prepare subplots
def prepare_graph(): 
	plt.rcParams.update(config_matplotlibrc.parameters)
	fig, host = plt.subplots(
			1,  
			3,  
			figsize = figure_dimensions, 
			squeeze = False)
	return fig, host

# ======== Round up the input to the nearest base. Taken from: https://stackoverflow.com/questions/26454649/python-round-up-to-the-nearest-ten 
def round_up(x, base):
    return int(math.ceil(x / base)) * base

# ======== Save all output files
def save_output(datarate, fig, filename_extension, pkt_interarrival, pkt_length, pkt_list):
	save_graph(fig, filename_extension)
	save_packets(filename_extension, pkt_list)
	save_statistics(datarate, filename_extension, pkt_interarrival, pkt_length)

# ======== Save generated packets to a pcap file
def save_packets(filename_extension, pkt_list):
	wrpcap(outputfolder + os.sep + date + filename_extension + '.' + outputfile_packets_extension, pkt_list)

# ======== Save statistical results to a csv file
def save_statistics(datarate, filename_extension, pkt_interarrival, pkt_length):
	with open(outputfolder + os.sep + date + filename_extension + '.' + outputfile_statistics_extension, 'w') as outputfile: 
		outputfile.write("{}, {}, {}\n".format("Packet Inter-arrival (ms)", "Packet Length (bytes)", "Data Rate (kbps)"))
		for x in zip(pkt_interarrival, pkt_length, datarate):
			outputfile.write("{}, {}, {}\n".format(x[0], x[1], x[2]))

# ======== Save graph
def save_graph(fig, filename_extension):
	handles, labels = plt.gca().get_legend_handles_labels() # to avoid duplicate labels. Taken from: https://stackoverflow.com/questions/13588920/stop-matplotlib-repeating-labels-in-legend
	by_label = dict(zip(labels, handles))
	fig.legend(
			by_label.values(),
			by_label.keys(), 
			bbox_to_anchor = legend_location)
	fig.suptitle(title)
	fig.savefig(
            '%s' %outputfolder + os.sep + 
            '%s.%s' %(date + filename_extension, figure_format), 
            bbox_inches = 'tight', 
            format = figure_format)

# ======== Show graph
def show_graph():
	plt.show()

# ======== Statistics of the generated data - data rate, packet inter-arrival, packet length
def statistics_results(datarate, firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous):
	time_difference = float(pkt.time - time_previous) * 1000 if time_previous != 0 else 0 # multiply by 1000 to convert into ms
	pkt_interarrival.append(float(time_difference))
	pkt_length.append(int(len(pkt)))
	if int(time_previous) != int(pkt.time): # divide by 100 to convert into sec
		if not firstrun: datarate.append(float(pkt_length_total * 8 / 1000)) # multiply by 8 to convert bytes to bits, divide by 1000 to convert into kbps
		pkt_length_total = 0
		firstrun = False
	else:
		datarate.append(float())
	pkt_length_total += len(pkt)	
	pkt_list.append(pkt) # list_pkt are the generated packets to be sent to the MAC layer for transmission
	time_previous = pkt.time
	return datarate, firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous

main()