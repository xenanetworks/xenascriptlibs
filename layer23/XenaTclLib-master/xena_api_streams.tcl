# -----------------------------------------------------------------------------------
# Name      : xena_api_streams.tcl
# Purpose   : Provide wrapper streams functions for easier usage
# Create By : Dan Amzulescu - Xena Networks inc.
#			  dsa@xenanetworks.com
#
#  Updated  : 23 Jan 2016
#  Version  : v0.5
# -----------------------------------------------------------------------------------
# ----------------ModifyStreamRate-------------------------
proc ModifyStreamRate {s port sid rate_type new_rate console} {
	set pf_flag 1

	switch $rate_type {
		"FRACTION" { puts $s "$port PS_RATEFRACTION \[$sid\] $new_rate\n" }
		"FPS" { puts $s "$port PS_RATEPPS \[$sid\] $new_rate\n"}
		"L2BPS" { puts $s "$port PS_RATEL2BPS \[$sid\] $new_rate\n" }
		default { set pf_flag 0 }	
	}		
	gets $s response
	if {$response == ""} { gets $s response	}
	
	#if {$response != "<OK>"}    {set pf_flag 0}	
	return $pf_flag
}
#
# -----------------------------------------

# ----------------ModifyStreamMinPacketSize-------------------------
proc ModifyStreamMinPacketSize {s port sid new_size console} {
	set pf_flag 1
	
	puts $s "$port PS_PACKETLENGTH \[$sid\] FIXED $new_size $new_size"	
	
	gets $s response
	if {$response == ""} { gets $s response	}
	if {$console == 1} { puts "$port PS_PACKETLENGTH \[$sid\] FIXED $new_size $new_size   | $response" }	
	
	return $pf_flag
}
#
# -----------------------------------------

# ----------------StreamTxTrafficResults-------------------------
proc StreamTxTrafficResults {s port stream_id result_type console} {

	puts $s "$port PT_STREAM \[$stream_id\] ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]
	
	switch $result_type {
		"BPS" { return [lindex $results 6] }
		"PPS" { return [lindex $results 7] }
		"BYTES" { return [lindex $results 8]}		
		"PACKETS" { return [lindex $results 9]}
		default { return -1 }	
	}
}
#
# -----------------------------------------

# -------------------StreamRxTrafficResults----------------------
proc StreamRxTrafficResults {s port stream_tid result_type console} {

	puts $s "$port PR_TPLDTRAFFIC \[$stream_tid\] ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]
	
	switch $result_type {
		"BPS" { return [lindex $results 6] }
		"PPS" { return [lindex $results 7] }
		"BYTES" { return [lindex $results 8]}		
		"PACKETS" { return [lindex $results 9]}
		default { return -1 }	
	}
}
#
# -----------------------------------------

# -------------------StreamRxLatencyResults----------------------
proc StreamRxLatencyResults {s port stream_tid result_type console} {

	puts $s "$port PR_TPLDLATENCY \[$stream_tid\] ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]
	
	switch $result_type {
		"MIN" { return [lindex $results 6] }
		"AVG" { return [lindex $results 7] }
		"MAX" { return [lindex $results 8]}		
		"SEC" { return [lindex $results 9]}
		default { return -1 }	
	}
}

#
# -----------------------------------------

# -------------------StreamRxJitterResults----------------------
proc StreamRxJitterResults {s port stream_tid result_type console} {

	puts $s "$port PR_TPLDJITTER \[$stream_tid\] ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]
	
	switch $result_type {
		"MIN" { return [lindex $results 6] }
		"AVG" { return [lindex $results 7] }
		"MAX" { return [lindex $results 8]}		
		"SEC" { return [lindex $results 9]}
		default { return -1 }	
	}
}
#
# -----------------------------------------

# -------------------StreamRxErrorsResults----------------------
proc StreamRxErrorsResults {s port stream_tid result_type console} {

	puts $s "$port PR_TPLDERRORS \[$stream_tid\] ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]
	
	switch $result_type {
		"SEQ" { return [lindex $results 7]} 
		"MIS" { return [lindex $results 8]} 
		"PLD" { return [lindex $results 9]}
		default { return -1 }	
	}
}
#
# -----------------------------------------

# ---------------------SaveStreamStatistics------------------------------------------------------
proc SaveStreamResults { s tx_port rx_port tx_sid rx_tid console {comment ""}} {
	
	set pf_flag 1

	set systemTime [clock seconds]
	file mkdir [clock format $systemTime -format "Xena_Results/%d_%m_%Y"]
	set file_name [clock format $systemTime -format "Xena_Results/%d_%m_%Y/StreamResults.csv"]
	
	set fexist [file exist $file_name]
	
	if {[catch {set fp1 [open $file_name a]} errmsg]} {
		if {$console == 1} { puts "\n---Error---: $errmsg \n" }
		return 0
	}	
	
	if {$fexist==0} {
		puts -nonewline $fp1 "Date,Time,,TxPort,RxPort,,Sid,Tid,,Tx_bPS,Tx_PPS,Tx_BYTES,Tx_PACKETS,,"	
		puts -nonewline $fp1 "Rx_bPS,Rx_PPS,Rx_BYTES,Rx_PACKETS,,"
		puts -nonewline $fp1 "PacketLoss,MisOrdered,PayloadErrors,,"
		puts -nonewline $fp1 "LatencyMIN,LatencyAVG,LatencyMAX,Latency1Sec,,JitterMIN,JitterAVG,JitterMAX,Jitter1Sec,\n"
	}
	
	
	puts $s "$tx_port PT_STREAM \[$tx_sid\] ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set date [clock format $systemTime -format %d_%m_%Y]
	set time [clock format $systemTime -format %H_%M_%S]
	
	set results [split $response " "]
	puts -nonewline $fp1  "$date,$time,,P_$tx_port,P_$rx_port,,$tx_sid,$rx_tid,,[lindex $results 6],[lindex $results 7],[lindex $results 8],[lindex $results 9],,"
	

	puts $s "$rx_port PR_TPLDTRAFFIC \[$rx_tid\] ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]
	puts -nonewline $fp1  "[lindex $results 6],[lindex $results 7],[lindex $results 8],[lindex $results 9],,"

	puts $s "$rx_port PR_TPLDERRORS \[$rx_tid\] ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]
	puts -nonewline $fp1  "[lindex $results 7],[lindex $results 8],[lindex $results 9],,"

	puts $s "$rx_port PR_TPLDLATENCY \[$rx_tid\] ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]
	puts -nonewline $fp1  "[lindex $results 6],[lindex $results 7],[lindex $results 8],[lindex $results 9],,"
	
	puts $s "$rx_port PR_TPLDJITTER \[$rx_tid\] ?"
	gets $s response
	if {$response == ""} { gets $s response	}
	
	set results [split $response " "]
	puts -nonewline $fp1  "[lindex $results 6],[lindex $results 7],[lindex $results 8],[lindex $results 9],\n"
	
	close $fp1
	return $pf_flag		
}