# UAVDataTrafficGenerator 

UAVDataTrafficGenerator is a UAV-RC data traffic generation tool based on the data distribution models derived from experimental UAV measurements. It is the outcome of our paper *[Experimental Data Traffic Modeling and Network Performance Analysis of UAVs]()*, which is presented at *[xxx]()*. 

## Dependencies
**Python3**
> sudo apt install python3-dev python3-pip

**Keyboard, matplotlib, numpy and scapy libraries**
> pip3 install keyboard matplotlib numpy scapy 

## Usage
**Run the program**
> python3 generatetraffic.py

Select the wireless channel, [d] or [u], you want to produce traffic for, press [Enter] to start and to stop the traffic generation. 
For more information regarding the traffic models, please refer to our paper.

## Results
Generated results are saved in the folder *outputfiles/*:
- **.csv**: Statistical results in terms of packet inter-arrival, packet length and data rate
- **.pcap**: The record of the generated packets
- **.pdf**: The distribution graphs of the statistics in *.csv* file

## uav_datatraces/
Sample UDP data traffic, which are collected during measurements with UAVs (DJI Spark, DJI Mavic and Parrot AR 2.0) are provided.

## Copyright
This code is licensed under GNU General Public License v3.0. For further information, please refer to [LICENSE](LICENSE)