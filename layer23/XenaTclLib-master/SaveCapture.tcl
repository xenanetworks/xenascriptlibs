# ----- Import the Xena TCL Command Library ------
#
source [file dirname [info script]]/xena_api_main.tcl
source [file dirname [info script]]/xena_api_port.tcl
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


# ---------------- Test Scenario Variables ----------------

set port "11/0"

# -------------------------------TEST MAIN-----------------------------------------
#
# --- Connect + Check Connected
set xena_socket [Connect $xena1_ip $xena1_port]
if {$xena_socket == "null"} {
	puts "Test Halted due to Xena connection time out"
	return
} 



# --- Login and provide owner user-name
Login $xena_socket $xena1_password $xena1_owner $console_flag

# --- TEST
ReservePort $s $port $console_flag
SavePortCapture $s $port $console_flag

# --- Release all ports and disconnect
ReleasePort $s $port $console_flag
Logout $xena_socket