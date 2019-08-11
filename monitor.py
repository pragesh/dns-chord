import sys, string, os
import subprocess
from threading import Timer
import signal
import random
import matplotlib.pyplot as plt
import psutil
from beautifultable import BeautifulTable
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np

#kill distalgo process and its children after a timeout of 15seconds beacause of failure issues
def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()

runType = sys.argv[1] if len(sys.argv) > 1 else "Nodes"
m = (int(sys.argv[2]) ) if len(sys.argv) > 2 else 5
nodes = int(sys.argv[3]) if len(sys.argv) > 3 else 6
r = int(sys.argv[4]) if len(sys.argv) > 4 else 2
queryNo = int(sys.argv[5]) if len(sys.argv) > 5 else 200
stabDelay = float(sys.argv[6]) if len(sys.argv) > 6 else 0.1
fixFingerDelay =float(sys.argv[7]) if len(sys.argv) > 7 else 0.1
predDelay =float(sys.argv[8]) if len(sys.argv) > 8 else 0.1
probFailure = float(sys.argv[9]) if len(sys.argv) > 9 else 0.1

# Java command is different for Unix and Window
javaRunCommand = 'java -cp ./open-chord/.:./open-chord/bin:./open-chord/lib/*:./open-chord/chord.properties:./open-chord/config/* myapp.driver.Driver '

# its win32, maybe there is win64 too?
is_windows = sys.platform.startswith('win')
if is_windows:
	javaRunCommand = 'java -cp ./open-chord/.;./open-chord/bin;./open-chord/lib/*;./open-chord/chord.properties;./open-chord/config/* myapp.driver.Driver '

pythonRunCommand = 'python -m da DriverChanged.da '

file=open("chordRunInfo.txt", "w")
fileTable = open('chordTabularResults.txt', 'w')

if not os.path.exists("Results"):
	os.mkdir("Results")

if os.path.exists("resultDistalgo.txt"):
	os.remove("resultDistalgo.txt")
if os.path.exists("results_java.txt"):
	os.remove("results_java.txt")
run = 1
#################################################################################################################################################################3
#change number of nodes and fix all other parameters
#number of nodes changes from [5 to 10) as our system can't handle more nodes

# The idea to evaluate performance by varying numbe rof nodes is taken from paper : #
########### Farida Chowdhury, Mario Kolberg - Performance Evaluation of Structured Peer-to-Peer
# Overlays for Use on Mobile Networks - 2013 International Conference on Developments in eSystems Engineering (DeSE) #############

