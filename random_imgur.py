import os
import sys
import random
import time
from urllib2 import Request, urlopen, URLError, HTTPError

CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghiklmnopqrstuvwxyz"
start_time = time.time()

# syntax: random_imgur.py <how_many>; defaults to 5 if no input
parsed_number = ''.join(sys.argv[1:])
if not parsed_number:
	HOW_MANY = 5
else:
	HOW_MANY = int(parsed_number)
	
print 'getting ' + str(HOW_MANY) + ' random pics'

# functions
def rand_string(string_length):
	output = ''		
	
	for i in xrange(string_length):
		output += random.choice(CHARS)
		
	return output

def get_images(num_pics):
	if sys.platform.startswith('win32'):
		path = os.getcwd() + '\\output\\'
	else:
		path = os.getcwd() + '/output/'
		
	if not os.path.exists(path):
		os.makedirs(path)
	print 'saving to: ' + path

	for k in xrange(num_pics):
		good = False
		while not good:
			img_name = rand_string(5)
			url = "http://i.imgur.com/" + img_name + ".jpg"
			req = Request(url)
			
			try:
				f = urlopen(req)
				print "downloading " + url
				local_file = open(path + img_name + '.jpg', "wb")
				local_file.write(f.read())
				local_file.close()
				good = True
			except HTTPError, e:
				print "HTTP Error:",e.code , url
				print 'trying again...'
			except URLError, e:
				print "URL Error:",e.reason , url
				print 'trying again...'

# main
get_images(HOW_MANY)
print 'done!'
end_time = time.time()
print 'completed in: ' + str(round(end_time - start_time, 2)) + ' seconds'