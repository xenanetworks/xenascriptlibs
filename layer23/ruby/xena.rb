require 'socket'      # Sockets are in standard library
#---------------------------------------------------------------------------------------------------------------------------------------------------GLOBALS
# This is IP is the current IP of the Xena Live Demo Unit
$hostname = '131.164.227.250'

# This is IP is the current IP used for the EXT port - edit and change to own Xena IP.
#$hostname = '172.16.255.200'
$dbg = 1

$password = '"xena"'
$owner = '"AutoRuby"'

# The CLI API TCP port used for the socket.
$port = 22611

# Tx port used for the Demo.
$tx_port = '11/0'
# Rx port used for the Demo.
$rx_port = '11/1'

# Config file used to demo config file loading - change name to load your own
# set the path or place in Ruby bin directory.
$config_file = '123.xpc' 

#---------------------------------------------------------------------------------------------------------------------------------------------------METHODS

##############################################################################################################################
# Name:              x_tx_string
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    tx_string
#                        API command that will be used.
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    General Function used to send command over the socket.
##############################################################################################################################

def x_tx_string(socket, tx_string,debug_flag)
    socket.puts(tx_string)
	response = socket.gets
	if debug_flag != 0
		puts tx_string
		puts response
	end	
		
    rescue IOError, SocketError, SystemCallError
      # eof = true
end

##############################################################################################################################
# Name:              x_connect
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Logon + Owner declaration to Xena Chassis.
##############################################################################################################################

def x_connect(socket,debug_flag)
	x_tx_string(socket,'C_LOGON '+$password,debug_flag);
	x_tx_string(socket,'C_OWNER '+$owner,debug_flag);
end

##############################################################################################################################
# Name:              x_disconnect
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Logout Xena Chassis.
##############################################################################################################################

def x_disconnect(socket,debug_flag)
	x_tx_string(socket,'C_LOGOFF',debug_flag);
end

##############################################################################################################################
# Name:              x_reserve
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be reserved (e.g. 0/1 (module 0 port 1))
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Reserve a specific port on the Xena platform.
##############################################################################################################################

def x_reserve(socket,port,debug_flag)
	x_tx_string(socket,port+' P_RESERVATION RESERVE',debug_flag);
end

###########################################################################################################################
# Name:              x_release
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be released (e.g. 0/1 (module 0 port 1))
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Releases a specific port on the Xena platform.
##############################################################################################################################

def x_release(socket,port,debug_flag)
	x_tx_string(socket,port+' P_RESERVATION RELEASE',debug_flag);
end

###########################################################################################################################
# Name:              x_load_config
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be imported to (e.g. 0/1 (module 0 port 1))
#                    file_name
#                        config file name string
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Imports a port configuration to a specified port.
##############################################################################################################################

def x_load_config(socket,port,file_name,debug_flag)
	config=File.open(file_name).read
	config.each_line do |line|
		if line[0]!=';'
			x_tx_string(socket,port+' '+line,debug_flag)
		end
	end
end

###########################################################################################################################
# Name:              x_start_traffic
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be started (e.g. 0/1 (module 0 port 1))
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Starts traffic on specified port.
##############################################################################################################################

def x_start_traffic(socket,port,debug_flag)
	x_tx_string(socket,port+' P_TRAFFIC ON',debug_flag);
end

###########################################################################################################################
# Name:              x_stop_traffic
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be stopped (e.g. 0/1 (module 0 port 1))
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Stops traffic on specified port.
##############################################################################################################################

def x_stop_traffic(socket,port,debug_flag)
	x_tx_string(socket,port+' P_TRAFFIC OFF',debug_flag);
end

###########################################################################################################################
# Name:              x_rx_total_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be queried (e.g. 0/1 (module 0 port 1))
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out port Total RX results (bps,pps,Bytes,Packets)
##############################################################################################################################

