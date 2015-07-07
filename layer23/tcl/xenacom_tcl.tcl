#Xena TCL scripting library v. 0.5


# Process for string cropping
proc crop  {string index} {
	set mod_cnt 0
	while {[scan $string %s%n word length] == 2} {
	     set words($mod_cnt) $word
	      incr mod_cnt
	    set string [string range $string $length end]
	}
	return $words($index)
}

# Another process for string cropping
proc crop2  {string startindex} {
	set mod_cnt 0
	set rstring ""
	while {[scan $string %s%n word length] == 2} {
		if { $mod_cnt>=$startindex } {
			set rstring "$rstring $word" 
		}
	     set words($mod_cnt) $word
	      incr mod_cnt
	    set string [string range $string $length end]
	}
	
	return $rstring
}


#Process for running a TCP server - not used but left in for reference
proc Server {channel clientaddr clientport} {
   puts "Connection from $clientaddr registered"
   puts $channel [clock format [clock seconds]]
   close $channel
}

#Process for setting up a TCP-connection to the Xena Box. 
proc Echo_Client {host port} {
    set s [socket $host $port]
    fconfigure $s -buffering line
    return $s
}

#Process for fetching parameters and other information from the chassis
proc getparam {command s} {
	puts $s "$command ?"
	gets $s response
	return $response
}

#Process for setting operating parameters. 
proc setparam {command param s} { 
	puts $s "$command $param"
	#puts $s "c_owner \"AR\""
	gets $s response
	return $response
	#puts "$command Set: 	$response"
}

#Process for validating read/write of parameters (as c_owner etc). 
proc check_RW {command param s} {
	setparam $command $param $s
	puts $s "$command ?"
	gets $s response
	#"C_OWNER  $owner"
	if {"$response" == "$command  $param"}    {puts "$command $param verified!"
	
	}  else {puts "$command FAILED!: \[$command  $param\] \<\-\> \[$response\] "}	
}

#Process for validating read/write asymetric parameters (as c_owner etc). 
proc check_RW_asym {command param ok_response s} {
	setparam $command $param $s
	puts $s "$command ?"
	gets $s response
	#"C_OWNER  $owner"
	if {"$response" == "$ok_response"}    {puts "$command $param verified!"
	
	}  else {puts "$command FAILED!: \[$ok_response\] \<\-\> \[$response\] "}	
}

#Process for validating read/write asymetric parameters (as c_owner etc). 
proc check_R {command ok_response s} {
	puts $s "$command"
	gets $s response
	#"C_OWNER  $owner"
	if {"$response" == "$ok_response"}    {puts "$command verified!"
	
	}  else {puts "$command FAILED!: \[$ok_response\] \<\-\> \[$response\] "}	
}


#Chassis commands


#Module commands




#Port commands
proc P_RESERVATION {module port reserve s} {
	return [setparam "$module/$port P_RESERVATION" $reserve $s]
}

proc P_RESET {module port s} {
	return [setparam "$module/$port P_RESET" "" $s]
}

proc P_TRAFFIC {module port onoff s} {
	return [setparam "$module/$port P_TRAFFIC" $onoff $s]
}


#Stream commands
proc PS_CREATE {module port sid s} {return [setparam "$module/$port PS_CREATE" "\[$sid\]" $s]}

proc PS_TPLDID {module port sid tid s} {
	return [setparam "$module/$port PS_TPLDID" "\[$sid\] $tid" $s]
}

proc PS_MODIFIERCOUNT {module port sid mcount s} {
	return [setparam "$module/$port PS_MODIFIERCOUNT" "\[$sid\] $mcount" $s]
}

proc PS_MODIFIER {module port sid mid pos mask act rep s} {
	return [setparam "$module/$port PS_MODIFIER" "\[$sid,$mid\] $pos $mask $act $rep" $s]
}

proc PS_MODIFIERRANGE {module port sid mid start step stop s} {
	return [setparam "$module/$port PS_MODIFIERRANGE" "\[$sid,$mid\] $start $step $stop" $s]
}

proc PS_RATEFRACTION {module port sid rate s} {
	return [setparam "$module/$port PS_RATEFRACTION" "\[$sid\] $rate" $s]
}

proc PS_RATEPPS {module port sid pps s} {
	return [setparam "$module/$port PS_RATEPPS" "\[$sid\] $pps" $s]
}


proc PS_PACKETLIMIT {module port sid plimit s} {
	return [setparam "$module/$port PS_PACKETLIMIT" "\[$sid\] $plimit" $s]
}

proc PS_PACKETLENGTH {module port sid type min_length max_length s} {
	return [setparam "$module/$port PS_PACKETLENGTH" "\[$sid\] $type $min_length $max_length" $s]
}

proc PS_PACKETHEADER {module port sid header s} {
	return [setparam "$module/$port PS_PACKETHEADER" "\[$sid\] $header" $s]
}

proc PS_ENABLE {module port sid enable s} {
	return [setparam "$module/$port PS_ENABLE" "\[$sid\] $enable" $s]
}


#Statistics commands
proc PT_CLEAR {module port s} {
	return [setparam "$module/$port PT_CLEAR" "" $s]
}

proc PR_TPLDTRAFFIC? {module port tid s} {
	return [getparam "$module/$port PR_TPLDTRAFFIC \[$tid\]" $s]
}
proc PT_STREAM? {module port sid s} {
	return [getparam "$module/$port PT_STREAM \[$sid\]" $s]
}


#Histogram commands


#Filter commands


