#!/usr/bin/tclsh
#TCL example for running tests on a Xena Networks tester using the scripting interface. 
#Version 2

# Import the xena tcl command library
source [file dirname [info script]]/xenacom_tcl.tcl

#Default parameters
#Chassis IP
set server 192.168.1.170
#Chassis scripting port
set port 22611
#Chassis password
set password \"xena\"
#Set TX and RX ports
set tx "0/2"
set rx "0/3"


#Set the rate, 10000=1%
set rate "100000"
#Set frame size
set minsize "64"
set maxsize "1518"
#Set number of packets to be sent before auto stop
#set numpackets "1000"
#Set time to wait after traffic start before reading out TX/RX statistics
set time 5
#Set number of simulated hosts
set numhosts 8192


#puts [lindex $argv 0]

#Get all parameters
for {set x 0} {$x<$argc} {incr x} {
   		#Find the IP parameter
	   if { [string compare [string range [lindex $argv $x] 0 2] "ip="] == 0 } {
		   set server [string trimleft [lindex $argv $x] ?ip=?]
		   
	   }
	
	#Find the password parameter
	if { [string compare [string range [lindex $argv $x] 0 2] "pw="] == 0 } { 
		set password [string trimleft [lindex $argv $x] ?pw=?]
		set password \"$password\"
		
	}
	
	#Find the rate parameter
	if { [string compare [string range [lindex $argv $x] 0 4] "rate="] == 0 } {
		set rate [string trimleft [lindex $argv $x] ?rate=?]
		
	}
	#Find the size parameter
	if { [string compare [string range [lindex $argv $x] 0 4] "size="] == 0 } {
		set size [string trimleft [lindex $argv $x] ?size=?]
		
	}
	#Find the time parameter
	if { [string compare [string range [lindex $argv $x] 0 4] "time="] == 0 } {
		set time [string trimleft [lindex $argv $x] ?time=?]
		
	}
	#Find the tx parameter
	if { [string compare [string range [lindex $argv $x] 0 2] "tx="] == 0 } {
		set tx [string trimleft [lindex $argv $x] ?tx=?]
		
	}
	#Find the rx parameter
	if { [string compare [string range [lindex $argv $x] 0 2] "rx="] == 0 } {
		set rx [string trimleft [lindex $argv $x] ?rx=?]
		
	}
	#Find the numpackets parameter
	if { [string compare [string range [lindex $argv $x] 0 4] "pkts="] == 0 } {
		set numpackets [string trimleft [lindex $argv $x] ?pkts=?]
	}
}


set tx_mod [regexp {^(.*?)(?:/)?$} $tx]  
set rx_mod [regexp {^(.*?)(?:\/)?$} $rx]
set tx_port [string range $tx [expr [string first "/" $tx]+1] [expr [string length $tx]-1] ]
set rx_port [string range $rx [expr [string first "/" $rx]+1] [expr [string length $rx]-1] ]

puts ""
puts "IP-address: $server"
puts "Password: $password" 
puts "Traffic rate: $rate"
puts "Packet size: $minsize to $maxsize"
#puts "Number of Packets: $numpackets"
puts "Wait time: $time"
puts "TX/RX: $tx -> $rx"
puts ""
 	
 	#Process for running a test
