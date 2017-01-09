# ------------------------------------------------------------------------------------
# Name      : xena_graphite_api_helper.tcl
# Purpose   : Provide functions to pass results and update a graphite server
# Create By : Dan Amzulescu - Xena Networks inc.
#			  dsa@xenanetworks.com
#
#  Updated  : 24 Jan 2016
#  Version  : v0.3
# -----------------------------------------------------------------------------------


# ----------------FeedPortTotalResults-------------------------
proc FeedPortTotalResults {xena_socket graphite_socket graphite_path port} {
	
	set systemTime [clock seconds]
		
	puts $xena_socket "$port PT_TOTAL ?"
	gets $xena_socket tx_response
	if {$tx_response == ""} { gets $xena_socket tx_response}
	set tx_results [split $tx_response " "]
	
	puts $xena_socket "$port PR_TOTAL ?"
	gets $xena_socket rx_response
	if {$rx_response == ""} { gets $xena_socket rx_response}
	set rx_results [split $rx_response " "]
	
	set module_port [split $port "/"]	
	
	append graphite_path ".Module_[lindex $module_port 0].Port_[lindex $module_port 1].Total."
	
	set result_type "TxBPS"
	puts $graphite_socket "$graphite_path$result_type [lindex $tx_results 4] $systemTime"
	set result_type "TxPPS"
	puts $graphite_socket "$graphite_path$result_type [lindex $tx_results 5] $systemTime"
	set result_type "TxBYTES"
	puts $graphite_socket "$graphite_path$result_type [lindex $tx_results 6] $systemTime"
	set result_type "TxPACKETS"
	puts $graphite_socket "$graphite_path$result_type [lindex $tx_results 7] $systemTime"

	set result_type "RxBPS"
	puts $graphite_socket "$graphite_path$result_type [lindex $rx_results 4] $systemTime"
	set result_type "RxPPS"
	puts $graphite_socket "$graphite_path$result_type [lindex $rx_results 5] $systemTime"
	set result_type "RxBYTES"
	puts $graphite_socket "$graphite_path$result_type [lindex $rx_results 6] $systemTime"
	set result_type "RxPACKETS"
	puts $graphite_socket "$graphite_path$result_type [lindex $rx_results 7] $systemTime"		
}

# ----------------FeedPortNoTPLDResults-------------------------
proc FeedPortNoTPLDResults {xena_socket graphite_socket graphite_path port} {
	
	set systemTime [clock seconds]
		
	puts $xena_socket "$port PT_NOTPLD ?"
	gets $xena_socket tx_response
	if {$tx_response == ""} { gets $xena_socket tx_response}
	set tx_results [split $tx_response " "]
	
	puts $xena_socket "$port PR_NOTPLD ?"
	gets $xena_socket rx_response
	if {$rx_response == ""} { gets $xena_socket rx_response}
	set rx_results [split $rx_response " "]
	
	set module_port [split $port "/"]	
	
	append graphite_path ".Module_[lindex $module_port 0].Port_[lindex $module_port 1].NoTestPayload."
	
	set result_type "TxBPS"
	puts $graphite_socket "$graphite_path$result_type [lindex $tx_results 4] $systemTime"
	set result_type "TxPPS"
	puts $graphite_socket "$graphite_path$result_type [lindex $tx_results 5] $systemTime"
	set result_type "TxBYTES"
	puts $graphite_socket "$graphite_path$result_type [lindex $tx_results 6] $systemTime"
	set result_type "TxPACKETS"
	puts $graphite_socket "$graphite_path$result_type [lindex $tx_results 7] $systemTime"

	set result_type "RxBPS"
	puts $graphite_socket "$graphite_path$result_type [lindex $rx_results 4] $systemTime"
	set result_type "RxPPS"
	puts $graphite_socket "$graphite_path$result_type [lindex $rx_results 5] $systemTime"
	set result_type "RxBYTES"
	puts $graphite_socket "$graphite_path$result_type [lindex $rx_results 6] $systemTime"
	set result_type "RxPACKETS"
	puts $graphite_socket "$graphite_path$result_type [lindex $rx_results 7] $systemTime"		
}

