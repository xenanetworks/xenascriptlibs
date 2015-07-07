package xena;


public class XenaExampl {

	public static void main(String[] args) 
	{
		try
		{
			String xenaip="87.63.85.110";
			String owner = "Java";
			String password = "xena";
			XenaCom xena = new XenaCom();
			
			int module0 = 3;
			int module1 = 3;
			int port0 = 0;
			int port1 = 1;
			int maxload=100;
			int minload=10;
			int step=10;
			
			xena.cmdtrace=true; //This will make the code print out all communication with the chassis 
			xena.C_CONNECT(xenaip);
			System.out.println("Connected to Xena at " + xenaip);
			xena.C_LOGON(password);	
			xena.C_OWNER(owner);
		
			xena.P_RESERVE(module0, port0); //Reserve module0, port0 - this will be the TX port
			xena.P_RESERVE(module1, port1); //Reserve module1, port1 - this will be the RX port
			
			//Reset the two ports
			xena.P_RESET(module0, port0);
			xena.P_RESET(module1, port1);
			Thread.sleep(5000);	//Give the ports a chance to recover from reset
			
			//Create one stream on port 0
			xena.PS_CREATE(module0, port0, 0); 	//module, port, stream id
			xena.PS_TPLDID(module0, port0, 0, 0); //Set the TID of the packets = the stream ID for easy identification

			xena.cmdtrace=false; //Stop printing out all communication with chassis - just print what we ask
			
			xena.PS_ENABLE(module0, port0, 0, "ON");			//Enable stream
			
			//Clear stats
			xena.PT_CLEAR(module0, port0);
			xena.PR_CLEAR(module1, port1);
			
			//Run through all 
			for (int i=minload;i<=maxload;i=i+step)
			{
				xena.PS_RATEFRACTION(module0, port0, 0, i*10000); //1 million = 100%, 10.000 = 1%
				xena.P_TRAFFIC(module0, port0, true);				//Start traffic
				Thread.sleep(1000);						//Wait for one second
				xena.P_TRAFFIC(module0, port0, false);			//Stop traffic
				//xena.PS_ENABLE(0, 0, 0, "OFF");			//Disable stream
				Thread.sleep(2000);						//Wait for two seconds for all traffic to run through etc.
				//Print out statistics
				//These two should match if all traffic has run through!
				System.out.println("TX="+xena.PT_STREAM(module0, port0, 0));	//Get TX stats for SID=0
				System.out.println("RX="+xena.PR_TPLDTRAFFIC(module1, port1, 0));  //Get RX stats for TID=0
				System.out.println();
			}
				
			xena.cmdtrace=true;	
			
			
			//Release resources and disconnect
			xena.P_RELEASE(module0, port0);
			xena.P_RELEASE(module1, port1);
			xena.C_DISCONNECT();
			
		}
		catch(Exception e)
		{
			e.printStackTrace();	
		}
		
		
	}

}