if runType == 'Nodes':
	nodes_start = 5
	nodes_end = 10
	print ("\n################## Varying Nodes ###############\n")
	for i in range (nodes_start, nodes_end, 1):
		valuesDistalgo = {}
		valuesJava = {}
		cmd = str(m) + ' ' + str(i) + ' ' + str(r) + ' ' + str(queryNo) + ' ' + str(stabDelay) + ' ' + str(fixFingerDelay) + ' ' + str(predDelay) + ' ' + str(0) + ' ' + str(run)
		print (cmd)
		pythonCmd = pythonRunCommand + cmd
		javacmd =  javaRunCommand + cmd
		
		#Launching  python driver
		
		proc = subprocess.Popen(pythonCmd , shell=True)
		try:
			proc.wait(timeout=100)
		except subprocess.TimeoutExpired:
			kill(proc.pid)
		
	    #Launching java driver
		p2 = subprocess.Popen(javacmd, shell=True)
		while p2.wait():
			pass

		file.write("%s\n" %cmd)
		run += 1
	file.flush()

	###################################################################
	#Read  Data from files for  for performance values

	fileD = open("resultDistalgo.txt", "r");
	fileJ = open("results_java.txt", "r");

	valuesLDistalgo = {}      # stores latency for distalgo
	valuesLJava = {}          # stores latency for java
	valuesHDistalgo = {}      # stores hop count for distalgo
	valuesHJava = {}          # stores hop count for java
	valuesLookupDistalgo = {} # stores lookup success ratio for distalgo
	valuesLookupJava = {}     # stores lookup succes ratio for java
	valuesTJava = {}          # stores timeout ratio for java 
	valuesTDistalgo = {}      #stores timeout ratio for distalgo 
	table = BeautifulTable()

	column_headers = ["Nodes","Java \n HopCount", "Distalgo\n HopCount", "Java \nAverage Latency", "Distalgo\n Average Latency", "Java\n Lookup ratio", "Distalgo\n Lookup ratio","Java Timeout\n ratio", "Distalgo Timeout\n ratio"]

	# Data in results file is in the following format
	#runno  HopCount Latency Lookupratio timeoutratio 
	for i in range(nodes_start, nodes_end, 1):
		line = fileD.readline()
		line = line.rstrip('\n')
		words = line.split(',')
		numbers = []
		for w in words:
			x = float(w)
			numbers.append( x)
		valuesLDistalgo[i] = numbers[2]
		valuesHDistalgo[i] = numbers[1]
		valuesLookupDistalgo[i] = numbers[3]
		valuesTDistalgo[i] = numbers[4]


	for i in range(nodes_start, nodes_end, 1):
		line = fileJ.readline()
		line = line.rstrip('\n')
		words = line.split(',')
		numbers = []
		for w in words:
			x = float(w)
			numbers.append( x)
		valuesLJava[i] = numbers[2]
		valuesHJava[i] = numbers[1]
		valuesLookupJava[i] = numbers[3]
		valuesTJava[i] = numbers[4]

	###################################################################
	#Dump table and plot graphs

	for i in range(nodes_start, nodes_end, 1):
		table.append_row([i,valuesHJava[i], valuesHDistalgo[i], valuesLJava[i], valuesLDistalgo[i], valuesLookupJava[i], valuesLookupDistalgo[i], valuesTJava[i], valuesTDistalgo[i]])

	print (tabulate(table,headers=column_headers))
	fileTable.write("Number of bits : %d, Successor List : %d, Total Number of Queries : %d, Stabilization Delay : %f, Fix Finger Delay : %f, CheckPredecessor Delay : %f, Probalility Failure  : %f\n" %(m, r, queryNo, stabDelay, fixFingerDelay, predDelay, probFailure))
	fileTable.write(tabulate(table,headers=column_headers))
	fileTable.flush()


	#Plot average latency
	plt.figure()
	lists = sorted(valuesLJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesLDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Nodes')
	plt.ylabel('Average Latency')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Latency_Nodes.png'
	plt.savefig(filename)

	# plot hopCount
	plt.figure()
	lists = sorted(valuesHJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesHDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Nodes')
	plt.ylabel('HopeCount')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Hope_Nodes.png'
	plt.savefig(filename)

	'''
	# plot lookup success ratio
	plt.figure()
	lists = sorted(valuesLookupJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesLookupDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Nodes')
	plt.ylabel('Lookup Success')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Lookup_Nodes.png'
	plt.savefig(filename)
	file.close()
	fileD.close()
	fileJ.close()
	fileTable.close()
	'''

############################################################################################################################################################
#change probability of failure and fix all other parameters
#probability of failure changes from [0.02 to 0.10) as our system can't handle more nodes
# The idea to evaluate performance by varying probability failure is taken from paper : #
###########Ion Stoica, Robert Morris, David Liben-Nowell, David R. Karger, M. Frans Kaashoek, Frank Dabek, Hari Balakrishnan - Chord:
# A Scalable Peer-to-peer Lookup Protocol for Internet Applications - IEEE/ACM TRANSACTIONS ON NETWORKING, VOL. 11, NO. 1, FEBRUARY 2003 #############

#Values of probability failure 
elif runType == 'Failure':
	permute = [0.02,0.04,0.06,0.08,0.10]
	print ("\n################## Varying Probablity of Failure ###############\n")
	for i in range (0, 5):
		cmd = str(m) + ' ' + str(nodes) + ' ' + str(r) + ' ' + str(queryNo) + ' ' + str(stabDelay) + ' ' + str(fixFingerDelay) + ' ' + str(predDelay) + ' ' + str(permute[i]) + ' ' + str(run)
		print (cmd)
		pythonCmd = pythonRunCommand + cmd
		javacmd = javaRunCommand + cmd

	    #Launching  python driver
		proc = subprocess.Popen(pythonCmd , shell=True)
		try:
			proc.wait(timeout=100)
		except subprocess.TimeoutExpired:
			kill(proc.pid)

		#Launching  java driver
		p2 = subprocess.Popen(javacmd, shell=True)
		while p2.wait():
			pass
		file.write("%s\n" %cmd)
		run += 1
	file.flush()

	###################################################################
	#Read  Data from files for  for performance values

	fileD = open("resultDistalgo.txt", "r");
	fileJ = open("results_java.txt", "r");

	valuesLDistalgo = {}      # stores latency for distalgo
	valuesLJava = {}          # stores latency for java
	valuesHDistalgo = {}      # stores hop count for distalgo
	valuesHJava = {}          # stores hop count for java
	valuesLookupDistalgo = {} # stores lookup success ratio for distalgo
	valuesLookupJava = {}     # stores lookup succes ratio for java
	valuesTJava = {}          # stores timeout ratio for java 
	valuesTDistalgo = {}      #stores timeout ratio for distalgo 
	table = BeautifulTable()

	column_headers = ["Failure \nProbability","Java \nHopCount", "Distalgo\n HopCount", "Java Average\n Latency", "Distalgo Average\n Latency", "Java Lookup\n ratio", "Distalgo Lookup\n ratio","Java Timeout\n ratio", "Distalgo Timeout\n ratio"]

	for i in range(0,5):
		line = fileD.readline()
		line = line.rstrip('\n')
		words = line.split(',')
		numbers = []
		for w in words:
			x = float(w)
			numbers.append( x)
		valuesLDistalgo[permute[i]] = numbers[2]
		valuesHDistalgo[permute[i]] = numbers[1]
		valuesLookupDistalgo[permute[i]] = numbers[3]
		valuesTDistalgo[permute[i]] = numbers[4]


	for i in range(0,5):
		line = fileJ.readline()
		line = line.rstrip('\n')
		words = line.split(',')
		numbers = []
		for w in words:
			x = float(w)
			numbers.append( x)
		valuesLJava[permute[i]] = numbers[2]
		valuesHJava[permute[i]] = numbers[1]
		valuesLookupJava[permute[i]] = numbers[3]
		valuesTJava[permute[i]] = numbers[4]

	###################################################################
	#Dump table and plot graph

	for j in range(0, 5):
		i = permute[j]
		table.append_row([i,valuesHJava[i], valuesHDistalgo[i], valuesLJava[i], valuesLDistalgo[i], valuesLookupJava[i], valuesLookupDistalgo[i], valuesTJava[i], valuesTDistalgo[i]])

	print(tabulate(table,headers=column_headers))
	fileTable.write("Number of bits : %d, Number of Nodes : %d, Successor List : %d, Total Number of Queries : %d, Stabilization Delay : %f, Fix Finger Delay : %f, CheckPredecessor Delay : %f\n" %(m, nodes, r, queryNo, stabDelay, fixFingerDelay, predDelay))
	fileTable.write(tabulate(table,headers=column_headers))
	fileTable.flush()

	#Plot average latency
	plt.figure()
	lists = sorted(valuesLJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesLDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Failure Probablity')
	plt.ylabel('Average Latency')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Latency_Failure.png'
	plt.savefig(filename)

	# plot hopCount
	plt.figure()
	lists = sorted(valuesHJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesHDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Failure Probablity')
	plt.ylabel('HopeCount')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Hope_Failure.png'
	plt.savefig(filename)

	# plot lookup success ratio
	plt.figure()
	lists = sorted(valuesLookupJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesLookupDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Failure ')
	plt.ylabel('Lookup Success Ratio')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Lookup_Failure.png'
	plt.savefig(filename)

	# plot timeout ratio
	plt.figure()
	lists = sorted(valuesTJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesTDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Failure ')
	plt.ylabel('TimeOut Ratio')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Time_Out_Failure.png'
	plt.savefig(filename)

	file.close()
	fileD.close()
	fileJ.close()
	fileTable.close()

######################################################################################################################################################
#change stabilization delay and fix all other parameters
#stabilization delay changes from [0.1 to 0.5) 
# The idea to evaluate performance by varying stabilization delay is taken from paper : #
########### Farida Chowdhury, Mario Kolberg - Performance Evaluation of Structured Peer-to-Peer
# Overlays for Use on Mobile Networks - 2013 International Conference on Developments in eSystems Engineering (DeSE) #############
#Values of stabilization delay for 5 runs 

elif runType == 'Stabilization_Delay':
	print ("\n################## Varying Stabilization Delay ###############\n")
	permute = [0.1, 0.2, 0.3, 0.4, 0.5]
	for i in range (0, 5):
		cmd = str(m) + ' ' + str(nodes) + ' ' + str(r) + ' ' + str(queryNo) + ' ' + str(permute[i]) + ' ' + str(fixFingerDelay) + ' ' + str(predDelay) + ' ' + str(probFailure) + ' ' + str(run)
		print (cmd)
		pythonCmd = pythonRunCommand + cmd
		javacmd = javaRunCommand + cmd

	    #Launching  python driver
		proc = subprocess.Popen(pythonCmd , shell=True)
		try:
			proc.wait(timeout=100)
		except subprocess.TimeoutExpired:
			kill(proc.pid)

		#Launching  java driver
		p2 = subprocess.Popen(javacmd, shell=True)
		while p2.wait():
			pass
		file.write("%s\n" %cmd)
		run += 1
	file.flush()

	###################################################################
	#Read  Data from files for  for performance values
	fileD = open("resultDistalgo.txt", "r");
	fileJ = open("results_java.txt", "r");

	valuesLDistalgo = {}      # stores latency for distalgo
	valuesLJava = {}          # stores latency for java
	valuesHDistalgo = {}      # stores hop count for distalgo
	valuesHJava = {}          # stores hop count for java
	valuesLookupDistalgo = {} # stores lookup success ratio for distalgo
	valuesLookupJava = {}     # stores lookup succes ratio for java
	valuesTJava = {}          # stores timeout ratio for java 
	valuesTDistalgo = {}      #stores timeout ratio for distalgo 
	table = BeautifulTable()

	column_headers = ["Stabilization\n delay","Java\n HopCount", "Distalgo\n HopCount", "Java Average\n Latency", "Distalgo Average\n Latency", "Java Lookup\n ratio", "Distalgo Lookup\n ratio","Java Timeout\n ratio", "Distalgo Timeout\n ratio"]

	for i in range(0,5):
		line = fileD.readline()
		line = line.rstrip('\n')
		words = line.split(',')
		numbers = []
		for w in words:
			x = float(w)
			numbers.append( x)
		valuesLDistalgo[permute[i]] = numbers[2]
		valuesHDistalgo[permute[i]] = numbers[1]
		valuesLookupDistalgo[permute[i]] = numbers[3]
		valuesTDistalgo[permute[i]] = numbers[4]

	for i in range(0,5):
		line = fileJ.readline()
		line = line.rstrip('\n')
		words = line.split(',')
		numbers = []
		for w in words:
			x = float(w)
			numbers.append( x)
		valuesLJava[permute[i]] = numbers[2]
		valuesHJava[permute[i]] = numbers[1]
		valuesLookupJava[permute[i]] = numbers[3]
		valuesTJava[permute[i]] = numbers[4]

	###################################################################
	#Dump table and plot graph

	for j in range(0, 5):
		i = permute[j]
		table.append_row([i,valuesHJava[i], valuesHDistalgo[i], valuesLJava[i], valuesLDistalgo[i], valuesLookupJava[i], valuesLookupDistalgo[i], valuesTJava[i], valuesTDistalgo[i]])

	print(tabulate(table, headers=column_headers))
	fileTable.write("Number of bits : %d, Number of Nodes : %d,  Successor List : %d, Total Number of Queries : %d, Fix Finger Delay : %f, CheckPredecessor Delay : %f, Probability Failure : %f\n" %(m, nodes, r, queryNo, fixFingerDelay, predDelay, probFailure))
	fileTable.write(tabulate(table, headers=column_headers))
	fileTable.flush()

	#Plot average latency
	plt.figure()
	lists = sorted(valuesLJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesLDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Stabilization delay')
	plt.ylabel('Average Latency')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Latency_stab_delay.png'
	plt.savefig(filename)

	# plot hopCount
	plt.figure()
	lists = sorted(valuesHJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesHDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Stabilization delay')
	plt.ylabel('HopeCount')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Hope_stab_delay.png'
	plt.savefig(filename)

	plt.figure()
	lists = sorted(valuesLookupJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesLookupDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Stabilization delay ')
	plt.ylabel('Lookup Success Ratio')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Lookup_stab_delay.png'
	plt.savefig(filename)
	file.flush()

	plt.figure()
	lists = sorted(valuesTJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesTDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Stabilization delay ')
	plt.ylabel('Timeout Ratio')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Timeout_stab_delay.png'
	plt.savefig(filename)
	file.flush()

	file.close()
	fileD.close()
	fileJ.close()
	fileTable.close()



######################################################################################################################################################
#Fix finger delay changes from [0.1 to 0.5]
# The idea to evaluate performance by varying Fix finger delay is taken from paper : #
########### Farida Chowdhury, Mario Kolberg - Performance Evaluation of Structured Peer-to-Peer
# Overlays for Use on Mobile Networks - 2013 International Conference on Developments in eSystems Engineering (DeSE) ############# 
#Values of Fix Finger delay for 5 runs
elif runType == 'FixFinger_Delay':
	print ("\n################## Varying FixFinger_Delay ###############\n")

	permute = [0.1,0.2,0.3,0.4,0.5]

	for i in range (0, 5):
		cmd = str(m) + ' ' + str(nodes) + ' ' + str(r) + ' ' + str(queryNo) + ' ' + str(stabDelay) + ' ' + str(permute[i]) + ' ' + str(predDelay) + ' ' + str(probFailure) + ' ' + str(run)
		print (cmd)
		pythonCmd = pythonRunCommand + cmd
		javacmd = javaRunCommand + cmd

	    #Launching  python driver
		proc = subprocess.Popen(pythonCmd , shell=True)
		try:
			proc.wait(timeout=100)
		except subprocess.TimeoutExpired:
			kill(proc.pid)

		#Launching  java driver
		p2 = subprocess.Popen(javacmd, shell=True)
		while p2.wait():
			pass
		file.write("%s\n" %cmd)
		run += 1
	file.flush()

	###################################################################
	#Read  Data from files for  for performance values

	fileD = open("resultDistalgo.txt", "r");
	fileJ = open("results_java.txt", "r");

	valuesLDistalgo = {}      # stores latency for distalgo
	valuesLJava = {}          # stores latency for java
	valuesHDistalgo = {}      # stores hop count for distalgo
	valuesHJava = {}          # stores hop count for java
	valuesLookupDistalgo = {} # stores lookup success ratio for distalgo
	valuesLookupJava = {}     # stores lookup succes ratio for java
	valuesTJava = {}          # stores timeout ratio for java 
	valuesTDistalgo = {}      #stores timeout ratio for distalgo 
	table = BeautifulTable()

	column_headers = ["Fix Finger\n delay","Java\n HopCount", "Distalgo\n HopCount", "Java Average\n Latency", "Distalgo Average\n Latency", "Java Lookup\n ratio", "Distalgo Lookup\n ratio","Java Timeout\n ratio", "Distalgo Timeout\n ratio"]

	for i in range(0,5):
		line = fileD.readline()
		line = line.rstrip('\n')
		words = line.split(',')
		numbers = []
		for w in words:
			x = float(w)
			numbers.append( x)
		valuesLDistalgo[permute[i]] = numbers[2]
		valuesHDistalgo[permute[i]] = numbers[1]
		valuesLookupDistalgo[permute[i]] = numbers[3]
		valuesTDistalgo[permute[i]] = numbers[4]

	for i in range(0,5):
		line = fileJ.readline()
		line = line.rstrip('\n')
		words = line.split(',')
		numbers = []
		for w in words:
			x = float(w)
			numbers.append( x)
		valuesLJava[permute[i]] = numbers[2]
		valuesHJava[permute[i]] = numbers[1]
		valuesLookupJava[permute[i]] = numbers[3]
		valuesTJava[permute[i]] = numbers[4]

	###################################################################
	#Dump table and plot graph

	for j in range(0, 5):
		i = permute[j]
		table.append_row([i,valuesHJava[i], valuesHDistalgo[i], valuesLJava[i], valuesLDistalgo[i], valuesLookupJava[i], valuesLookupDistalgo[i], valuesTJava[i], valuesTDistalgo[i]])

	print(tabulate(table, headers=column_headers))
	fileTable.write("Number of bits : %d, Number of Nodes : %d,  Successor List : %d, Total Number of Queries : %d, Successor Delay : %f, CheckPredecessor Delay : %f, Probability Failure : %f\n" %(m, nodes, r, queryNo, stabDelay, predDelay, probFailure))
	fileTable.write(tabulate(table, headers=column_headers))
	fileTable.flush()

	#Plot average latency
	plt.figure()
	lists = sorted(valuesLJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesLDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Fix Finger delay')
	plt.ylabel('Average Latency')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Latency_fix_finger_delay.png'
	plt.savefig(filename)

	plt.figure()
	lists = sorted(valuesHJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesHDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Fix Finger delay')
	plt.ylabel('HopeCount')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Hope_fix_finger_delay.png'
	plt.savefig(filename)

	plt.figure()
	# plot hopCount
	lists = sorted(valuesLookupJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesLookupDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Fix Finger delay ')
	plt.ylabel('Lookup Success')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Lookup_fix_finger_delay.png'
	plt.savefig(filename)
	file.flush()

	plt.figure()
	lists = sorted(valuesTJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesTDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('Fix Finger delay ')
	plt.ylabel('Timeout Ratio')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Timeout_fix_finger_delay.png'
	plt.savefig(filename)
	file.flush()

	file.close()
	fileD.close()
	fileJ.close()
	fileTable.close()


######################################################################################################################################################
#CheckPredecessor delay changes from [0.1 to 0.5] 
#Values of checkPredecessor delay for 5 runs
# The idea to evaluate performance by varying checkpredecessor Delay is taken from paper : #
########### Farida Chowdhury, Mario Kolberg - Performance Evaluation of Structured Peer-to-Peer
# Overlays for Use on Mobile Networks - 2013 International Conference on Developments in eSystems Engineering (DeSE) #############

elif runType == 'CheckPred_Delay':
	print ("\n################## Varying CheckPredecessor Delay ###############\n")
	permute = [0.1,0.2,0.3,0.4,0.5]

	for i in range (0, 5):
		cmd = str(m) + ' ' + str(nodes) + ' ' + str(r) + ' ' + str(queryNo) + ' ' + str(stabDelay) + ' ' + str(fixFingerDelay) + ' ' + str(permute[i]) + ' ' + str(probFailure) + ' ' + str(run)
		print (cmd)
		pythonCmd = pythonRunCommand + cmd
		javacmd = javaRunCommand + cmd
		
	    #Launching  python driver
		proc = subprocess.Popen(pythonCmd , shell=True)
		try:
			proc.wait(timeout=100)
		except subprocess.TimeoutExpired:
			kill(proc.pid)

		#Launching  java driver
		p2 = subprocess.Popen(javacmd, shell=True)
		while p2.wait():
			pass
		file.write("%s\n" %cmd)
		run += 1
	file.flush()

	###################################################################
	#Read  Data from files for  for performance values
	fileD = open("resultDistalgo.txt", "r");
	fileJ = open("results_java.txt", "r");

	valuesLDistalgo = {}      # stores latency for distalgo
	valuesLJava = {}          # stores latency for java
	valuesHDistalgo = {}      # stores hop count for distalgo
	valuesHJava = {}          # stores hop count for java
	valuesLookupDistalgo = {} # stores lookup success ratio for distalgo
	valuesLookupJava = {}     # stores lookup succes ratio for java
	valuesTJava = {}          # stores timeout ratio for java 
	valuesTDistalgo = {}      #stores timeout ratio for distalgo 
	table = BeautifulTable()

	column_headers = ["CheckPredecessor Delay","Java HopCount", "Distalgo HopCount", "Java Average Latency", "Distalgo Average Latency", "Java Lookup ratio", "Distalgo Lookup ratio","Java Timeout ratio", "Distalgo Timeout ratio"]

	for i in range(0,5):
		line = fileD.readline()
		line = line.rstrip('\n')
		words = line.split(',')
		numbers = []
		for w in words:
			x = float(w)
			numbers.append( x)
		valuesLDistalgo[permute[i]] = numbers[2]
		valuesHDistalgo[permute[i]] = numbers[1]
		valuesLookupDistalgo[permute[i]] = numbers[3]
		valuesTDistalgo[permute[i]] = numbers[4]

	for i in range(0,5):
		line = fileJ.readline()
		line = line.rstrip('\n')
		words = line.split(',')
		numbers = []
		for w in words:
			x = float(w)
			numbers.append( x)
		valuesLJava[permute[i]] = numbers[2]
		valuesHJava[permute[i]] = numbers[1]
		valuesLookupJava[permute[i]] = numbers[3]
		valuesTJava[permute[i]] = numbers[4]

	#dump table
	for j in range(0, 5):
		i = permute[j]
		table.append_row([i,valuesHJava[i], valuesHDistalgo[i], valuesLJava[i], valuesLDistalgo[i], valuesLookupJava[i], valuesLookupDistalgo[i], valuesTJava[i], valuesTDistalgo[i]])

	print(tabulate(table, headers=column_headers))
	fileTable.write("Number of bits : %d, Number of Nodes : %d,  Successor List : %d, Total Number of Queries : %d, Successor Delay : %f, Fix Finger Delay : %f, Probability Failure : %f\n" %(m, nodes, r, queryNo, stabDelay, fixFingerDelay, probFailure))
	fileTable.write(tabulate(table, headers=column_headers))
	fileTable.flush()

	#Plot average latency
	plt.figure()
	lists = sorted(valuesLJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesLDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('CheckPredecessor delay')
	plt.ylabel('Average Latency')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Latency_checkpred_delay.png'
	plt.savefig(filename)

	plt.figure()
	lists = sorted(valuesHJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesHDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('CheckPredecessor delay')
	plt.ylabel('HopeCount')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Hope_checkpred_delay.png'
	plt.savefig(filename)

	plt.figure()
	lists = sorted(valuesLookupJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesLookupDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('CheckPredecessor delay ')
	plt.ylabel('Lookup Success Ratio')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Lookup_checkpred_delay.png'
	plt.savefig(filename)
	file.flush()

	plt.figure()
	lists = sorted(valuesTJava.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	lists2 = sorted(valuesTDistalgo.items()) # sorted by key, return a list of tuples
	a, b = zip(*lists2) # unpack a list of pairs into two tuples
	plt.plot(a, b, label="PlotDistValues", marker='s')
	plt.xlabel('CheckPredecessor delay ')
	plt.ylabel('Timeout Ratio')

	plt.legend(["Java", "Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Timeout_checkpred_delay.png'
	plt.savefig(filename)
	file.flush()

	file.close()
	fileD.close()
	fileJ.close()
	fileTable.close()

#############################################################################################################################################################################3

elif (runType == "Storage_Load"):
	print ("\n################## Checking Storage and Load  ###############\n")
	if os.path.exists("resultDistalgo2.txt"):
		os.remove("resultDistalgo2.txt")

	probFailure = 0
	for i in range (0, 5):
		cmd = str(m) + ' ' + str(nodes) + ' ' + str(r) + ' ' + str(queryNo) + ' ' + str(stabDelay) + ' ' + str(fixFingerDelay) + ' ' + str(predDelay) + ' ' + str(probFailure) + ' ' + str(run) + ' ' + 'True'
		print (cmd)
		pythonCmd = pythonRunCommand + cmd
			
		#Launching  python driver
		proc = subprocess.Popen(pythonCmd , shell=True)
		try:
			proc.wait(timeout=100)
		except subprocess.TimeoutExpired:
			kill(proc.pid)
		
		file.write("%s\n" %cmd)
		run += 1
		file.flush()

	fileD1 = open("resultDistalgo2.txt", "r");
	valuesSDistalgo = {}

	for i in range(0, nodes*4):
		line = fileD1.readline()
		line = line.rstrip('\n')
		words = line.split(',')
		numbers = []
		for w in words:
			x = float(w)
			numbers.append( x)
		valuesSDistalgo[numbers[1]] = numbers[2]  #stores load values corresponding to storage values

	plt.figure()
	lists = sorted(valuesSDistalgo.items()) # sorted by key, return a list of tuples
	x, y = zip(*lists) # unpack a list of pairs into two tuples
	plt.plot(x, y, label="PlotValues", marker='o')

	plt.plot(x, y, label="PlotDistValues", marker='s')
	plt.xlabel('Storage balance')
	plt.ylabel('Load balance')

	plt.legend(["Distalgo"], loc = "upper left",prop= {'size':5})
	filename = 'Results/Storage_Load.png'
	plt.savefig(filename)

	#Plot Cummilative distribution function of lookups over latency
	fileDC = open("latencyCDF.txt", "r")
	valuesCDF = []
	while True:
		line = fileDC.readline()
		line = line.strip()
		if line=='':
			break
		x = float(line)
		valuesCDF.append(x)
	valuesCDF.sort()
	p = 1. * np.arange(len(valuesCDF))/(len(valuesCDF) - 1)
	plt.plot(valuesCDF, p)
	plt.xlabel('Latency')
	plt.ylabel('Cumulative Fraction of Lookups')
	plt.savefig('Results/LatencyCDF.png')
	fileDC.close()
	fileD1.close()
	file.close()
	fileTable.close()

else :
	print ("Wrong Run type passed. Please pass one of the following run : Nodes | Failure | Stabilization_Delay | FixFinger_Delay |CheckPred_Delay | Storage_Load")
print('Exiting..............')