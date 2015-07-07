#!/usr/bin/perl
##PERL example script for connecting to a XENA tester
# via the scripting interface.
#Version 1.0

my $chassis = '87.63.85.110';
my $port = '22611';
my $data="";
use IO::Socket;

$sock = IO::Socket::INET->new(PeerAddr => $chassis,
                                PeerPort => $port,
                                Proto    => "tcp",
				 Type     => SOCK_STREAM)
    or die "Couldn't connect to $remote_host:$remote_port : $@\n";

print "Connected to chassis.\n";


#Always remember the \n (newline) character after the commands
# to the chassis. 

# Log on to the chassis...
$data="c_logon \"xena\"";
print $sock "$data\n";
$data= <$sock>;

$data="c_owner \"PERL\"";
print $sock "$data\n";
$data= <$sock>;

#Get chassis info:
print $sock "c_model ?\n";
print $sock "c_serialno ?\n";
print $sock "c_versionno ?\n";
print $sock "c_portcounts ?\n";

#Print it out
$data= <$sock>;
print "Model: $data";
$data= <$sock>;
print "Serial: $data";
$data= <$sock>;
print "Version: $data";
$data= <$sock>;
print "Portcounts: $data";





sleep (10);
$sock->close();
