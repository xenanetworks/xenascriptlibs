
class PacketParse():
   IPPROTO_TCP   =  6
   IPPROTO_UDP   = 17
   IPPROTO_ICMPV6= 58

   # Constructor/Destructor
   # 
   def __init__(self, brief=0):
      self.init = 0
      self.brief = brief
      return

   def __del__(self):
      return

   #
   # Helper functions - ugly, should be refactored
   #
   def tomac(self, addr):
      i = 1
      res = ""
      for d in addr:
         res+=d
         if i%2==0 and i < 12:
            res+=":"
         i+=1
      return res

   def toip(self, addr):
      i = 1
      res = ""
      tmp="0x"
      for d in addr:
         tmp+=d
         if i%2==0:
            res+=str(int(tmp,16))
            if (i < 8):
               res+="."
            tmp=""
         i+=1
      return res


   def toipv6(self, addr):
      i = 1
      p = 0
      res = ""
      tmp="0x"
      for d in addr:
         if i <= 4 or i >24:
            tmp+=d
            if i%4==0:
               res+=tmp
               if i < 32:
                  res+=":"
               tmp=""
         else:
            if p == 0:
               p=1
               res+=".:"
         i+=1
      return res

   # return next n bytes as string or empty if not enough data
   def getn(self, n):
      if self.len < n:
         return ""
      tmp = self.data[0:2*n]
      self.data=self.data[2*n:] 
      self.len-= n
      return tmp

   #
   # Packet parsing functions below
   #

   # on first call, set time offset 
   #
   def parse(self, arg):
      args = arg.split()
      if len(args) != 8:
         return
      self.parse = ""
      self.pktnum = int(args[2])
      self.t = int(args[3])*1000000 + int(args[4])
      if self.init == 0:
         self.t0 = self.t
         self.init = 1
      self.plen = args[5]
      self.len = int(args[6])
      self.data = (args[7])[2:]
      t = self.t - self.t0
      self.parse+= "%3d %4d.%06ds: " % (self.pktnum, t/1000000, t%1000000)
      self.ethernet()

   def vlan(self):
      tci=self.getn(2) 
      etype=self.getn(2)
      self.parse+= "vlan tci %s|" % (tci)
      return etype

   def arp(self):
      hwt=self.getn(2)
      prt=self.getn(2)
      hwl=self.getn(1)
      prl=self.getn(1)
      opc=self.getn(2)
      sha=self.getn(6)
      spa=self.getn(4)
      tha=self.getn(6)
      tpa=self.getn(4)
      if opc=="0001":
         self.parse+=" arp  who-has %s tell %s" % (self.toip(tpa), self.toip(spa))
      if opc=="0002":
         self.parse+=" arp  %s is-at %s" % (self.toip(spa), self.tomac(sha))
      return

   def flgs(self, f):
      res = ""
      flg=int(f, 16)
      if flg & 0x1:
         res+="F"
      if flg & 0x2:
         res+="S"
      if flg & 0x4:
         res+="R"
      if flg & 0x8:
         res+="P"
      if flg & 0x10:
         res+="A"
      return res

   def tcp(self):
      srcp="0x"+self.getn(2)
      dstp="0x"+self.getn(2)
      seq=self.getn(4)
      ack=self.getn(4)
      null=self.getn(1)
      flags="0x"+self.getn(1) 
      self.parse+= " tcp  %d->%d %-4s" % (int(srcp,16), int(dstp,16), self.flgs(flags))
      return

   def udp(self):
      srcp="0x"+self.getn(2)
      dstp="0x"+self.getn(2)
      self.parse+= " udp  %d->%d " % (int(srcp,16), int(dstp,16))
      if int(dstp,16) == 5678:
         self.parse+="(neighbour disc.)"
      return

   def icmpv6(self):
      type="0x"+self.getn(1)
      code="0x"+self.getn(1)
      self.parse+= " icmp "
      if int(type,16) == 135:
         self.parse+= "ndp request"
      if int(type,16) == 136:
         self.parse+= "ndp reply"
      return

   def ipv4(self):
      null = self.getn(8)
      ttl = "0x"+self.getn(1)
      proto = int("0x"+self.getn(1), 16)
      null = self.getn(2)
      srcip = self.getn(4)
      dstip = self.getn(4)
      self.parse+= " ip  %s -> %s (ttl %s)|" % (self.toip(srcip), self.toip(dstip), int(ttl,0))
      if proto == self.IPPROTO_TCP:
         self.tcp()
      elif proto == self.IPPROTO_UDP:
         self.udp()
      return


   def ipv6(self):
      vtfl = self.getn(4)
      paylen = "0x"+self.getn(2)
      proto = int("0x"+self.getn(1), 16)
      ttl   = "0x"+self.getn(1)
      srcip = self.getn(16)
      dstip = self.getn(16)
      self.parse+= " ipv6  %s -> %s (hop %s)|" % (self.toipv6(srcip), self.toipv6(dstip), int(ttl,0))
      if proto == self.IPPROTO_TCP:
         self.tcp()
      elif proto == self.IPPROTO_UDP:
         self.udp()
      elif proto == self.IPPROTO_ICMPV6:
         self.icmpv6()
      return


   def ethernet(self):
      dstmac=self.getn(6)
      srcmac=self.getn(6)
      etype=self.getn(2)
      if not self.brief:
         self.parse+= "%s->%s|"  % (self.tomac(srcmac), self.tomac(dstmac))

      if dstmac == "01000CCCCCCC":
         self.parse+= " CISCO Discovery Protocol"
      
      if etype == "8100":
         etype = self.vlan()

      if etype == "0806":
         self.arp() 
      elif etype == "0800":
         self.ipv4()
      elif etype == "86DD":
         self.ipv6()
      else:
         self.parse+= " type/len %s" % (etype)

      self.parse += " %s bytes" % (self.plen)
      print(self.parse)

