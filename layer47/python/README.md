# Python Examples
The files in this collection uses Python as the scripting language
for controlling Xenas L4-7 products XenaAppliance and XenaScale.

The files consist of a Python library called testutils and a number 
of test scripts using the functionality provided by the library.

In the following example we assume that your chassis ip address is 192.168.1.210
and uses ports 1/2 and 1/3. 

Most scripts have a debug option **-d** which can be used to show which script
commands are actually sent to the server.

### Logging
Logging of scripting commands can be enabled by setting the environment 
variable **XENLOG**. This allows you to inspect the actual commands generated
by running a script with specific parameters and options.

```
> export XENALOG=logfile
> ./Ramp.py 192.168.1.210 1/2 1/4
> cat logfile
```

##Packet generating scripts

### Ramp.py
This scripts generates SYN/FIN packets only. No payload is transmitted.

```
> ./Ramp.py 192.168.1.210 1/2 1/3
```

### Payload.py
The Payload.py script transmits payload over a specified number of connections 
and load profile (see the many options for details). Following
coinnection establishment, payload is transmitted.

```
> ./Payload.py 192.168.1.210 1/2 1/3
```

### Bisect.py
This script performs an iterative procedure to find the maximum number of
connections per second CPS for connection establishment and teardown.

There are a number of options such as the test resolution, number of allocated
packet engines, but for a quick test with 1M connections just type

```
> ./Bisect.py 192.168.1.210 1000 1000 600 400 1/2 1/3
```

##Utility scripts
These scripts are just simple examples of how to extract certain information 
from a chassis.

### Info.py
Displays various chassis related information, such as software versions and 
license attributes.

```
> ./Info.py 192.168.1.210
```

### PortStatus.py
Lists all ports on a chassis, along with attributes such as configured 
speed, current link speed, packet engine allocation, speec capabilities, etc.

```
> ./PortStatus.py 192.168.1.210
```

### GetStats.py
Retrieves selected statistics for a given port.

```
> ./GetStats.py 192.168.1.210 1/2
```

### ResetAllPorts.py
Used to bring all ports in a default state, clearing all counters, and packet 
engine allocations.

```
> ./ResetAllPorts.py 192.168.1.210 1/2
```

### Reboot.py
Just a simple example showing how to remotely reboot (or halt) a chassis
   
```
> ./Reboot.py 192.168.1.210
```
