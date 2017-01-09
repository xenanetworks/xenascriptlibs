# ----- Import the Xena TCL Command Library ------
#
source [file dirname [info script]]/xena_api_main.tcl
source [file dirname [info script]]/xena_api_streams.tcl

# ----- Import the Test Globals ------
#
source [file dirname [info script]]/TestGlobals.tcl

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

# ------------------------------------------------------------------------------------

SaveStreamResults $s $tx_port_1 $rx_port_1 0 $tx_tid_1 $console_flag
SaveStreamResults $s $tx_port_2 $rx_port_2 0 $tx_tid_2 $console_flag


# --- Release all ports and disconnect
foreach port $ports { set response [ReleasePort $s $port $console_flag] }
set response [Logout $s]
