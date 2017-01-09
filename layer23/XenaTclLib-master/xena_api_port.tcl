# -----------------------------------------------------------------------------------
# Name      : xena_api_port.tcl
# Purpose   : Provide wrapper port functions for easier usage
# Create By : Dan Amzulescu - Xena Networks inc.
#			  dsa@xenanetworks.com
#
#  Updated  : 23 Jan 2016
#  Version  : v0.5
# -----------------------------------------------------------------------------------

# ---------------- IsPortReserved ----------------
proc IsPortReserved {s port console} {

	set pf_flag 0
	
	puts $s "$port P_RESERVEDBY ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	set results [split $response " "]
	
	if {$console == 1} { puts "$port P_RESERVEDBY  | $response" }	

	if {[lindex $results 4] == "\"\""}    {set pf_flag 1}	
  
   return $pf_flag
}
#
# ----------------------------------------

# ---------------- IsPortReservedByMe ----------------
proc IsPortReservedByMe {s port console} {

	set pf_flag 0
	
	puts $s "$port P_RESERVATION ? "
	gets $s response
	if {$response == ""} { gets $s response	}
	set results [split $response " "]
	
	if {$console == 1} { puts "$port P_RESERVATION ? | $response" }	

	if {[lindex $results 4] == "RESERVED_BY_YOU"}    {set pf_flag 1}	
  
   return $pf_flag
}
#
# ------------------------------------------

# ---------------- Unlock_Port ----------------
proc UnlockPort {s port console} {

	set pf_flag 1
	
	puts $s "$port P_RESERVATION RELINQUISH"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	if {$console == 1} { puts "$port P_RESERVATION RELINQUISH   | $response" }	
	if {$response != "<OK>"}    {set pf_flag 0}	
  
   return $pf_flag
}
#
# -----------------------------------------

# ---------------- Reserve_Port ----------------
proc ReservePort {s port console} {

	set pf_flag 1
	
	puts $s "$port P_RESERVATION RESERVE"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	if {$console == 1} { puts "$port P_RESERVATION RESERVE   | $response" }	
	if {$response != "<OK>"}    {set pf_flag 0}	
  
   return $pf_flag
}
#
# -----------------------------------------

# ---------------- Release_Port ----------------
proc ReleasePort {s port console} {

	set pf_flag 1
	
	puts $s "$port P_RESERVATION RELEASE"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	if {$console == 1} { puts "$port P_RESERVATION RELEASE   | $response" }	
	if {$response != "<OK>"}    {set pf_flag 0}	
  
   return $pf_flag
}
#
# -----------------------------------------

# ---------------- ClearPort ----------------
proc ResetPort {s port console} {

	set pf_flag 1
	
	puts $s "$port P_RESET"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	if {$console == 1} { puts "$port P_RESET  | $response" }	
	if {$response != "<OK>"}    {set pf_flag 0}	
  
   return $pf_flag
}
#
# -----------------------------------------

# ---------------- HasLink ----------------
proc HasLink {s port console} {

	set has_link_flag 0
	
	puts $s "$port P_RECEIVESYNC ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	if {$console == 1} { puts "$port P_RECEIVESYNC | $response" }	
	if {$response == "$port  P_RECEIVESYNC  IN_SYNC"}    { set has_link_flag 1}	
  
   return $has_link_flag
}
#
# -----------------------------------------

# ---------------- StartPortCapture -------------
proc StartPortTraffic {s port console} {

	set pf_flag 1
	
	puts $s "$port P_TRAFFIC ON"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	if {$console == 1} { puts "$port P_TRAFFIC ON   | $response" }	
	if {$response != "<OK>"}    {set pf_flag 0}	
  

	
   return $pf_flag
}
#
# -----------------------------------------

# ---------------- StopPortTraffic -------------
proc StopPortTraffic {s port console} {

	set pf_flag 1
	
	puts $s "$port P_TRAFFIC OFF"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	if {$console == 1} { puts "$port P_TRAFFIC OFF   | $response" }	
	if {$response != "<OK>"}    {set pf_flag 0}	
  
   return $pf_flag
}
#
# -----------------------------------------

# ---------------- StartPortTraffic -------------
proc StartPortCapture {s port console} {

	set pf_flag 1
	
	puts $s "$port P_CAPTURE ON"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	if {$console == 1} { puts "$port P_CAPTURE ON   | $response" }	
	if {$response != "<OK>"}    {set pf_flag 0}	
  
   return $pf_flag
}
#
# -----------------------------------------

# ---------------- StopPortCapture -------------
proc StopPortCapture {s port console} {

	set pf_flag 1
	
	puts $s "$port P_CAPTURE OFF"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	if {$console == 1} { puts "$port P_CAPTURE OFF   | $response" }	
	if {$response != "<OK>"}    {set pf_flag 0}	
  
   return $pf_flag
}
#
# -----------------------------------------

