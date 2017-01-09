# ------------------------------------------------------------------------------------
# 
# Purpose   : To demonstrate the usage of XenaMainStart loading API and running this test Scenario.
#				Latency Test RFC2544 a la mode...
# Create By : Dan Amzulescu - Xena Networks Inc.
#			  dsa@xenanetworks.com
#
# -----------------------------------------------------------------------------------

# ----- Import the Xena TCL Command Library ------
#
source [file dirname [info script]]/xena_api_main.tcl
source [file dirname [info script]]/xena_api_streams.tcl

# ------------------------------------------------

# ---------------- General Variables ----------
#
# Chassis IP
set xena1_ip 131.164.227.250
#
# Chassis scripting port
set xena1_port 22611
#
# Chassis password
set xena1_password \"xena\"
#
# Test port owner
set xena1_owner "\"TCLAPI\""
#
# -----------------------------------------------

# ---------------- Test Scenario Variables ----------------
#
# Tx port 1
set tx_port_1 "11/0"
# Rx port 1
set rx_port_1 "11/1"

# Tx port 2
set tx_port_2 "11/1"
# Rx port 2
set rx_port_2 "11/0"

# The TID`s used in 
set tx_tid_1 1
set tx_tid_2 2


 set ports { "11/0" "11/1"}
 set tids     {$tx_tid_1 $tx_tid_2}
 set packet_sizes { "64" "128"}
 set rates { "500000" "800000" }

set port_config_1 "1.xpc"
set port_config_2 "2.xpc"

# Setting the time for the traffic to run each trial in seconds
set trial_time 3

# Console flag
set console_flag 1
#
# ---------------------------------------------------------

# -------------------------------TEST MAIN-----------------------------------------
#
# --- Connect + Check Connected
set s [Connect $xena1_ip $xena1_port]

if {$s == "null"} {
	puts "Test Halted due to connection time out"
	return
} 
#

# --- Login and provide owner user-name
set response [Login $s $xena1_password $xena1_owner $console_flag]
# if {$response==0} { Validate Pass/Fail for Function reply}
#
# ------------------------------------------------------------------------------------

# --- Reserve ports
foreach port $ports {ReservePort $s $port $console_flag}

# --- Load port configuration
puts "\[Info\] Loading Port Configuration($port_config_1) to port ($tx_port_1)"
LoadPortConfig $s $tx_port_1 $port_config_1 $console_flag
puts "\[Info\] Loading Port Configuration($port_config_2) to port ($tx_port_2)"
LoadPortConfig $s $tx_port_2 $port_config_2 $console_flag

foreach rate $rates {
	
	# --- Modify rates for just first stream on all ports
	foreach port $ports {ModifyStreamRate $s $port 0 "FRACTION" $rate $console_flag}
		
	foreach size $packet_sizes {	
		
		# --- Modify packet size for just first stream on all ports
		foreach port $ports {ModifyStreamMinPacketSize $s $port 0 $size $console_flag}
		
		foreach port $ports {StopPortTraffic $s $port $console_flag}
		after 300
		SaveStreamResults $s $tx_port_1 $rx_port_1 0 $tx_tid_1 $console_flag
		
		# --- Clear Port Results
		foreach port $ports {ClearPortResults $s $port $console_flag}
	
		# --- Start Traffic on all ports
		foreach port $ports {StartPortTraffic $s $port $console_flag}
	
		# --- Save results of both Streams
		for {set i 0} {$i < $trial_time } {incr i} {	
			
			#SaveStreamResults $s $tx_port_2 $rx_port_2 0 $tx_tid_2 $console_flag
			after 1000*60
		}
	}
}
	

	
		# --- Save results of both Streams
		for {set i 0} {$i < $trial_time } {incr i} {	
			SaveStreamResults $s $tx_port_1 $rx_port_1 0 $tx_tid_1 $console_flag
			SaveStreamResults $s $tx_port_2 $rx_port_2 0 $tx_tid_2 $console_flag
			after 1000
}


# --- Stop Traffic on all ports
foreach port $ports {StopPortTraffic $s $port $console_flag}
after 100



# --- Release all ports and disconnect
foreach port $ports { set response [ReleasePort $s $port $console_flag] }
set response [Logout $s]