def x_rx_total_results(socket,port,debug_flag)
	socket.puts(port+' PR_TOTAL ?')
	response = socket.gets
    puts port+' PR_TOTAL ?'	
	puts '    Rx : bps='+response.split(" ")[2]+',pps='+response.split(" ")[3]+',Bytes='+response.split(" ")[4]+',Packets='+response.split(" ")[4] 
end

###########################################################################################################################
# Name:              x_tx_total_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be queried (e.g. 0/1 (module 0 port 1))
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out port Total TX results (bps,pps,Bytes,Packets)
##############################################################################################################################

def x_tx_total_results(socket,port,debug_flag)
	socket.puts(port+' PT_TOTAL ?')
	response = socket.gets
    puts port+' PT_TOTAL ?'	
	puts '    Tx : bps='+response.split(" ")[2]+',pps='+response.split(" ")[3]+',Bytes='+response.split(" ")[4]+',Packets='+response.split(" ")[4] 
end
###########################################################################################################################
# Name:              x_txrx_total_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be queried (e.g. 0/1 (module 0 port 1))
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out port Total TX and RX results (bps,pps,Bytes,Packets) by calling both functions (Rx,Tx - Results)
##############################################################################################################################

def x_txrx_total_results(socket,port,debug_flag)
	x_tx_total_results(socket,port,debug_flag)
	x_rx_total_results(socket,port,debug_flag)
end

###########################################################################################################################
# Name:              x_rx_notpld_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be queried (e.g. 0/1 (module 0 port 1))
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out port "No Test Payload" RX results (bps,pps,Bytes,Packets)
##############################################################################################################################

def x_rx_notpld_results(socket,port,debug_flag)
	socket.puts(port+' PR_NOTPLD ?')
	response = socket.gets
    puts port+' PR_NOTPLD ?'	
	puts '    Rx : bps='+response.split(" ")[2]+',pps='+response.split(" ")[3]+',Bytes='+response.split(" ")[4]+',Packets='+response.split(" ")[4] 
end

###########################################################################################################################
# Name:              x_tx_notpld_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be queried (e.g. 0/1 (module 0 port 1))
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out port "No Test Payload" TX results (bps,pps,Bytes,Packets)
##############################################################################################################################

def x_tx_notpld_results(socket,port,debug_flag)
	socket.puts(port+' PT_NOTPLD ?')
	response = socket.gets
    puts port+' PT_NOTPLD ?'	
	puts '    Tx : bps='+response.split(" ")[2]+',pps='+response.split(" ")[3]+',Bytes='+response.split(" ")[4]+',Packets='+response.split(" ")[4] 
end

###########################################################################################################################
# Name:              x_txrx_notpld_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be queried (e.g. 0/1 (module 0 port 1))
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out port "No Test Payload" TX and Rx  results (bps,pps,Bytes,Packets) by calling both functions (Rx,Tx - Results)
##############################################################################################################################

def x_txrx_notpld_results(socket,port,debug_flag)
	x_tx_notpld_results(socket,port,debug_flag)
	x_rx_notpld_results(socket,port,debug_flag)
end

###########################################################################################################################
# Name:              x_rx_extra_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be queried (e.g. 0/1 (module 0 port 1))
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out port "Extra" RX results (FCS errors,Pause Frames,ARP Requests,ARP Replies,PING Requests,PING Replies,GAP Count,Gap Duration)
##############################################################################################################################

def x_rx_extra_results(socket,port,debug_flag)
	socket.puts(port+' PR_EXTRA ?')
	response = socket.gets
    puts port+' PR_EXTRA ?'	
	puts '    FCS errors='+response.split(" ")[2]+',Pause Frames='+response.split(" ")[3]+',ARP Requests='+response.split(" ")[4]+',ARP Replies='+response.split(" ")[4]+',PING Requests='+response.split(" ")[5]+',PING Replies='+response.split(" ")[6]+',GAP Count='+response.split(" ")[7]+',Gap Duration='+response.split(" ")[8]    
end