# ---------------- ClearPortResults -------------
proc ClearPortResults {s port console} {

	set pf_flag 1
	
	puts $s "$port PT_CLEAR"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	if {$console == 1} { puts "$port PT_CLEAR | $response" }	
	if {$response != "<OK>"}    {set pf_flag 0}

	puts $s "$port PR_CLEAR"
	gets $s response
	if {$console == 1} { puts "$port PR_CLEAR | $response" }	
	if {$response != "<OK>"}    {set pf_flag 0}		
  
   return $pf_flag
}
#
# -----------------------------------------

# ---------------- PortLinkDown -------------
proc PortLinkDown {s port console} {

	set pf_flag 1
	
	puts $s "$port P_TXENABLE OFF"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	if {$console == 1} { puts "$port P_TXENABLE OFF   | $response" }	
	if {$response != "<OK>"}    {set pf_flag 0}	
  
   return $pf_flag
}
#
# -----------------------------------------

# ---------------- PortLinkUp -------------
proc PortLinkUp {s port console} {

	set pf_flag 1
	
	puts $s "$port P_TXENABLE ON"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	if {$console == 1} { puts "$port P_TXENABLE ON   | $response" }	
	if {$response != "<OK>"}    {set pf_flag 0}	
  
   return $pf_flag
}
#
# -----------------------------------------

# ----------------PortTxTotalResults-------------------------
proc PortTxTotalResults {s port result_type console} {
	
	puts $s "$port PT_TOTAL ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]
	
	switch $result_type {
		"BPS" { return [lindex $results 4] }
		"PPS" { return [lindex $results 5] }
		"BYTES" { return [lindex $results 6]}		
		"PACKETS" { return [lindex $results 7]}
		default { return -1 }	
	}
}
#
# -----------------------------------------

# ----------------PortRxTotalResults-------------------------
proc PortRxTotalResults {s port result_type console} {
	
	puts $s "$port PR_TOTAL ?"
	gets $s response	
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]
	
	switch $result_type {
		"BPS" { return [lindex $results 4] }
		"PPS" { return [lindex $results 5] }
		"BYTES" { return [lindex $results 6]}		
		"PACKETS" { return [lindex $results 7]}
		default { return -1 }	
	}
}
#
# -----------------------------------------

# ----------------PortTxNoTPLDResults-------------------------
proc PortTxNoTPLDResults {s port result_type console} {
	puts $s "$port PT_NOTPLD ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]
	
	switch $result_type {
		"BPS" { return [lindex $results 4] }
		"PPS" { return [lindex $results 5] }
		"BYTES" { return [lindex $results 6]}		
		"PACKETS" { return [lindex $results 7]}
		default { return -1 }	
	}
}
#
# -----------------------------------------

# ----------------PortRxNoTPLDResults-------------------------
proc PortRxNoTPLDResults {s port result_type console} {
	puts $s "$port PR_NOTPLD ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]
	
	switch $result_type {
		"BPS" { return [lindex $results 4] }
		"PPS" { return [lindex $results 5] }
		"BYTES" { return [lindex $results 6]}		
		"PACKETS" { return [lindex $results 7]}
		default { return -1 }	
	}
}
#
# -----------------------------------------

# -------------------PortRxFilterResults----------------------
proc PortRxFilterResults {s port filter_id result_type console} {

	puts $s "$port PR_FILTER \[$filter_id\] ?\n"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]
	
	switch $result_type {
		"BPS" { return [lindex $results 6]	}
		"PPS" { return [lindex $results 7]}
		"BYTES" { return [lindex $results 8]}
		"PACKETS" { return [lindex $results 9]}
		default { return -1 }	
	}
}
#
# -----------------------------------------

# ----------------------------------------------------------------------------------------------------------------------------------------------

# ---------------- LoadPortConfig ----------------
proc LoadPortConfig { s port file_name console} {
	set fp [open $file_name r]
    set file_data [read $fp]
    set data [split $file_data "\n"]	
	
    foreach line $data { 
		if {$line==""} {break}
		if !{[string match ";*" $line]} {
			puts $s "$port $line"
			gets $s response
		}
	}
    close $fp  
}
#
# -----------------------------------------

