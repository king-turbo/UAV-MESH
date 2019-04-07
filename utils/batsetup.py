import subprocess
from multiprocessing import Pool
import time

def setup(num):

	ip = "169.254.143."+str(num)+"/16" 
	subprocess.call(['./batmansetup.sh'])
	time.sleep(1)
	subprocess.call(["sudo", "ifconfig", "bat0", "down"])
	time.sleep(.5)
	subprocess.call(["sudo", "ip", "addr", "add", ip, "dev", "bat0"])
	time.sleep(.5)
	subprocess.call(["sudo", "ifconfig", "bat0", "up"])


# def ping_network(i):
	
# 	try:
# 		ip = "169.254.143."+str(i)
# 		subprocess.check_output(["fping", "-q", "-t", "50", "-c", "1", "-a", ip])
# 		return ip
# 	except:
# 		pass
		

# def pingit():

# 	tic = time.time()
# 	p = Pool(5)
# 	a = p.map(ping_network, range(255))
# 	h = []
# 	for b in a:
# 		if b != None:
# 			h.append(b)
# 	print(h)
# 	p.terminate()
# 	p.join()
# 	print(time.time() - tic)

if __name__ == '__main__':

	
	setup(71)
	