###########################################################################################################################
# Name:              x_tx_extra_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be queried (e.g. 0/1 (module 0 port 1))
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out port "Extra" TX results (ARP Requests,ARP Replies,PING Requests,PING Replies,Injected FCS,
#                    Injected Sequence Err,Injected Misorder Err,Injected Integrity Err,Injected TID Err,MAC Training)
##############################################################################################################################

def x_tx_extra_results(socket,port,debug_flag)
	socket.puts(port+' PT_EXTRA ?')
	response = socket.gets
    puts port+' PT_EXTRA ?'	
	puts '    ARP Requests='+response.split(" ")[2]+',ARP Replies='+response.split(" ")[3]+',PING Requests='+response.split(" ")[4]+',PING Replies='+response.split(" ")[5]+',Injected FCS='+response.split(" ")[6]+',Injected Sequence Err='+response.split(" ")[7]+',Injected Misorder Err='+response.split(" ")[8]+',Injected Integrity Err='+response.split(" ")[9]+',Injected TID Err='+response.split(" ")[10]+',MAC Training='+response.split(" ")[11]     
end

###########################################################################################################################
# Name:              x_txrx_extra_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be queried (e.g. 0/1 (module 0 port 1))
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out port "Extra" TX and results 
#                    TX:
#                       ARP Requests,ARP Replies,PING Requests,PING Replies,Injected FCS,Injected Sequence Err
#                       Injected Misorder Err,Injected Integrity Err,Injected TID Err,MAC Training
#                    RX:
#                       FCS errors,Pause Frames,ARP Requests,ARP Replies,PING Requests,PING Replies,GAP Count,Gap Duration
##############################################################################################################################

def x_txrx_extra_results(socket,port,debug_flag)
	x_tx_extra_results(socket,port,debug_flag)
	x_rx_extra_results(socket,port,debug_flag)
end

###########################################################################################################################
# Name:              x_rx_tpldtraffic_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be queried (e.g. 0/1 (module 0 port 1))
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out port Only "Test Payload" RX results (bps,pps,Bytes,Packets)
##############################################################################################################################

def x_rx_tpldtraffic_results(socket,port,tid,debug_flag)
	socket.puts(port+' PR_TPLDTRAFFIC ['+tid+'] ?')
	response = socket.gets
    puts port+' PR_TPLDTRAFFIC ['+tid+'] ?'
	puts '    Stream Rx : bps='+response.split(" ")[3]+',pps='+response.split(" ")[4]+',Bytes='+response.split(" ")[5]+',Packets='+response.split(" ")[6] 
end

###########################################################################################################################
# Name:              x_tx_tpldtraffic_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to queried (e.g. 0/1 (module 0 port 1))
#                    Tid
#                        Test-Payload ID of the stream.
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out port Only "Test Payload" TX results (bps,pps,Bytes,Packets)
##############################################################################################################################

def x_tx_tpldtraffic_results(socket,port,tid,debug_flag)
	socket.puts(port+' PT_STREAM ['+tid+'] ?')
	response = socket.gets
    puts port+' PT_STREAM ['+tid+'] ?'
	puts response	
	puts '    Stream Tx : bps='+response.split(" ")[3]+',pps='+response.split(" ")[4]+',Bytes='+response.split(" ")[5]+',Packets='+response.split(" ")[6] 
end

###########################################################################################################################
# Name:              x_txrx_tpldtraffic_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    tx_port
#                        Transmit port (e.g. 0/1 (module 0 port 1))
#                    rx_port
#                        Receive port (e.g. 0/2 (module 0 port 2))
#                    Tid
#                        Test-Payload ID of the stream.
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out stream(tid)  TX and RX results (bps,pps,Bytes,Packets)
##############################################################################################################################

def x_txrx_tpldtraffic_results(socket,tx_port,rx_port,tid,debug_flag)
	x_tx_tpldtraffic_results(socket,tx_port,tid,debug_flag)
	x_rx_tpldtraffic_results(socket,rx_port,tid,debug_flag)
end

###########################################################################################################################
# Name:              x_rx_tplderrors_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be queried (e.g. 0/1 (module 0 port 1))
#                    Tid
#                        Test-Payload ID of the stream.
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out stream(tid) "Test Payload Errors" RX results (Lost Packets,Misordered Packets,Payload Errors)
##############################################################################################################################

def x_rx_tplderrors_results(socket,port,tid,debug_flag)
	socket.puts(port+' PR_TPLDERRORS ['+tid+'] ?')
	response = socket.gets
    puts port+' PR_TPLDERRORS ['+tid+'] ?'
	puts '    Errors : Lost Packets='+response.split(" ")[4]+',Misordered Packets='+response.split(" ")[5]+',Payload Errors='+response.split(" ")[6] 
end

###########################################################################################################################
# Name:              x_rx_tpldlatency_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be queried (e.g. 0/1 (module 0 port 1))
#                    Tid
#                        Test-Payload ID of the stream.
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out stream(tid) Latency RX results (min,avg,max,1SecAvg)
##############################################################################################################################

def x_rx_tpldlatency_results(socket,port,tid,debug_flag)
	socket.puts(port+' PR_TPLDLATENCY ['+tid+'] ?')
	response = socket.gets
    puts port+' PR_TPLDLATENCY ['+tid+'] ?'
	puts '    Latency : Min='+response.split(" ")[3]+',Avg='+response.split(" ")[4]+',Max='+response.split(" ")[5]+',1SecAvg='+response.split(" ")[6] 
end

###########################################################################################################################
# Name:              x_rx_tpldjitter_results
# Input Parameters:  
#                    socket
#                        Used handle to communicate with Xena.
#                    Port
#                        a string that defines the port needed to be queried (e.g. 0/1 (module 0 port 1))
#                    Tid
#                        Test-Payload ID of the stream.
#                    debug_flag
#                        Flag to indicate whether or not the Method shall output the actual command sent/received.
# Output:
#					 Void (prints to screen the requested command input/output)	
# Description:
#                    Prints out stream(tid) RX Jitter results (min,avg,max,1SecAvg)
##############################################################################################################################
def x_rx_tpldjitter_results(socket,port,tid,debug_flag)
	socket.puts(port+' PR_TPLDJITTER ['+tid+'] ?')
	response = socket.gets
    puts port+' PR_TPLDJITTER ['+tid+'] ?'
	puts '    Jitter : Min='+response.split(" ")[3]+',Avg='+response.split(" ")[4]+',Max='+response.split(" ")[5]+',1SecAvg='+response.split(" ")[6] 
end

#---------------------------------------------------------------------------------------------------------------------------------------------------MAIN 

#Create a socket and save handle to "s"
s = TCPSocket.open($hostname, $port)

# Connect(+logon) + Reserve both Tx and Rx ports + Load a config to Port Tx + start the traffic.
x_connect(s,$dbg)
x_reserve(s,$tx_port,$dbg)
x_reserve(s,$rx_port,$dbg)
x_load_config(s,$tx_port,$config_file,0)
x_start_traffic(s,$tx_port,$dbg)

# Delay...
sleep 1
print '.'
sleep 1
print '.'
sleep 1
print '.'
sleep 1
print '.'
sleep 1
puts '.'

# Print port results
x_txrx_total_results(s,$tx_port,$dbg)
x_txrx_notpld_results(s,$tx_port,$dbg)
x_txrx_extra_results(s,$tx_port,$dbg)

# Print TID results
x_txrx_tpldtraffic_results(s,$tx_port,$rx_port,'0',$dbg)

# Print TID errors,latency,jitter results
x_rx_tplderrors_results(s,$tx_port,'0',$dbg)
x_rx_tpldlatency_results(s,$tx_port,'0',$dbg)
x_rx_tpldjitter_results(s,$tx_port,'0',$dbg)

# Release ports and disconnect
x_release(s,$tx_port,$dbg)
x_release(s,$rx_port,$dbg)
x_disconnect(s,$dbg)

# Close and Release socket handle
s.close               # Close the socket when done