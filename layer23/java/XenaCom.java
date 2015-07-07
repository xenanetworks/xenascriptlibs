/*************************************************************************************************************
 * 
 * 		Name:			XenaCom.java
 * 		Version: 		1.0
 * 		Author:			AR
 * 		Description:	Functions for communicating with a Xena Networks tester via scripting commands. 
 * 		
 ************************************************************************************************************/

package xena;
import java.io.*;
import java.net.*;
//import java.util.ArrayList;

import javax.swing.JOptionPane;

public class XenaCom {

	private Socket socket = null;
	PrintWriter out;
	BufferedReader in;
	//Xena owner;
	public boolean cmdtrace=false;
	
	//public void setOwner(Xena xena)
	//{
		//owner = xena;
	//} 
	
	/**********************************************************************************
	 * 					Functions for general communication with the chassis
	 * ********************************************************************************/
	
	public void command(int module,int port,int _sid,String cmd,String param,int param1,int param2) throws Exception
	{
		command(String.format("%d/%d %s [%d] %s %d %d",module,port,cmd,_sid,param,param1,param2));
	}
	public void command(int module,int port,int _sid,String cmd,String param) throws Exception
	{
		command(String.format("%d/%d %s [%d] \"%s\"",module,port,cmd,_sid,param));
	}
	public void command(int module,int port,int _sid,String cmd,int param1,int param2) throws Exception
	{
		command(String.format("%d/%d %s [%d] %d %d",module,port,cmd,_sid,param1,param2));
	}
	
	public void command(int module,int port,int _sid,String cmd,int param) throws Exception
	{
		command(String.format("%d/%d %s [%d] %d",module,port,cmd,_sid,param));
	}
	
	public void command(int module,int port,int _sid,String cmd) throws Exception
	{
		command(String.format("%d/%d %s [%d]",module,port,cmd,_sid));
	}
	
	public void command(int module,int port,String cmd,boolean onoff) throws Exception
	{
		command(String.format("%d/%d %s %s",module,port,cmd,onoff ? "ON":"OFF"));
	}
	
	public void command(int module,int port,int did, String cmd,boolean onoff) throws Exception
	{
		command(String.format("%d/%d %s [%d] %s",module,port,cmd,did,onoff ? "ON":"OFF"));
	}
	public void command(int module,int port,String cmd,String param) throws Exception
	{
		command(String.format("%d/%d %s \"%s\"",module,port,cmd,param));
	}	
	public void command(int module,int port,String cmd) throws Exception
	{
		command(String.format("%d/%d %s",module,port,cmd));
	}
	
	public void command(String cmd,boolean onoff) throws Exception
	{
		command(cmd + " " + (onoff ? "ON":"OFF"));
	}

	public void command(String cmd,String str) throws Exception
	{
		command(cmd + " \"" +str + "\"");
	}

	private void commandWithException(String cmd) throws Exception
	{
		if(cmdtrace){System.out.println("Xena command: "+ cmd);}
		out.println(cmd);
		String info;
		do
		{
			Thread.sleep(10);
			info = in.readLine();
		} while (info == null);
		if(cmdtrace){System.out.println("Xena response: "+ info);}
		if (!info.contains("<OK>"))
		{
			//JOptionPane.showInputDialog("Xena failure");
			throw new Exception(String.format("Xena Failure. command='%s' response='%s'",cmd,info));
		}
	}
	
	public void command(String cmd) throws Exception
	{
		try
		{
			commandWithException(cmd);
		} catch (SocketException e) {
			//owner.reconnect();
			commandWithException(cmd);
		}
	}

	
	
	public String ask(int module,int port,int sid,String cmd) throws Exception
	{
		return ask(module,port,String.format("%s [%d]",cmd,sid));
	}
	
	public String ask(int module,int port,String cmd) throws Exception
	{
		String full_command = String.format("%d/%d %s",module,port,cmd);
		return ask(full_command);
	}
	
	private String askWithException(String cmd) throws Exception
	{	
		String full_command = String.format("%s ?",cmd);
		if(cmdtrace){System.out.println("Xena ask: " +full_command);}
		out.println(full_command);
		String info;
		do
		{
			Thread.sleep(100);
			info = in.readLine();
		} while (info == null);
		info = info.replaceAll("\\s+"," ");
		if(cmdtrace){System.out.println("Xena response: " + info);}
		// the return values contains the command and then comes the response
		if (!info.startsWith(cmd))
		{
			JOptionPane.showInputDialog("Xena failure");
			throw new Exception(String.format(
					"Xena Failure. command='%s' response='%s'", full_command, info));
		}
		return info.substring(cmd.length()).trim();		
	}

	private String ask(String cmd) throws Exception
	{
		try
		{
			return askWithException(cmd);
		} catch (SocketException e) {
			//owner.reconnect();
			return askWithException(cmd);
		}
	}


