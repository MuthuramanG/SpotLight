import pexpect
import json
import re

child = pexpect.spawn ('ssh root@192.168.75.77')
child.expect ('.*password: ')
child.sendline ('rootroot')
child.expect ('.*#')

child.sendline ('uname -n')
child.expect ('.*#')
hostname = str(child.after).split("\n")[1]

child.sendline ('uname -m')
child.expect ('.*#')
bit = str(child.after).split("\n")[1]

child.sendline ('lsb_release -d')
child.expect ('.*#')
os = str(child.after).split("\n")[1].split(":")[1].strip()

child.sendline ('ifconfig')
child.expect ('.*#')
ifconfig_lines = str(child.after).split("\n")
eths = ""
for lines in ifconfig_lines:
	if re.search(r'eth',lines):
		if re.search(r'ether',lines):
			pass
		else:
			interface_name = lines.split('Link')[0].strip()
			eths = eths+','+interface_name
	if re.search(r'flags',lines):
		interface_name = lines.split('flags')[0].strip()
		eths = eths+','+interface_name
return re.sub(r':',"",eths)[1:].strip()
			
