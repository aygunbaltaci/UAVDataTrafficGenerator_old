# UAVDataTrafficGenerator 

UAVDataTrafficGenerator is a set of tool to simulate the data traffic between UAV-RC based on the data distribution models derived from experimental UAV measurements. It is the outcome of our paper *Experimental Data Traffic Modeling and Network Performance Analysis of UAVs*, which is presented at *xxx*. 

## Dependencies
**Python3**
> sudo apt install python3-dev python3-pip

**Keyboard, numpy and scapy libraries**
> pip3 install keyboard numpy scapy 

## Usage
**Run the program**
> python3 generatetraffic.py

Select the wireless channel you want to produce traffic for, press [enter] to start and to stop the traffic generation. 
For more information regarding the traffic models, please refer to our study here.

## Results
Generated results are saved in the folder *outputfiles*:
- **.csv**: Statistical results in terms of packet inter-arrival, packet length and data rate
- **.pcap**: The record of the generated packets
- **.pdf**: The distribution graphs of the statistics in *.csv* file

## Copyright
This code is licensed under GNU General Public License v3.0. For further information, please refer to [LICENSE](LICENSE)