import pexpect
import reachable_ips
import sys
import subprocess
import re

def ssh_ips(networks):
	ips = reachable_ips.ping_ips(networks)
	sshed_ips = []
	unsshed_ips = []
	for ip in ips:		
		try:
		        #child = pexpect.spawn ('sshpass -p rootroot ssh root@'+ip)	
			child = pexpect.spawn ('ssh '+ip)
	   		child.expect([pexpect.TIMEOUT,'.*password: ','.*(yes/no)? ', pexpect.EOF])
			#child.sendline ("logout")
			if re.search(r'port 22:',child.after):
				unsshed_ips.append(ip)
			else:
				sshed_ips.append(ip)
		except:
			#print "UNABLE TO CHECK LOGIN STATUS --> "+ip
			pass
	return sshed_ips

networks = sys.argv[1:]
pinged_ips = reachable_ips.ping_ips(networks)
ssh_ips(pinged_ips)