	public boolean askbool(int module,int port,int sid,String cmd) throws Exception
	{	
		String ret = ask(module,port,sid,cmd);
		if (ret.contains("ON"))
			return true;
		return false;
	}
	public boolean askbool(int module,int port,String cmd) throws Exception
	{	
		String ret = ask(module,port,cmd);
		if (ret.contains("ON"))
			return true;
		return false;
	}	
	
	public boolean askbool(String cmd) throws Exception
	{	
		String ret = ask(cmd);
		if (ret.contains("ON"))
			return true;
		return false;
	}
	
	public int askInt(String cmd) throws Exception
	{	
		String ret = ask(cmd);
		return Integer.parseInt(ret);
	}
	
	public int askInt(int module,int port,String cmd) throws Exception
	{	
		String ret = ask(module,port,cmd);
		return Integer.parseInt(ret);
	}
	
	public int askInt(int module,int port,int sid,String cmd) throws Exception
	{
		return Integer.parseInt(ask(module,port,String.format("%s [%d]",cmd,sid)));
	}
	
	public int[] askIntArray(String cmd,int offset) throws Exception
	{	
		String[] ret = ask(cmd).trim().split("  ");
		int[] answer=new int[ret.length-offset];
		for (int i=0;i<ret.length-offset;i++)
		{answer[i]=Integer.parseInt(ret[i+offset]);}
		return answer;
	}
	
	public int[] askIntArray(int module,int port,String cmd,int offset) throws Exception
	{	
		String[] ret = ask(module,port,cmd).trim().split("  ");
		int[] answer=new int[ret.length-offset];
		for (int i=0;i<ret.length-offset;i++)
		{answer[i]=Integer.parseInt(ret[i+offset]);}
		return answer;
	}
	
	public long[] askLongArray(int module,int port,String cmd,int offset) throws Exception
	{	
		String[] ret = ask(module,port,cmd).trim().split("  ");
		long[] answer=new long[ret.length-offset];
		for (int i=0;i<ret.length-offset;i++)
		{answer[i]=Long.parseLong(ret[i+offset]);}
		return answer;
	}
	
	/* 
	 * 	Below follows functions for setting and receiving parameters:
	 * 	Chassis parameters, Module parameters, Port parameters,
	 *  Stream parameters, Filter and terms parameters, Capture parameters, 
	 *  Statistics parameters, Dataset(histogram) parameters and 40/100G parameters. 
	 *  
	 *  The naming and the order of the functions generally follow that of the Xena Scripting
	 *  manual: http://www.xenanetworks.com/Xena_Scripting.pdf  
	 * 
	 */
	
	
	/**********************************************************************************
	 * 					Chassis parameters
	 * ********************************************************************************/

	public void C_CONNECT(String ipaddr) throws Exception {
		socket = new Socket(ipaddr, 22611); // IP of Xena +
		socket.setKeepAlive(true); 
		out = new PrintWriter(socket.getOutputStream(), true);
		in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
	}