# ----------------FeedStreamTxTrafficResults-------------------------
proc FeedStreamTxTrafficResults {xena_socket graphite_socket graphite_path port stream_id} {

	set systemTime [clock seconds]
	
	puts $xena_socket "$port PT_STREAM \[$stream_id\] ?"
	gets $xena_socket response
	if {$response == ""} { gets $xena_socket response	}
	
	set tx_results [split $response " "]
	
	set module_port [split $port "/"]	
	append graphite_path ".Module_[lindex $module_port 0].Port_[lindex $module_port 1].TxStreams.$stream_id" "."
	
	set result_type "TxBPS"
	puts $graphite_socket "$graphite_path$result_type [lindex $tx_results 6] $systemTime"
	set result_type "TxPPS"
	puts $graphite_socket "$graphite_path$result_type [lindex $tx_results 7] $systemTime"
	set result_type "TxBYTES"
	puts $graphite_socket "$graphite_path$result_type [lindex $tx_results 8] $systemTime"
	set result_type "TxPACKETS"
	puts $graphite_socket "$graphite_path$result_type [lindex $tx_results 9] $systemTime"
}

# ----------------FeedStreamRxTrafficResults-------------------------
proc FeedStreamRxTrafficResults {xena_socket graphite_socket graphite_path port stream_tid} {

    set systemTime [clock seconds]
	
	puts $xena_socket "$port PR_TPLDTRAFFIC \[$stream_tid\] ?"
	gets $xena_socket response
	if {$response == ""} { gets $xena_socket response	}
	
	set results [split $response " "]
	
	set module_port [split $port "/"]	
	append graphite_path ".Module_[lindex $module_port 0].Port_[lindex $module_port 1].RxStreams.$stream_tid" "."
	
	set result_type "RxBPS"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 6] $systemTime"
	set result_type "RxPPS"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 7] $systemTime"
	set result_type "RxBYTES"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 8] $systemTime"
	set result_type "RxPACKETS"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 9] $systemTime"
}

# ----------------FeedStreamRxLatencyResults-------------------------
proc FeedStreamRxLatencyResults {xena_socket graphite_socket graphite_path port stream_tid} {
    
	set systemTime [clock seconds]
	
	puts $xena_socket "$port PR_TPLDLATENCY \[$stream_tid\] ?"
	gets $xena_socket response
	if {$response == ""} { gets $xena_socket response	}
	
	set results [split $response " "]
	set module_port [split $port "/"]	
	append graphite_path ".Module_[lindex $module_port 0].Port_[lindex $module_port 1].RxStreams.$stream_tid" ".Latency."
	
	set result_type "Min"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 6] $systemTime"
	set result_type "Avg"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 7] $systemTime"
	set result_type "Max"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 8] $systemTime"
	set result_type "1SecAvg"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 9] $systemTime"
}

# ----------------FeedStreamRxJitterResults-------------------------
proc FeedStreamRxJitterResults {xena_socket graphite_socket graphite_path port stream_tid} {

    set systemTime [clock seconds]

	puts $xena_socket "$port PR_TPLDJITTER \[$stream_tid\] ?"
	gets $xena_socket response
	if {$response == ""} { gets $xena_socket response	}
	
	set results [split $response " "]
	set module_port [split $port "/"]	
	append graphite_path ".Module_[lindex $module_port 0].Port_[lindex $module_port 1].RxStreams.$stream_tid" ".Jitter."
	
	set result_type "Min"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 6] $systemTime"
	set result_type "Avg"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 7] $systemTime"
	set result_type "Max"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 8] $systemTime"
	set result_type "1SecAvg"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 9] $systemTime"
}

# ----------------FeedStreamRxErrorsResults-------------------------
proc FeedStreamRxErrorsResults {xena_socket graphite_socket graphite_path port stream_tid} {

    set systemTime [clock seconds]
	
	puts $xena_socket "$port PR_TPLDJITTER \[$stream_tid\] ?"
	gets $xena_socket response
	if {$response == ""} { gets $xena_socket response	}
	
	set results [split $response " "]
	set module_port [split $port "/"]	
	append graphite_path ".Module_[lindex $module_port 0].Port_[lindex $module_port 1].RxStreams.$stream_tid" ".Errors."
	
	set result_type "PacketLoss"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 7] $systemTime"
	set result_type "MisOrdered"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 8] $systemTime"
	set result_type "PayloadErrors"
	puts $graphite_socket "$graphite_path$result_type [lindex $results 9] $systemTime"
	
	puts $xena_socket "$port PR_TPLDTRAFFIC \[$stream_tid\] ?"
	gets $xena_socket response2
	if {$response == ""} { gets $xena_socket response2	}
	set results2 [split $response2 " "]
	
	set result_type "BER"
	
	set sumErrors [expr "[lindex $results 7] + [lindex $results 8]"]
	set RxBits [expr "8 * [lindex $results2 9]"]
		
	if {$sumErrors} {		
		puts $graphite_socket "$graphite_path$result_type [expr "double(1) / $RxBits / $sumErrors"] $systemTime"
	}	else {
		puts $graphite_socket "$graphite_path$result_type 0 $systemTime"
	}
	
}