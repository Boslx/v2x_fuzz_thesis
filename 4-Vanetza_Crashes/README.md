# Documentation


This directory contains crash reports for Vanetza at commit [8c7c6d3](https://github.com/riebl/vanetza/tree/8c7c6d35d1a1dea57f7ad04d8770f7c87a606948). These crashes have been addressed and should no longer occur in the current master branch.

To reproduce these crashes in the specified Vanetza commit, use the [sendNastyPayload_vanetza.py](../99-Helper/sendNastyPayload_vanetza.py) script located in the `99-Helper` directory.

## Crash Analysis Reports (CASRs)

Detailed information about each crash can be found in the corresponding `.casrep` files.  A summary of the crashes is provided below:
```
==> <cl1>
Crash: /usr/src/project/routerIndicate/output-casr/cl1/id:000001,sig:06,src:000572,time:41636,execs:43332,op:havoc,rep:7
  casrep: NOT_EXPLOITABLE: std::bad_alloc: /home/boslx/CLionProjects/vanetzaFuzz/vanetza/security/v2/recipient_info.cpp:129
  Similar crashes: 1
Cluster summary -> std::bad_alloc: 1
==> <cl2>
Crash: /usr/src/project/routerIndicate/output-casr/cl2/id:000013,sig:06,src:000429,time:113488,execs:322766,op:ext_AO,pos:51
  casrep: NOT_EXPLOITABLE: allocation-size-too-big: /home/boslx/CLionProjects/vanetzaFuzz/vanetza/security/v2/recipient_info.cpp:129
  Similar crashes: 1
Cluster summary -> allocation-size-too-big: 1
==> <cl3>
Crash: /usr/src/project/routerIndicate/output-casr/cl3/id:000117,sig:06,src:003405,time:74174793,execs:100996152,op:quick,pos:535
  casrep: NOT_EXPLOITABLE: std::runtime_error: /home/boslx/CLionProjects/vanetzaFuzz/vanetza/asn1/asn1c_wrapper.cpp:57
  Similar crashes: 1
Cluster summary -> std::runtime_error: 1
==> <cl4>
Crash: /usr/src/project/routerIndicate/output-casr/cl4/id:000010,sig:06,src:000697+000474,time:66004,execs:237404,op:splice,rep:9
  casrep: NOT_EXPLOITABLE: std::bad_alloc: /home/boslx/CLionProjects/vanetzaFuzz/vanetza/security/v2/subject_attribute.cpp:60
  Similar crashes: 3
Cluster summary -> std::bad_alloc: 3
==> <cl5>
Crash: /usr/src/project/routerIndicate/output-casr/cl5/id:000001,sig:06,src:000145,time:58436,execs:61289,op:ext_AO,pos:5
  casrep: NOT_EXPLOITABLE: allocation-size-too-big: /home/boslx/CLionProjects/vanetzaFuzz/vanetza/security/v2/payload.cpp:49
  Similar crashes: 4
Crash: /usr/src/project/routerIndicate/output-casr/cl5/id:000000,sig:06,src:000614,time:38852,execs:25743,op:havoc,rep:5
  casrep: NOT_EXPLOITABLE: std::bad_alloc: /home/boslx/CLionProjects/vanetzaFuzz/vanetza/security/v2/payload.cpp:49
  Similar crashes: 5
Cluster summary -> allocation-size-too-big: 4 std::bad_alloc: 5
SUMMARY -> allocation-size-too-big: 5 std::bad_alloc: 9 std::runtime_error: 1
```