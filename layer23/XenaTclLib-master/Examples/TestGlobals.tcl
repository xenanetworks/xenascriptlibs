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