# Implementing and evaluating DNS using Chord in DistAlgo
<https://sites.google.com/a/stonybrook.edu/sbcs535/projects/dns-chord-distalgo>
## Requirements
Please run below commands to install below libraries before running this code:
```
pip install numpy
pip install matplotlib
pip install beautifultable
pip install psutil
pip install tabulate
```
## Version for Distalgo and Java
Distalgo version: 1.1.0b12
Java version: 1.8.0_60

## Compile the Java Program using Makefile in CLI (Unix/MacOS)
```
Navigate to open-chord directory
make
```

## Execution Command:
Run the Monitor file: 
Execute following command to run monitor.py file:

```
python monitor.py runType m n r q s_d f_d p_d prob
```
Parameters to be passed:
runType : where runType is string that you want to vary keeping other parameters fixed. It can be Nodes, Failure, Stabilization_Delay, FixFinger_Delay, CheckPred_Delay, Storage_Load

m = number of bits for finger table size and maximum number of nodes in chord ring. Default value: 5. Constraint: This value should be in between 2 - 16.

n = number of nodes in the chord ring. Default value: 6

r = success list size. Default value: 2

q = number of queries. Default value: 200

s_d = Stabilization delay. Default value: 0.1s. Constraint: This value should be in between 0-1.

f_d = Fix Finger delay. Default value: 0.1s. Constraint: This value should be in between 0-1.

p_d  = check predecessor delay. Default value: 0.1s. Constraint: This value should be in between 0 - 1.

prob = Probability failure ratio. Default value: 0.1. Constraint: This value should be in between 0-1.

After running the program, chordTabularResults.txt will contain the tabular results and graphs will be stored in results folder.

Run Following commands to execute all test scenarios on default parameters
```
python monitor.py Nodes
python monitor.py Failure
python monitor.py Stabilization_Delay
python monitor.py FixFinger_Delay
python monitor.py CheckPred_Delay
python monitor.py Storage_Load
```

## Compile the Java Program (Windows)
```
Navigate to open-chord directory
javac -d bin -sourcepath src -cp ./lib/*;./config/chord.properties src/myapp/driver/Driver.java
```

## Run the Java Driver Program in CLI
For Mac/Unix Environment:
```
java -cp ./open-chord/.:./open-chord/bin:./open-chord/lib/*:./open-chord/chord.properties:./open-chord/config/* myapp.driver.Driver 8 2 1 2 2 2 1 0.6 1
```
For Windows:
```
java -cp ./open-chord/.;./open-chord/bin;./open-chord/lib/*;./open-chord/chord.properties;./open-chord/config/* myapp.driver.Driver 8 2 1 2 2 2 1 0.6 1
```



## Credits:
Open Source Implementation can be found here - https://github.com/jtan189/open-chord.

We have referred the same source code and made changes to include driver program to compare implementations of Chords.




