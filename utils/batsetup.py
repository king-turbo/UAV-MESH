#!/usr/bin/env python3
import sys, getopt
import subprocess
from multiprocessing import Pool
import time
import os
def setup(argv):

	opts, args = getopt.getopt(argv, "n:", ["number"])
	print(opts,args)
	num = 0
	for opt, arg in opts:
		if opt == "-n":
			num = arg
			# print(opt, arg)
	if num == 0:
		print("Please include a unique vehicle number between 1-254")
		return 0
	print(num)
	ip = "169.254.143."+str(num)+"/16" 
	subprocess.call(['./batmansetup.sh', ip])
	# time.sleep(1)
	# subprocess.call(["sudo", "ifconfig", "bat0", "down"])
	# time.sleep(.5)
	# subprocess.call(["sudo", "ip", "addr", "add", ip, "dev", "bat0"])
	# time.sleep(.5)
	# subprocess.call(["sudo", "ifconfig", "bat0", "up"])


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

	setup(sys.argv[1:])