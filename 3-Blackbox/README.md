# Documentation

Please note that for some scripts you have to edit the variables within the source code.  

## plotAverageIntervalSocktap.py

Reads pcap files containing CAM messages.
The script then plots two histograms with the time between CAM messages.

This is used to compare the CAM intervals of a device in normal operation and after a crash.

## sshBasedBlackboxFuzz.py

Sends fuzzed messages to a C-ITS device via SSH. See the script below for more information. 

## udpBasedBlackboxFuzz.py

This script implements a blackbox fuzzing approach for C-ITS implementations where the internal structure of the system is unknown. 
It works by sending fuzzed CAM messages to the target device over UDP and monitoring the device's response. 
Specifically, it leverages the periodic transmission of CAM messages as a liveness indicator. 
If the device crashes due to a fuzzed input, it will cease to transmit CAM messages or experience a significant delay in their transmission.
When this happens, the seeds will be exported to the output folder as an anomaly for further analysis. 

### Vanetza preparation
Start the vanetza socktap demo application using the following command line arguments (See https://www.vanetza.org/tools/socktap/):
```
./socktap -l udp
```

### Commandline arguments of this script

* `-o, --output`: Output directory for anomalies
* `-i, --input`: Folder containing the input seed files
* `--packet_interval`: Number of packets to send before sniffing for a response (default: 3)
* `-hi, --high_threshold`: High threshold for generation time interval (default: 1100)
* `-lo, --low_threshold`: Low threshold for generation time interval (default: 990)
