import reachable_ips
import is_ssh
import schedule
import time

def job():
	networks = ["192.168.75.*","192.168.13.*","192.168.10.*","192.168.12.*"]
	for network in networks:
		ip_list = is_ssh.ssh_ips([network])
		f = open("ips_"+network+".txt","w+")
		ip_list = str(ip_list).strip('[|]')
		f.write(ip_list)
		f.close()
	return

schedule.every().day.at("16:38").do(job,)

while True:
    schedule.run_pending()
    time.sleep(60) # wait one minut