	public void C_DISCONNECT() {
		if (socket != null)
		{
			try {
				socket.close();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			socket = null;
			in = null;
			out = null;
		}
	}

	public void C_LOGON( String _pwd) throws Exception 
	{
		command("C_LOGON",_pwd);
	}
	
	public void C_LOGOFF() throws Exception 
	{
		command("C_LOGOFF");
	}

	public void C_OWNER( String _username) throws Exception 
	{
		command("C_OWNER",_username);
	}

	public String C_OWNER() throws Exception 
	{
		return ask("C_LOGON");
	}

	public String C_KEEPALIVE() throws Exception 
	{
		return ask("C_KEEPALIVE");
	}

	public String C_RESERVEDBY() throws Exception 
	{
		return ask("C_RESERVEDBY");
	}
	
	public String C_MODEL() throws Exception 
	{
		return ask("C_MODEL");
	}
	
	public String C_PORTCONTS() throws Exception 
	{
		return ask("C_PORTCONTS");
	}
	
	public String C_CAPABILITIES() throws Exception 
	{
		return ask("C_CAPABILITIES");
	}

	public String C_SERIALNO() throws Exception 
	{
		return ask("C_SERIALNO");
	}	

	public String C_VERSIONNO() throws Exception 
	{
		return ask("C_VERSIONNO");
	}	

	public String C_NAME() throws Exception 
	{
		return ask("C_NAME");
	}	

	public void C_NAME( String _chassisname) throws Exception 
	{
		command("C_NAME" ,_chassisname);
	}

	public String C_COMMENT() throws Exception 
	{
		return ask("C_COMMENT");
	}	

	public void C_COMMENT( String _comment) throws Exception 
	{
		command("C_COMMENT" ,_comment);
	}

	public String C_PASSWORD() throws Exception 
	{
		return ask("C_PASSWORD");
	}	
	
	public void C_PASSWORD( String _password) throws Exception 
	{
		command("C_COMMENT" ,_password);
	}

	public String C_IPADDRESS() throws Exception 
	{
		return ask("C_IPADDRESS");
	}	
	
	public void C_IPADDRESS( String _ipaddr, String _mask, String _gw) throws Exception 
	{
		command("C_IPADDRESS " +_ipaddr + " " + _mask + " " + _gw);
	}

	
	public String C_INDICES() throws Exception 
	{
		return ask("C_INDICES");
	}

	public void C_DOWN(String _shutdownrestart)  throws Exception 
	{
		command("C_DOWN -1480937026" ,_shutdownrestart);
	}

	public void C_RESERVE()  throws Exception 
	{
		command("C_RESERVATION RESERVE");
	}
	
	public void C_RELEASE()  throws Exception 
	{
		command("C_RESERVATION RELEASE");
	}
	public void C_RELINQUISH()  throws Exception 
	{
		command("C_RESERVATION RELINQUISH");
	}	
	
	
	/**********************************************************************************
	 * 					Module parameters
	 * ********************************************************************************/
	public void M_RESERVE()  throws Exception 
	{
		command("M_RESERVATION RESERVE");
	}
	
	public void M_RELEASE()  throws Exception 
	{
		command("M_RESERVATION RELEASE");
	}
	
	public void M_RELINQUISH()  throws Exception 
	{
		command("M_RESERVATION RELINQUISH");
	}
	
	public String M_RESERVEDBY() throws Exception 
	{
		return ask("M_RESERVEDBY");
	}
	
	public String M_MODEL() throws Exception 
	{
		return ask("M_MODEL");
	}
	
	public int M_SERIALNO() throws Exception 
	{
		return askInt("M_SERIALNO");
	}
	
	public int M_VERSIONNO() throws Exception 
	{
		return askInt("M_VERSIONNO");
	}
	
	public void M_TIMESYNC(String _syncmode) throws Exception 
	{
		command("M_TIMESYNC" ,_syncmode);
	}
	
	public String M_TIMESYNC() throws Exception 
	{
		return ask("M_TIMESYNC");
	}
	
	public int M_STATUS() throws Exception 
	{
		return askInt("M_STATUS");
	}
	
	public String M_CFPTYPE() throws Exception 
	{
		return ask("M_CFPTYPE");
	}
	
	public void M_CFPCONFIG(int module, int ports, int speed) throws Exception 
	{
		
		command(""+module +"  "+"M_CFPCONFIG  "+ports+"  "+speed);
	}

	public int[] M_CFPCONFIG(int module) throws Exception 
	{
		return askIntArray(""+module+"  M_CFPCONFIG",2);
	}
	
	/* Image upgrade commands have been purposely left out */
	
	
	
	

	/**********************************************************************************
	 * 					Port parameters
	 * ********************************************************************************/

	public void P_RESERVE( int _module, int _port)  throws Exception
	{
		command(_module,_port,"P_RESERVATION RESERVE");
	}
	public void P_RELEASE( int _module, int _port)  throws Exception
	{
		command(_module,_port,"P_RESERVATION RELEASE");
	}
	
	public void P_RELINQUISH( int _module, int _port)  throws Exception
	{
		command(_module,_port,"P_RESERVATION RELINQUISH");
	}
	
	public String P_RSERVEDBY( int _module, int _port) throws Exception {
		return ask(_module,_port,"P_RSERVEDBY");
	}

	public void P_RESET( int _module, int _port)  throws Exception
	{
		command(_module,_port,"P_RESET");
	}

	public String P_COMMENT( int _module, int _port)  throws Exception
	{
		return ask (_module,_port,"P_COMMENT");
	}

	public void P_COMMENT( int _module, int _port,String _comment)  throws Exception
	{
		command(_module,_port,"P_COMMENT",_comment);
	}


	public boolean P_TRAFFIC( int _module, int _port)  throws Exception
	{
		return askbool(_module,_port,"P_TRAFFIC");
	}

	public void P_TRAFFIC( int _module, int _port,boolean onoff) throws Exception
	{
		command(_module,_port,"P_TRAFFIC",onoff);
	}
	
	public int P_SPEED( int _module, int _port) throws Exception
	{
		return askInt(_module,_port,"P_SPEED");
	}
	

	public void P_SPEED( int _module, int _port,int speed) throws Exception
	{
		String param = "AUTO";
		switch (speed) {
		case 10: 
			param = "F10M";
			break;
		case 100: 
			param = "F100M";
			break;
		case 1000: 
			param = "F1G";
			break;
		default:
			break;
		}
		command(_module,_port,"P_SPEEDSELECTION " + param);
	}

	public boolean P_SYNC( int _module, int _port) throws Exception
	{
		String ret =  ask(_module,_port,"P_RECEIVESYNC");
		return ret.contains("IN_SYNC") ? true:false;
			
	}
	
	public String P_LOOPBACK( int _module, int _port)  throws Exception
	{
		return ask (_module,_port,"P_LOOPBACK");
	}
	
	public void P_LOOPBACK( int _module, int _port,String _loopmode)  throws Exception
	{
		command(_module,_port,"P_LOOPBACK",_loopmode);
	}

	public void P_LOOPBACK( int _module, int _port,int _loopmode)  throws Exception
	{
		String param="NONE";
		switch (_loopmode) {
		case 1: 
			param = "L1RX2TX";
			break;
		case 2: 
			param = "L2RX2TX";
			break;
		case 3: 
			param = "TXON2RX";
			break;
		case 4:
			param = "TXOFF2RX";
			break;
		default:
			break;
		}	
		command(_module,_port,"P_LOOPBACK",param);
	}
	
	public boolean P_CAPTURE( int _module, int _port)  throws Exception
	{
		return askbool(_module,_port,"P_CAPTURE");
	}

	public void P_CAPTURE( int _module, int _port,boolean onoff) throws Exception
	{
		command(_module,_port,"P_CAPTURE",onoff);
	}
	

	/**********************************************************************************
	 * 					Stream parameters
	 * ********************************************************************************/
	
	public String PS_INDICES( int _module, int _port) throws Exception
	{
		return ask(_module,_port,"PS_INDICES");
	}
	
	public void PS_CREATE(  int _module, int _port, int _sid) throws Exception
	{
		command(_module,_port,_sid,"PS_CREATE");
	}

	public void PS_DELETE(  int _module, int _port, int _sid) throws Exception
	{
		command(_module,_port,_sid,"PS_DELETE");
	}

	public void PS_ENABLE(  int _module, int _port, int _sid, String enable) throws Exception
	{
		command(String.format("%d/%d PS_ENABLE [%d] %s",_module,_port,_sid, enable));
	}

	public boolean PS_ENABLE(  int _module, int _port, int _sid) throws Exception
	{
		return askbool(_module,_port,_sid,"PS_ENABLE");
	}

	public String PS_PACKETLIMIT( int _module, int _port,int _sid) throws Exception
	{
		return ask(_module,_port,_sid,"PS_PACKETLIMIT");
	}

	public void PS_PACKETLIMIT( int _module, int _port,int _sid, int _count) throws Exception
	{
		command(_module,_port,_sid,"PS_PACKETLIMIT",_count);
	}

	public String PS_COMMENT( int _module, int _port,int _sid) throws Exception
	{
		return ask(_module,_port,_sid,"PS_COMMENT");
	}

	public void PS_COMMENT( int _module, int _port,int _sid, String _comment)  throws Exception
	{
		 command(_module,_port,_sid,"PS_COMMENT",_comment);
	}

	public String PS_TPLDID( int _module, int _port,int _sid) throws Exception
	{
		return ask(_module,_port,_sid,"PS_TPLDID");
	}

	public void PS_TPLDID( int _module, int _port,int _sid, int _tpldid)  throws Exception
	{
		 command(_module,_port,_sid,"PS_TPLDID",_tpldid);
	}
	
	public void PS_INSERTFCS(  int _module, int _port, int _sid,boolean enable) throws Exception
	{
		command(String.format("%d/%d PS_INSERTFCS [%d] %s",_module,_port,_sid,enable ? "ON":"SUPRESS"));
	}

	public boolean PS_INSERTFCS(  int _module, int _port, int _sid) throws Exception
	{
		return askbool(_module,_port,_sid,"PS_INSERTFCS");
	}

	/*TODO
	PS_ARPREQUEST [sid] macaddress
	PS_PINGREQUEST [sid] delay ttl	
	*/
	public String PS_RATEFRACTION( int _module, int _port,int _sid) throws Exception
	{
		return ask(_module,_port,_sid,"PS_RATEFRACTION");
	}

	public void PS_RATEFRACTION( int _module, int _port,int _sid, int _fraction)  throws Exception
	{
		 command(_module,_port,_sid,"PS_RATEFRACTION",_fraction);
	}

	public String PS_RATEPPS( int _module, int _port,int _sid) throws Exception
	{
		return ask(_module,_port,_sid,"PS_RATEPPS");
	}

	public void PS_RATEPPS( int _module, int _port,int _sid, int _pps)  throws Exception
	{
		 command(_module,_port,_sid,"PS_RATEPPS",_pps);
	}

	public String PS_RATEL2BPS( int _module, int _port,int _sid) throws Exception
	{
		return ask(_module,_port,_sid,"PS_RATEL2BPS");
	}


	public void PS_RATEL2BPS( int _module, int _port,int _sid, int _bps)  throws Exception
	{
		 command(_module,_port,_sid,"PS_RATEL2BPS",_bps);
	}

	public String PS_RATE( int _module, int _port,int _sid) throws Exception
	{
		return ask(_module,_port,_sid,"PS_RATE");
	}
	public String PS_BURST( int _module, int _port,int _sid) throws Exception
	{
		return ask(_module,_port,_sid,"PS_BURST");
	}
	
	public void PS_BURST( int _module, int _port,int _sid, int _size,int _density)  throws Exception
	{
		 command(_module,_port,_sid,"PS_BURST",_size,_density);
	}
	
	public String PS_PACKETHEADER( int _module, int _port,int _sid) throws Exception
	{
		return ask(_module,_port,_sid,"PS_PACKETHEADER");
	}

	public void PS_PACKETHEADER( int _module, int _port,int _sid,String data)  throws Exception
	{
		 command(String.format("%d/%d PS_PACKETHEADER [%d] %s",_module,_port,_sid,data));
	}

	public String PS_HEADERPROTOCOL( int _module, int _port,int _sid) throws Exception
	{
		return ask(_module,_port,_sid,"PS_HEADERPROTOCOL");
	}

	public void PS_HEADERPROTOCOL( int _module, int _port,int _sid,String data)  throws Exception
	{
		 command(String.format("%d/%d PS_HEADERPROTOCOL [%d] %s",_module,_port,_sid,data));
	}	
	
	public String PS_MODIFIERCOUNT( int _module, int _port,int _sid) throws Exception
	{
		return ask(_module,_port,_sid,"PS_MODIFIERCOUNT");
	}

	public void PS_MODIFIERCOUNT( int _module, int _port,int _sid, int _count)  throws Exception
	{
		 command(_module,_port,_sid,"PS_MODIFIERCOUNT",_count);
	}
	
	public String PS_MODIFIER( int _module, int _port,int _sid, int _mid) throws Exception
	{
		String cmd = String.format("PS_MODIFIERCOUNT  [%d,%d]",_sid,_mid);
		return ask(_module,_port,cmd);
	}

	public void PS_MODIFIER( int _module, int _port,int _sid, int _mid, int _pos, String _mask, String _act, int _rep)  throws Exception
	{
		String cmd = String.format("PS_MODIFIERCOUNT  [%d,%d]  %d  %s  %s  %d",_sid,_mid,_pos,_mask,_act,_rep);
		 command(_module,_port,cmd);
	}
	
	public String PS_MODIFIERRANGE( int _module, int _port,int _sid, int _mid) throws Exception
	{
		String cmd = String.format("PS_MODIFIERRANGE  [%d,%d]",_sid,_mid);
		return ask(_module,_port,cmd);
	}

	public void PS_MODIFIERRANGE( int _module, int _port,int _sid, int _mid, int _start,int _step,int _stop)  throws Exception
	{
		String cmd = String.format("PS_MODIFIERRANGE  [%d,%d]  %d  %d  %d",_sid,_mid,_start,_step,_stop);
		 command(_module,_port,cmd);
	}

	public void PS_PACKETLENGTH( int _module, int _port,int _sid,String type, int _min, int _max)  throws Exception
	{
		 command(_module,_port,_sid,"PS_PACKETLENGTH",type,_min,_max);
	}

	public String PS_PACKETLENGTH( int _module, int _port,int _sid) throws Exception
	{
		return ask(_module,_port,_sid,"PS_PACKETLENGTH");
	}

	public String PS_PAYLOAD( int _module, int _port,int _sid) throws Exception
	{
		return ask(_module,_port,_sid,"PS_PAYLOAD");
	}
	
	public void PS_PAYLOAD( int _module, int _port,int _sid, String _type, String _hex)  throws Exception
	{
		String cmd = String.format("%d/%d  PS_PAYLOAD [%d]  %s  %s",_module, _port, _sid,_type,_hex);
		command(_module,_port,cmd);
	}
	
	public void PS_INJECTFCSERR( int _module, int _port,int _sid)  throws Exception
	{
		command(_module,_port,_sid,"PS_INJECTFCSERR");
	}
	
	public void PS_INJECTSEQERR( int _module, int _port,int _sid)  throws Exception
	{
		command(_module,_port,_sid,"PS_INJECTSEQERR");
	}
	
	public void PS_INJECTMISERR( int _module, int _port,int _sid)  throws Exception
	{
		command(_module,_port,_sid,"PS_INJECTMISERR");
	}
	
	public void PS_INJECTPLDERR( int _module, int _port,int _sid)  throws Exception
	{
		command(_module,_port,_sid,"PS_INJECTPLDERR");
	}
	
	public void PS_INJECTTPLDERR( int _module, int _port,int _sid)  throws Exception
	{
		command(_module,_port,_sid,"PS_INJECTTPLDERR");
	}
		
	public int PS_COUNT( int _module, int _port) throws Exception
	{
		String str = PS_INDICES(_module,_port).trim();
		if (str.isEmpty())
			return 0;
		String sp[] = str.split(" ");
		return sp.length;
	}	
	
	
	/**********************************************************************************
	 * 					Filter and terms parameters
	 * ********************************************************************************/
	public void PM_CREATE( int _module, int _port,int _mid)  throws Exception
	{
		command(_module,_port,_mid,"PM_CREATE");
	}
	
	public void PM_DELETE( int _module, int _port,int _mid)  throws Exception
	{
		command(_module,_port,_mid,"PM_DELETE");
	}
	
	public String PM_PROTOCOL( int _module, int _port,int _mid)  throws Exception
	{
		return ask(_module,_port,_mid,"PM_PROTOCOL");
	}
	
	public void PM_PROTOCOL( int _module, int _port,int _mid,String _segments)  throws Exception
	{
		command(String.format("%d/%d  %s  [%d]  %s",_module,_port,"PM_PROTOCOL",_mid,_segments));
	}
	
	public int PM_POSITION( int _module, int _port,int _mid)  throws Exception
	{
		return askInt(_module,_port,_mid,"PM_POSITION");
	}
	
	public void PM_POSITION( int _module, int _port,int _mid,int _byteoffset)  throws Exception
	{
		command(String.format("%d/%d  %s  [%d]  %d",_module,_port,"PM_POSITION",_mid,_byteoffset));
	}
	
	public String PM_MATCH( int _module, int _port,int _mid)  throws Exception
	{
		return ask(_module,_port,_mid,"PM_MATCH");
	}
	
	public void PM_MATCH( int _module, int _port,int _mid,String _mask, String _value)  throws Exception
	{
		command(String.format("%d/%d  %s  [%d]  %s  %s",_module,_port,"PM_MATCH",_mid,_mask,_value));
	}
	
	public void PL_CREATE( int _module, int _port,int _lid)  throws Exception
	{
		command(_module,_port,_lid,"PL_CREATE");
	}
	
	public void PL_DELETE( int _module, int _port,int _lid)  throws Exception
	{
		command(_module,_port,_lid,"PL_DELETE");
	}
	
	public String PL_LENGTH( int _module, int _port,int _lid)  throws Exception
	{
		return ask(_module,_port,_lid,"PL_LENGTH");
	}
	
	public void PL_LENGTH( int _module, int _port,int _lid, String _type, int _size)  throws Exception
	{
		command(String.format("%d/%d  %s  [%d]  %s  %d",_module,_port,"PL_LENGTH",_lid,_type,_size));
	}
	
	public void PF_CREATE( int _module, int _port,int _fid)  throws Exception
	{
		command(_module,_port,_fid,"PF_CREATE");
	}
	
	public void PF_DELETE( int _module, int _port,int _fid)  throws Exception
	{
		command(_module,_port,_fid,"PF_DELETE");
	}
	
	public boolean PF_ENABLE( int _module, int _port,int _fid)  throws Exception
	{
		return askbool(_module,_port,_fid,"PF_ENABLE");
	}
	
	public void PF_ENABLE( int _module, int _port,int _fid,boolean _enable)  throws Exception
	{
		command(_module,_port,"PF_ENABLE",_enable);
	}
	
	public String PF_COMMENT( int _module, int _port,int _fid)  throws Exception
	{
		return ask(_module,_port,_fid,"PF_COMMENT");
	}
	
	public void PF_COMMENT( int _module, int _port,int _fid,String _comment)  throws Exception
	{
		command(_module,_port,"PF_COMMENT",_comment);
	}
	
	public String PF_CONDITION( int _module, int _port,int _fid)  throws Exception
	{
		return ask(_module,_port,_fid,"PF_CONDITION");
	}
	
	public void PF_CONDITION( int _module, int _port,int _fid,String _condition)  throws Exception
	{
		command(_module,_port,"PF_CONDITION",_condition);
	}
	
	/**********************************************************************************
	 * 					Capture parameters
	 * ********************************************************************************/
	
	public String PC_TRIGGER( int _module, int _port)  throws Exception
	{
		return ask(_module,_port,"PC_TRIGGER");
	}
	
	public void PC_TRIGGER( int _module, int _port,String _start, int _fid1,String _stop, int _fid2)  throws Exception
	{
		String cmd=String.format("%s  %s  %d  %s  %d","PC_TRIGGER",_start,_fid1,_stop,_fid2);		
		command(_module,_port,cmd);
	}
	
	public String PC_KEEP( int _module, int _port)  throws Exception
	{
		return ask(_module,_port,"PC_KEEP");
	}
	
	public void PC_KEEP( int _module, int _port,String _which, int _index,int _bytes)  throws Exception
	{
		String cmd=String.format("%s  %s  %d  %d","PC_KEEP",_which,_index,_bytes);		
		command(_module,_port,cmd);
	}
	
	public long[] PC_STATS( int _module, int _port)  throws Exception
	{
		return askLongArray(_module,_port,"PC_KEEP",2);
	}
	
	public String PC_PACKET( int _module, int _port,int _cid)  throws Exception
	{
		return ask(_module,_port,_cid,"PC_PACKET");
	}
	
	public long[] PC_EXTRA( int _module, int _port,int _cid)  throws Exception
	{
		return askLongArray(_module,_port,"PC_EXTRA",3);
	}
		
	
	
	/***********************************************************************************
	 *							Statistics parameters 
	 * ********************************************************************************/
	 
	
	public XenaStatistics PT_TOTAL( int _module, int _port) throws Exception
	{
		return new XenaStatistics(ask(_module,_port,"PT_TOTAL"));
	}
	
	public XenaStatistics PT_NOTPLD( int _module, int _port) throws Exception
	{
		return new XenaStatistics(ask(_module,_port,"PT_NOTPLD"));
	}
	
	public long[] PT_EXTRA( int _module, int _port) throws Exception
	{
		return askLongArray(_module,_port,"PT_EXTRA",2);
	}

	public XenaStatistics PT_STREAM( int _module, int _port,int _sid) throws Exception
	{
		return new XenaStatistics(ask(_module,_port,_sid,"PT_STREAM"));
	}
	
	public void PT_CLEAR( int _module, int _port)  throws Exception
	{
		 command(_module,_port,"PT_CLEAR");
	}	
	
	public XenaStatistics PR_TOTAL( int _module, int _port) throws Exception
	{
		return new XenaStatistics(ask(_module,_port,"PR_TOTAL"));
	}
	
	public XenaStatistics PR_NOTPLD( int _module, int _port) throws Exception
	{
		return new XenaStatistics(ask(_module,_port,"PR_NOTPLD"));
	}
	
	public long[] PR_EXTRA( int _module, int _port) throws Exception
	{
		return askLongArray(_module,_port,"PR_EXTRA",2);
	}
	
	public int[] PR_TPLDS( int _module, int _port) throws Exception
	{
		return askIntArray(_module,_port,"PR_TPLDS",2);
	}
	
	public XenaStatistics PR_STREAM( int _module, int _port,int _sid) throws Exception
	{
		return new XenaStatistics(ask(_module,_port,_sid,"PR_TPLDTRAFFIC"));
	}
	
	public XenaStatistics PR_TPLDTRAFFIC( int _module, int _port,int _sid) throws Exception
	{
		return new XenaStatistics(ask(_module,_port,_sid,"PR_TPLDTRAFFIC"));
	}
	
	public long[] PR_TPLDERRORS( int _module, int _port) throws Exception
	{
		return askLongArray(_module,_port,"PR_TPLDERRORS",4);
	}
	
	public XenaLatencyStatistics PR_STREAM_LATENCY( int _module, int _port,int _sid) throws Exception
	{
		return new XenaLatencyStatistics(ask(_module,_port,_sid,"PR_TPLDLATENCY"));
	}
	
	public XenaLatencyStatistics PR_TPLDLATENCY( int _module, int _port,int _sid) throws Exception
	{
		return new XenaLatencyStatistics(ask(_module,_port,_sid,"PR_TPLDLATENCY"));
	}
	
	public XenaStatistics PR_FILTER( int _module, int _port,int _fid) throws Exception
	{
		return new XenaStatistics(ask(_module,_port,_fid,"PR_FILTER"));
	}
	
	public void PR_CALIBRATE( int _module, int _port, int _tid)  throws Exception
	{
		 command(_module,_port,_tid, "PR_CALIBRATE");
	}
	
	public void PR_CLEAR( int _module, int _port)  throws Exception
	{
		 command(_module,_port,"PR_CLEAR");
	}

	public void P_CLEAR( int _module, int _port)  throws Exception
	{
		PT_CLEAR(_module,_port);
		PR_CLEAR(_module,_port);
	}
	
	
	
	/***********************************************************************************
	 *							Dataset (histogram) parameters 
	 * ********************************************************************************/
	public String PD_INDICES( int _module, int _port,int _mid)  throws Exception
	{
		return ask(_module,_port,_mid,"PD_INDICES");
	}
	
	public void PD_INDICES( int _module, int _port,int _mid, String _dids)  throws Exception
	{
		command(_module,_port,_mid,"PD_INDICES", _dids);
	}
	
	public void PD_CREATE( int _module, int _port,int _did)  throws Exception
	{
		command(_module,_port,_did,"PD_CREATE");
	}
	
	public void PD_DELETE( int _module, int _port,int _did)  throws Exception
	{
		command(_module,_port,_did,"PD_DELETE");
	}
	
	public boolean PD_ENABLE( int _module, int _port,int _mid)  throws Exception
	{
		return askbool(_module,_port,_mid,"PD_ENABLE");
	}
	
	public void PD_ENABLE( int _module, int _port,int _mid, boolean _enable)  throws Exception
	{
		command(_module,_port,_mid,"PD_ENABLE", _enable);
	}
	
	public String PD_SOURCE( int _module, int _port,int _did)  throws Exception
	{
		return ask(_module,_port,_did,"PD_SOURCE");
	}
	
	public void PD_SOURCE( int _module, int _port,int _did, String _type, String _which, int _id)  throws Exception
	{
		String cmd=String.format("%s [%d] %s  %s  %d","PD_SOURCE",_did,_type,_which,_id);
		command(_module,_port,cmd);
	}
	
	public int[] PD_RANGE( int _module, int _port,int _did)  throws Exception
	{
		String cmd=String.format("%s  [%d]","PD_RANGE",_did);
		return askIntArray(_module,_port,cmd,3);
	}
	
	public void PD_RANGE( int _module, int _port,int _did, int _start, int _step, int _count)  throws Exception
	{
		String cmd=String.format("%s  [%d]  %d  %d  %d","PD_RANGE",_did,_start,_step,_count);
		command(_module,_port,cmd);
	}
	
	public long[] PD_SAMPLES( int _module, int _port,int _did)  throws Exception
	{
		String cmd=String.format("%s  [%d]","PD_SAMPLES",_did);
		return askLongArray(_module,_port,cmd,3);
	}
	
	
	
	/***********************************************************************************
	 *							40/100G parameters 
	 * ********************************************************************************/
	
	public int[] PP_TXLANECONFIG( int _module, int _port,int _pid)  throws Exception
	{
		String cmd=String.format("%s  [%d]","PP_TXLANECONFIG",_pid);
		return askIntArray(_module,_port,cmd,3);
	}
	
	public void PP_TXLANECONFIG( int _module, int _port,int _pid, int _virtlane, int _skew)  throws Exception
	{
		String cmd=String.format("%s  [%d]  %d  %d","PP_TXLANECONFIG",_pid,_virtlane,_skew);
		command(_module,_port,cmd);
	}
	
	public void PP_TXLANEINJECT( int _module, int _port,int _pid, String _type)  throws Exception
	{
		String cmd=String.format("%s  [%d]  %s","PP_TXLANEINJECT",_pid,_type);
		command(_module,_port,cmd);
	}
	
	public int[] PP_TXPRBSCONFIG( int _module, int _port,int _pid)  throws Exception
	{
		String cmd=String.format("%s  [%d]","PP_TXPRBSCONFIG",_pid);
		return askIntArray(_module,_port,cmd,4);
	}
	
	public void PP_TXPRBSCONFIG( int _module, int _port,int _pid, String _prbsonoff, String _errorsonoff)  throws Exception
	{
		String cmd=String.format("%s  [%d]  %d  %s  %s","PP_TXPRBSCONFIG",_pid,0,_prbsonoff,_errorsonoff);
		command(_module,_port,cmd);
	}
	
	
	
	
	
	
	
	
	/***********************************************************************************/
	
	public class XenaStatistics
	{
		public final long bps;
		public final long pps;
		public final long bytes;
		public final long packets;
		XenaStatistics (String data)
		{
			String st[] = data.split(" ");
			bps = Long.parseLong(st[0]);
			pps = Long.parseLong(st[1]);
			bytes = Long.parseLong(st[2]);
			packets = Long.parseLong(st[3]);
		}

		@Override
		public String toString() {
			return String.format("bps=%d pps=%d bytes=%d packets=%d",bps,pps,bytes,packets);
		}
		
		
	}

	public class XenaLatencyStatistics
	{
		public final long min;
		public final long max;
		public final long avg;

		XenaLatencyStatistics (String data)
		{
			String st[] = data.split(" ");
			min = Long.parseLong(st[0]);
			avg = Long.parseLong(st[1]);
			max = Long.parseLong(st[2]);
			
		}

		@Override
		public String toString() {
			return String.format("min=%d avg=%d max=%d",min,avg,max);
		}
		
		public XenaLatencyStatistics merge(XenaLatencyStatistics stat)
		{
			return new XenaLatencyStatistics(Math.min(min, stat.min),Math.max(max,stat.max),(avg+stat.avg)/2);

		}

		public XenaLatencyStatistics(long min, long max, long avg) {
			super();
			this.min = min;
			this.max = max;
			this.avg = avg;
		}
		
		
	}
		
	
}
