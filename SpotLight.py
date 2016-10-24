from flask import Flask,send_file 
from flask.ext.cors import CORS
from qrcode import *
import pexpect
import json
import re
import os
import pexpect
import sys
import reachable_ips
import is_ssh

app = Flask(__name__)
cors = CORS(app)

@app.route("/<info>/<ip>")
@app.route("/<info>/<ip>/<eth>")
@app.route("/<info>/<ip>/<username>/<password>")
@app.route("/<info>/<ip>/<eth>/<username>/<password>")
def hello(info,ip,eth='eth0',username="root",password="rootroot"):
	if info != "ssh":	
		child = pexpect.spawn ('ssh '+username+'@'+ip)
 		i = child.expect([pexpect.TIMEOUT,'.*password: ','.*(yes/no)? ', pexpect.EOF])
	    	if i == 2: # In this case SSH does not have the public key cached.
        	    child.sendline ('yes')
	            child.expect ('.*password: ')
		    child.sendline (password)
		    #child.expect ('.*#')
		    j = child.expect (['.*#','.*password:'])
                    if j == 1:
                        return "ACCESS DENIED ! ENTER CORRECT USERNAME or PASSWORD !"
		elif i == 1:
        	    child.sendline (password)
		    j = child.expect (['.*#','.*password:'])
		    if j == 1:
			return "ACCESS DENIED ! ENTER CORRECT USERNAME or PASSWORD !"
		else:
		    return "ERROR! could not login with SSH.:"
	#print ip
	if info == "os":
		child.sendline ('uname -n')
		child.expect ('.*#')
		hostname = str(child.after).split("\n")[1]

		child.sendline ('uname -m')
		child.expect ('.*#')
		bit = str(child.after).split("\n")[1]

		child.sendline ('lsb_release -d')
		child.expect ('.*#')
		os = str(child.after).split("\n")[1].split(":")[1].strip()

		if re.search('Desc',(child.after)):
			pass
		else:
			child.sendline ('cat /etc/*redhat*')
               		child.expect ('.*#')
			os = str((child.after).split("\n")[1])

		return "HOSTNAME    :   "+hostname+"\n"+ \
		       "OS          :   "+os+"\n"+ \
		       "ARCHITECURE :	"+bit

	elif info == "ram":
		# RAM DETAILS
		child.sendline ('free -m')
		child.expect ('.*#')
		ram_details =  str(child.after).split("\n")[2].split(":")[1]
		ram_details = re.sub("[ ]{1,}"," ",ram_details).split(" ")
		ram_total = str(ram_details[1]) + " MB"
		ram_used  = str(ram_details[2]) + " MB"
		ram_free  = str(ram_details[3]) + " MB"

		return  "RAM TOTAL   :   "+ram_total+"\n"+ \
			"RAM USED     :   "+ram_used+"\n"+ \
			"RAM FREE     :   "+ram_free

	elif info == "code":
		qr = QRCode(version=20, error_correction=ERROR_CORRECT_L)
		qr.add_data("pell-checker was created and developed by Reverso-Softissimo in addition to the online ...")
		qr.make() # Generate the QRCode itself
		# im contains a PIL.Image.Image object
		im = qr.make_image()
		# To save it
		#im.save("filename.png")
		img_io = StringIO()
	        pil_img.save(img_io, 'JPEG', quality=70)
		img_io.seek(0)
		return send_file(img_io, mimetype='image/jpeg')
		#return send_file(filename, mimetype='image/png')

	elif info == "processor":
		#NO. OF PROCESSING UNITS
		child.sendline ('cat /proc/cpuinfo | grep processor | wc -l')
		child.expect ('.*#')
		No_of_processor = str(child.after).split("\n")[1].strip()

		#PROCESSOR MODEL
		child.sendline ('cat /proc/cpuinfo | grep name')
		child.expect ('.*#')
		processor_model = str(child.after).split("\n")[1].split(":")[1].strip()

		#NO. OF CPU CORES
		child.sendline ('cat /proc/cpuinfo | grep cores')
		child.expect ('.*#')
		cpu_core = str(child.after).split("\n")[1].split(":")[1].strip()
	
		return "NO. OF PROCESSOR   :   "+No_of_processor+"\n" \
		       "PROCESSOR MODEL    :   "+processor_model+"\n" \
		       "NO. OF CPU CORE      :   "+cpu_core

	elif info == "interfaces":
		child.sendline ('ifconfig')
		child.expect ('.*#')
		ifconfig_lines = (child.after)
		#data = ""
		#for lines in ifconfig_lines:
		#	data = data+"\n"+lines	
		return ifconfig_lines
	
	elif info == "storage":
                child.sendline ('df -H')
                child.expect ('.*#')
                ifconfig_lines = (child.after)
		#return str(ifconfig_lines)
                #data = ""
                #for lines in ifconfig_lines:
                #       data = data+"\n"+lines
                return ifconfig_lines


	elif info == "select_eth":
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
		eth_names = re.sub(r':',"",eths)[1:].strip()
		return eth_names

	elif info == "ethernet":
		child.sendline ('ifconfig '+eth)
		child.expect ('.*#')
		ifconfig_lines = str(child.after).split("\n")

		#TO GET MAC
		if re.search(r'HWaddr',ifconfig_lines[1]):
			#interface_name = lines.split('Link')[0].strip()
			interface_mac  = ifconfig_lines[1].split('HWaddr')[1].strip()
		elif re.search(r'ether',ifconfig_lines[4]):
			interface_mac = ifconfig_lines[4].split('txqueuelen')[0].split('ether')[1].strip()
		else:
			interface_mac = "UNABLE TO GET MAC"
		
		# TO GET IP
		if re.search(r'Bcast',ifconfig_lines[2]):
			if re.search(r'inet addr',ifconfig_lines[2]):
				interface_ip = ifconfig_lines[2].split('Bcast')[0].split(':')[1].strip()
		elif re.search(r'broadcast',ifconfig_lines[2]):
			interface_ip = ifconfig_lines[2].split('netmask')[0].split('inet')[1].strip()
		else:
			interface_ip = 'No Ip'

		child.sendline ('ethtool '+eth)
		child.expect ('.*#')
		ethtool_details1 = (child.after)
		ethtool_details = list((child.after).split("\n"))
		#print ethtool_details.strip()
		for ethtool_detail in ethtool_details:
			#print ethtool_detail
			if re.search(r'[s|S]peed',ethtool_detail):
				interface_speed = ethtool_detail.split(":")[1].strip()
			elif re.search(r'Link detected',ethtool_detail):
				interface_link_status = ethtool_detail.split(":")[1].strip()

		# INTERFACE DRIVER
		try:
			child.sendline ('lshw -short | grep '+eth)
			child.expect ('.*#')
			interface_driver = str(child.after).split("\n")[1]
			interface_driver = re.sub("[ ]{1,}"," ",interface_driver).split("network")[1].strip()
		except:
			interface_driver = "UNABLE TO GET DRIVER INFO"
		

		return "IP   :   "+interface_ip+"\n" \
		       "MAC  :   "+interface_mac+"\n" \
		       "SPEED   :   "+interface_speed+"\n" \
		       "DRIVER  :   "+interface_driver+"\n" \
		       "LINK STATUS   :   "+interface_link_status

	elif info == "ssh":
		ip = "192.168."+ip+".*"
		#network = [ip]
	        #ip_list = is_ssh.ssh_ips(network)	
		f = open("ips_"+ip+".txt","r")
		data = f.read()
		f.close()
		return data
		#return "sssh"

	else:
		child.sendline ('logout')
		os.system("python difos.py "+ip+" > result_"+ip+".txt")
		f = open("result_"+ip+".txt","r")
		data = ""
		for line in f.readlines():
        		data = data
        		data = data+line
		#print data
		return data


if __name__ == "__main__":
        app.run(host= '0.0.0.0')

		#is_ssh.ssh_ips()
	