proc runtest {s} {
	
	global cportcounts
	global numModules
	global tx
	global rx
	global rate
	global minsize
	global maxsize
	global time
	global numpackets
	global tx_port
	global rx_port
	global tx_mod
	global rx_mod
	global numhosts
	
	#Get chassis name
	puts $s "c_name ?"
	set cname [crop2 [gets $s] 1]
	
	#Get comment
	puts $s "c_comment ?"
	set ccomment [crop2 [gets $s] 1]
	
	#Get Serial no
	puts $s "c_serialno ?"
	set cserialno [crop2 [gets $s] 1]
	#gets $s cserialno
	
	#Get Version no
	puts $s "c_versionno ?"
	set cversionno [crop2 [gets $s] 1]
	
	#Get Model
	puts $s "c_model ?"
	set cmodel [crop2 [gets $s] 1]
	
		
	#Get module and port configuration
	set mod_cnt 0
	
	#Get Portcounts and number of modules
	puts $s "c_portcounts ?"
	gets $s string
	while {[scan $string %s%n cportcount length] == 2} {
	     set cportcounts($mod_cnt) $cportcount
	      incr mod_cnt
	    set string [string range $string $length end]
	}
	set y [array size cportcounts]
	set numModules [expr $y-1]
	
	#Print out chassis information
	puts "Chassis name: 			$cname"
	puts "Comment:	 		$ccomment"
	puts "Model:				$cmodel"			
	puts "Serial no:			$cserialno"
	puts "Version no:			$cversionno"
	puts ""
	puts "Detected following modules:"
	puts "Model		FW-Version	Port Count"
	
	#Get all module models, versions and port counts
	for {set x 0} {$x<$numModules} {incr x} {
	   
	   	puts $s "$x m_model ?"
		set mmodel($x) [crop2 [gets $s] 2]
		puts $s "$x m_versionno ?"
		set mversionno($x) [crop2 [gets $s] 2]
		puts $s "$x m_versionno ?"
		set mversionno($x) [crop2 [gets $s] 2]
		set cportcounts($x) $cportcounts([expr $x+1])
	   	puts "$mmodel($x)	$mversionno($x) 		$cportcounts($x)"
	}
	puts ""
	#Reserve the ports, clear stats and reset port configurations..
	#puts $s "$tx P_RESERVATION RESERVE"
	puts "Reserve TX $tx: [P_RESERVATION $tx_mod $tx_port RESERVE $s]"
	P_RESET 0 4 $s
	puts "Clear settings and stats from TX\($tx\): [P_RESET $tx_mod $tx_port $s]"
	puts "Reserve RX $rx: [P_RESERVATION $rx_mod $rx_port RESERVE $s]"
	puts "Clear settings and stats from RX\($rx\): [P_RESET $rx_mod $rx_port $s]"
		
	
	#Create MAC learning stream on the RX port
	#This will inform the switch of the presence of the simulated hosts
	puts "Create stream for MAC learning: [PS_CREATE $rx_mod $rx_port 0 $s]"
	puts "Set TID to \"1\": [PS_TPLDID $rx_mod $rx_port 0 1 $s]"
	puts "Set Rate to $numhosts pps: [PS_RATEPPS $rx_mod $rx_port 0 $numhosts $s]"
	puts "Set header 0x00112233445500aabbcc00000800: [PS_PACKETHEADER $rx_mod $rx_port 0 0x00112233445500aabbcc00000800 $s]"
	#Set up SMAC modifier to generate packets with buttom SMAC bits = 000 -> numhosts
	puts "Set up SMAC modifier: [PS_MODIFIERCOUNT $rx_mod $rx_port 0 1 $s] [PS_MODIFIER $rx_mod $rx_port 0 0 10 0xFFFF0000 INC 1 $s] [PS_MODIFIERRANGE $rx_mod $rx_port 0 0 1 1 $numhosts $s]"
	#puts "Set number of packets $numpackets: [PS_PACKETLIMIT $rx_mod $rx_port 0 $numpackets $s]"
	puts "Set learning packet length to 64B: [PS_PACKETLENGTH $rx_mod $rx_port 0 FIXED 64 64 $s]"
	
	
	#puts $s "$tx PS_ENABLE \[0\] ON"
	puts "Enable stream: [PS_ENABLE $rx_mod $rx_port 0 ON $s]"
	
	#Create a stream on the TX port
	puts "Create stream for TX: [PS_CREATE $tx_mod $tx_port 0 $s]"
	puts "Set TID to \"1\": [PS_TPLDID $tx_mod $tx_port 0 2 $s]"
	puts "Set Rate $rate: [PS_RATEFRACTION $tx_mod $tx_port 0 $rate $s]"
	puts "Set header 0x00aabbcc00000011223344550800: [PS_PACKETHEADER $tx_mod $tx_port 0 0x00aabbcc00000011223344550800 $s]"
	#Set up SMAC modifier to generate packets with buttom SMAC bits = 000 -> numhosts
	puts "Set up DMAC modifier: [PS_MODIFIERCOUNT $tx_mod $tx_port 0 1 $s] [PS_MODIFIER $tx_mod $tx_port 0 0 4 0xFFFF0000 INC 1 $s] [PS_MODIFIERRANGE $tx_mod $tx_port 0 0 1 1 $numhosts $s]"
	#puts "Set number of packets $numpackets: [PS_PACKETLIMIT $tx_mod $tx_port 0 $numpackets $s]"
	puts "Set packet length $minsize to $maxsize: [PS_PACKETLENGTH $tx_mod $tx_port 0 RANDOM $minsize $maxsize $s]"
	
	
	puts "Enable stream: [PS_ENABLE $tx_mod $tx_port 0 ON $s]"
	
	
	#Wait 4s for ports to reinitialize after restart (just a precausion)
	after 4000
	puts "Start MAC learning on RX port: [P_TRAFFIC $rx_mod $rx_port ON $s]"
	after 4000
	#Start the traffic
	#puts $s "$tx P_TRAFFIC ON"
	puts "Start Traffic...and wait for $time seconds for it to run: [P_TRAFFIC $tx_mod $tx_port ON $s]"
	after [ expr {$time * 1000} ]
	#gets $s
	#puts [gets $s]
	
	#Stop the traffic
	puts "Stopping traffic: [P_TRAFFIC $tx_mod $tx_port OFF $s] [P_TRAFFIC $rx_mod $rx_port OFF $s]"
	after [ expr {2000} ]
	
	#Get statistics
	puts "The TX and RX statistics should be identical if test is OK:"
	puts "TX statistics: [PT_STREAM?  $tx_mod $tx_port 0 $s]"
	puts "RX statistics: [PR_TPLDTRAFFIC?  $rx_mod $rx_port 2 $s]"

	#Release ports.....
	puts "Release TX $tx: [P_RESERVATION $tx_mod $tx_port RELEASE $s]"
	puts "Release RX $tx: [P_RESERVATION $rx_mod $rx_port RELEASE $s]"

}	



############### End of runtest process. ##########################



#################################### Main code ######################################
#set logon "\"xena\""
set owner "\"tclsampl\""

#Global variables
set cportcounts(0) 0
set numModules 0

# Initial LiveDemo login..
   set s [Echo_Client $server $port]
   puts $s "c_logon $password"
   gets $s response
   puts "Loging on to $server: 	$response"
   
   #Set owner name
   puts $s "c_owner $owner"
   gets $s response
   

   if {"$response" == "<OK>"}    {runtest $s 
	   
	   }  else {puts "Unable to connect, exiting...."} 
    
   after 4000
   
   puts $s "c_logoff"
   close $s
 
