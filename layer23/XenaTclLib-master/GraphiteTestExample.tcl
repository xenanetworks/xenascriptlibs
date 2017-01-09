# ------------------------------------------------------------------------------------
# 
# Purpose   : To demonstrate the usage of XenaMainStart loading API and running this test Scenario.
#				
# Create By : Dan Amzulescu - Xena Networks Inc.
#			  dsa@xenanetworks.com
#  Updated  : 1 Jan 2017
#
# -----------------------------------------------------------------------------------

# ----- Import the Xena TCL Command Library ------

#
source xena_api_main.tcl
source xena_api_port.tcl
source xena_api_streams.tcl

source xena_graphite_api_helper.tcl

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

set graphite1_ip 10.0.0.45
set graphite1_port 2003


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
set tx_tid_1 0
set tx_tid_2 1


set ports { "11/0" "11/1"}
set tids     {$tx_tid_1 $tx_tid_2}

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
set xena_socket [Connect $xena1_ip $xena1_port]
if {$xena_socket == "null"} {
	puts "Test Halted due to Xena connection time out"
	return
} 

set graphite_socket [Connect $graphite1_ip $graphite1_port]
if {$graphite_socket == "null"} {
	puts "Test Halted due to Graphite connection time out"
	return
}


# --- Login and provide owner user-name
Login $xena_socket $xena1_password $xena1_owner $console_flag

set systemTime [clock seconds]

for {set i 0} {$i < 120000} {incr i} {
    FeedPortTotalResults $xena_socket $graphite_socket "local.xena" $tx_port_1
	FeedPortNoTPLDResults $xena_socket $graphite_socket "local.xena" $tx_port_1
	
	FeedPortTotalResults $xena_socket $graphite_socket "local.xena" $tx_port_2
	FeedPortNoTPLDResults $xena_socket $graphite_socket "local.xena" $tx_port_2
	
	FeedStreamTxTrafficResults $xena_socket $graphite_socket "local.xena" $tx_port_1 0
	FeedStreamRxTrafficResults $xena_socket $graphite_socket "local.xena" $rx_port_1 $tx_tid_1
	FeedStreamRxLatencyResults $xena_socket $graphite_socket "local.xena" $rx_port_1 $tx_tid_1
	FeedStreamRxJitterResults $xena_socket $graphite_socket "local.xena" $rx_port_1 $tx_tid_1
	FeedStreamRxErrorsResults $xena_socket $graphite_socket "local.xena" $rx_port_1 $tx_tid_1
	
	FeedStreamTxTrafficResults $xena_socket $graphite_socket "local.xena" $tx_port_2 0
	FeedStreamRxTrafficResults $xena_socket $graphite_socket "local.xena" $rx_port_2 $tx_tid_2
	FeedStreamRxLatencyResults $xena_socket $graphite_socket "local.xena" $rx_port_2 $tx_tid_2
	FeedStreamRxJitterResults $xena_socket $graphite_socket "local.xena" $rx_port_2 $tx_tid_2
	FeedStreamRxErrorsResults $xena_socket $graphite_socket "local.xena" $rx_port_2 $tx_tid_2
	after 800
	puts "."
}




# --- Release all ports and disconnect

Logout $xena_socket
close $graphite_socket