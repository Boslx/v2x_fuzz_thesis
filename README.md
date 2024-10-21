# Fuzzing Strategies for Identifying Vulnerabilities in V2X
This repository contains the source code developed for my master thesis at the University of Ulm, exploring fuzzing strategies to identify vulnerabilities in V2X (Vehicle-to-Everything) communication systems.

This repository utilizes submodules to maintain a modular and organized codebase. To clone the repository with all its necessary components, use the flag `--recurse-submodules`.

The submodules are:
- [pycrate-asn1-fuzzer](https://github.com/Boslx/pycrate-asn1-fuzzer)  Pycrate fork to generate fuzzed ASN.1 inputs 
- [scapy-etsi-its](https://github.com/Boslx/scapy-etsi-its) Scapy layers for dissecting and crafting ETSI C-ITS packets 

The artefacts of the evaluation can be found in the releases of this repository. 