import re
import subprocess
import sys

def ping_ips(networks):
	#networks = ["192.168.75.*","192.168.13.*","192.168.10.*"]
	#networks = ["192.168.12.*"]
	ip_addresses = []
	for network in networks:
		p = subprocess.Popen(["nmap","-sn",network], stdout=subprocess.PIPE)
		reach_ips, err = p.communicate()
		for report in reach_ips.split("\n"):
			#print report
			match = re.match(r'(.*)for(.*)',report)
			if match is None:
				pass
			else:
				# TO GET IP OF MACHINES WHICH HAVING HOSTNAME
				if re.search(r'[a-z]|[A-Z]',match.group(2)):
					host_ip = re.match(r'.*\((.*)\)',match.group(2))
		                	ip_addresses.append(host_ip.group(1).strip())
				else:
				        ip_addresses.append(match.group(2).strip())
	return ip_addresses

networks = sys.argv[1:]
print ping_ips(networks)