# ---------------- SavePortCapture ----------------
proc SavePortCapture { s port console} {
	# Setting the Pass/Fail flag to true for error reporting
	set pf_flag 1
	
	# Checking to see capture is not currently ON
	puts $s "$port P_CAPTURE ?\n"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	# Turn OFF capture in case it is ON	
	if {$response == "$port  P_CAPTURE  ON"} {
		puts $s "$port P_CAPTURE OFF"
		gets $s response
		if {$response == ""} { gets $s response	}
	}
	
	# Get the Date/Time from system in order to save it to a date formatted dir.
	set systemTime [clock seconds]
		
	regsub -all {[/]} $port {_} p
	
	#Create the files that are going to be used
	set txt_file_name     [clock format $systemTime -format "Xena_Results/%d_%m_%Y/Capture/P_$p/%H_%M_%S.txt"]
	set txtpcap_file_name [clock format $systemTime -format "Xena_Results/%d_%m_%Y/Capture/P_$p/%H_%M_%S.pcap.txt"]
	set pcap_file_name    [clock format $systemTime -format "Xena_Results/%d_%m_%Y/Capture/P_$p/%H_%M_%S.pcap"]
	
	#Create the Directory that the PCAP will be saved to
	file mkdir [clock format $systemTime -format "Xena_Results/%d_%m_%Y/Capture/P_$p"]
	
	# check txt File handler
	if {[catch {set fp1 [open $txt_file_name w]} errmsg]} {
		if {$console == 1} { puts "\n---Error---: $errmsg \n" }
		return 0
	}
	# check formatted_txt File handler
	if {[catch {set fp2 [open $txtpcap_file_name w]} errmsg]} {
		if {$console == 1} { puts "\n---Error---: $errmsg \n" }
		return 0
	}
	
	# Check amount of packet in Buffer.
	puts $s "$port PC_STATS ?\n"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]	
	set buffered_packets [lindex $results 5]
	
	# Loop that gets all HEX format packets and places them 
	if { $buffered_packets > 0 } {
		for {set i 0} {$i < $buffered_packets } {incr i} {

			puts $s "$port PC_PACKET \[$i\] ?\n"
			gets $s response
			if {$response == ""} { gets $s response	}
			
			set results [split $response " "]
			
			set packet_raw_data [lindex $results 6]
			puts $fp1 $packet_raw_data			
			
			set trimmed_string [string range $packet_raw_data 2 [string length $packet_raw_data]]
			set length [string length $trimmed_string]						
			
			for {set j 0;set loop_index 1} {$j < $length } {incr j;incr j;incr loop_index} {				
				if { $loop_index == 1} {	puts -nonewline $fp2 "[format "%6.6X" $j] "	}
				puts -nonewline $fp2 "[string range $trimmed_string $j [expr $j+1]] "								
				if { $loop_index % 16 == 0} {  puts -nonewline $fp2 "\n[format "%6.6X" $loop_index] " } 
			}
			puts $fp2 ""
		}
	}	
    
    close $fp1
	close $fp2
	
	set path [file normalize [info script]]
	set path [file dirname $path]
	
	if {[catch {[exec "C:/Program Files/Wireshark/text2pcap.exe" $path\\$txtpcap_file_name $path\\$pcap_file_name]} errmsg]} {
		if {$console == 1} { puts "\n--------Output From text2pcap.exe Exec--------:\n$errmsg\n-----------------------------------------------\n" }
		return 0
	}	
	
	return $pf_flag
}
#
# -----------------------------------------

# -------------------SavePortResults--------------------------------------------------------
proc SavePortResults { s port console} {
	
	set pf_flag 1
		
	set systemTime [clock seconds]
	file mkdir [clock format $systemTime -format "Xena_Results/%d_%m_%Y"]
	set file_name [clock format $systemTime -format "Xena_Results/%d_%m_%Y/PortResults.csv"]
	
	set fexist [file exist $file_name]
	
	if {[catch {set fp1 [open $file_name a]} errmsg]} {
		if {$console == 1} { puts "\n---Error---: $errmsg \n" }
		return 0
	}	
	
	
	
	if {$fexist==0} {
		puts -nonewline $fp1 "Date,Time,,Port,,Todal_Tx_bPS,Todal_Tx_PPS,Todal_Tx_BYTES,Todal_Tx_PACKETS,"
		puts -nonewline $fp1 "NoTPLD_Tx_bPS,Todal_Tx_PPS,Todal_Tx_BYTES,Todal_Tx_PACKETS,"
		puts -nonewline $fp1 "Todal_Rx_bPS,Todal_Rx_PPS,Todal_Rx_BYTES,Todal_Rx_PACKETS,"
		puts -nonewline $fp1 "NoTPLD_Rx_bPS,NoTPLD_Rx_PPS,NoTPLD_Rx_BYTES,NoTPLD_Rx_PACKETS,\n"
	}
	
	puts $s "$port PT_TOTAL ?"
	gets $s response
	if {$response == ""} { gets $s response	}	
	set results [split $response " "]
	
	set date [clock format $systemTime -format %d_%m_%Y]
	set time [clock format $systemTime -format %H_%M_%S]
	
	puts -nonewline $fp1  "$date,$time,,P_$port,,[lindex $results 4],[lindex $results 5],[lindex $results 6],[lindex $results 7],"
	puts $s "$port PT_NOTPLD ?"
	gets $s response
	if {$response == ""} { gets $s response	}	
	set results [split $response " "]
	puts -nonewline $fp1  "[lindex $results 4],[lindex $results 5],[lindex $results 6],[lindex $results 7],"
	puts $s "$port PR_TOTAL ?"
	gets $s response
	if {$response == ""} { gets $s response	}	
	set results [split $response " "]
	puts -nonewline $fp1  "[lindex $results 4],[lindex $results 5],[lindex $results 6],[lindex $results 7],"
	puts $s "$port PR_NOTPLD ?"
	gets $s response
	if {$response == ""} { gets $s response	}	
	set results [split $response " "]
	puts -nonewline $fp1  "[lindex $results 4],[lindex $results 5],[lindex $results 6],[lindex $results 7],\n"

	close $fp1
	return $pf_flag		
}
#
# --------------------------------
