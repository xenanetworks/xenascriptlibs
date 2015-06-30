
The files in this collection uses Python as the scripting language
for controlling Xenas L4-7 products XenaAppliance and XenaScale.

The files consist of a Python library called testutils and a number 
of test scripts.

In the following example we assume that your chassis ip address is 192.168.1.210
and uses ports 1/2 and 1/3. 



## Payload.py
The Payload.py script establishes the specified number of connections 
and the speficied load profile (see the many options for details)

```
> ./Payload.py 192.168.1.210 1/2 1/3
```


## Bisect.py
This script performs an iterative procedure to find the maximum number of
connections per second CPS for connection establishment and teardown.

There are a number of options such as the test resolution, number of allocated
packet engines, but for a quick test with 1M connections just type

```
> ./Bisect.py 192.168.1.210 1000 1000 600 400 1/2 1/3
```


   
