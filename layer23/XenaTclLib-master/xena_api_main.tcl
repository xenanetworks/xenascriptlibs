# ------------------------------------------------------------------------------------
# Name      : xena_api_main.tcl
# Purpose   : Provide wrapper core functions for easier usage
# Create By : Dan Amzulescu - Xena Networks inc.
#			  dsa@xenanetworks.com
#
#  Updated  : 23 Jan 2016
#  Version  : v0.9
# -----------------------------------------------------------------------------------


# ---------------- Connect --------------------------------
proc Connect {chassis_ip chassis_port} {
	global connected
	after 3000 {set connected timeout}
    set s [socket -async $chassis_ip $chassis_port]
	fileevent $s w {set connected ok}
	vwait connected
	fileevent $s w {}
	if {$connected == "timeout"} {
		return null
	} else {
		fconfigure $s -buffering line
		return $s
	} 
}
#
# ---------------------------------------------------------

# ---------------- Login ----------------
proc Login {s chassis_pass chassis_user console} {

	set pf_flag 1

   puts $s "c_logon $chassis_pass"
   gets $s response
   if {$response == ""} { gets $s response	}
   
   if {$response != "<OK>"}    {set pf_flag 0}
   if {$console == 1} { puts "Logging | $response" }	  	
   

   puts $s "c_owner $chassis_user"
   gets $s response
   if {$response == ""} { gets $s response	}
   
   if {$console == 1} { puts "Owner   | $response" }	
   if {$response != "<OK>"}    {set pf_flag 0}
   
   return $pf_flag
}
#
# -----------------------------------------

# ---------------- Logout ----------------
proc Logout {s} {

	puts $s "c_logoff"
	close $s
}
#
# -----------------------------------------


