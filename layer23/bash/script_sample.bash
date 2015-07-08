#!/bin/bash 

# Define chassis, port, password and owner
MACHINE=192.168.1.170
PORT=22611
PASSWORD='"xena"'  # Must be in double quotes
OWNER='"BASHTEST"' # Must be in double quotes

# Open file handle 3 as TCP connection to chassis:port
exec 3<> /dev/tcp/${MACHINE}/${PORT}
if [ $? -eq 0 ]
then
  echo "Telnet accepting connections"
else
  echo "Telnet connections not possible"
  exit 1
fi

# Send commands with echo command to file handle 3
echo -en "C_LOGON ${PASSWORD}\r\n" >&3
# Read answers from file handle 3, (one line a time)
read  <&3 
# Answers are put in $REPLY variable 
echo $REPLY

# Here are some examples
echo -en "C_OWNER ${OWNER}\r\n"  >&3
read  <&3 
echo $REPLY
echo -en "C_TIMEOUT 20\r\n" >&3
read  <&3 
echo $REPLY
echo -en "C_CONFIG ?\r\n" >&3  # Will create 5 lines of answer
read  <&3 # will only read one line of answer
echo $REPLY 
read  <&3 # will only read one line of answer
echo $REPLY
read  <&3 # will only read one line of answer
echo $REPLY
read  <&3 # will only read one line of answer
echo $REPLY
read  <&3 # will only read one line of answer
echo $REPLY

#
#
# Now echo your CLI commands to ">&3" and read the answers from "<&3"
#
#



# Close file handle 3
exec 3>&-
if [ $? -eq 0 ]
then
    echo "Telnet accepting close"
else
    echo "Telnet close not possible"
fi

