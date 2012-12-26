import os
import sys
import random
import time
import string
import Queue
import threading
from urllib2 import Request, urlopen, URLError, HTTPError

CHARS = string.letters + string.digits
num_q = Queue.Queue()   # won't store any data, just how many pics you want threads to get

# functions
def rand_string(string_length):
    return ''.join([random.choice(CHARS) for x in range(string_length)])

#class
class ThreadGet(threading.Thread):

    def __init__(self, queue):
          threading.Thread.__init__(self)
          self.queue = queue

    def get_images(self, num_pics):
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
                f = None
                
                try:
                    f = urlopen(req)
                    print "downloading " + url
                except HTTPError, e:
                    print "HTTP Error:",e.code , url
                    print 'trying again...'
                except URLError, e:
                    print "URL Error:",e.reason , url
                    print 'trying again...'
                    
                if f:
                    try:
                        local_file = open(path + img_name + '.jpg', "wb")
                        local_file.write(f.read())
                        local_file.close()
                        good = True
                    except:
                        print e, path + img_name + '.jpg'
                    
    def run(self):
        while True:
            #grabs num from queue - note that num is arbitrary and isn't used
            num = self.queue.get()
            
            #grabs a pic
            self.get_images(1)
            
            #signals to queue job is done
            self.queue.task_done()

# main
if __name__ == '__main__':
    start_time = time.time()
    
    # syntax: random_imgur.py <how_many>; defaults to 5 if no input
    parsed_number = ''.join(sys.argv[1:])
    if not parsed_number:
        HOW_MANY = 5
    else:
        HOW_MANY = int(parsed_number)
        
    print 'getting ' + str(HOW_MANY) + ' random pics'
    
    #spawn a pool of threads, and pass them queue instance 
    for i in range(5):
        t = ThreadGet(num_q)
        t.setDaemon(True)
        t.start()
      
    #populate queue with data   
    for n in range(HOW_MANY):
        num_q.put(n)
    
    #wait on the queue until everything has been processed     
    num_q.join()
    
    print 'done!'
    end_time = time.time()
    print 'completed in: ' + str(round(end_time - start_time, 2)) + ' seconds'
