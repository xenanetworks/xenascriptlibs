# Python Examples
The files in this collection uses Python as the scripting language
for controlling Xenas L4-7 products XenaAppliance and XenaScale.

The files consist of a Python library called testutils and a number 
of test scripts.

In the following example we assume that your chassis ip address is 192.168.1.210
and uses ports 1/2 and 1/3. 


##Packet generating scripts

### Payload.py
The Payload.py script establishes the specified number of connections 
and the speficied load profile (see the many options for details)

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
Lists all ports ona chassis, along with attributes such as configured 
speed, current link speed, packet engine allocation, speec capabilities, etc.

```
> ./PortStatus.py 192.168.1.210
```


### GetStats.py
Retrieves selected statistics for a given port. The port must 

```
> ./GetStats.py 192.168.1.210 1/2
```

### Reboot.py
Just a simple example showing how to remotely reboot (or halt) a chassis
   
```
> ./Reboot.py 192.168.1.210
```
