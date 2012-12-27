#!/usr/bin/env python
import argparse
import hashlib
from multiprocessing import Lock
import os
import queue
import random
import string
import sys
import threading
import time
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

# Constants
CHARS = string.ascii_letters+string.digits # Characters used for random URLs.
DIR_OUTPUT = 'output' # Output directory.
ERRORS_DISPLAY = True # Should all errors display?
IMAGE_EXTENSION = ".jpg" # Extension for search.
IMAGE_SIZE_MIN = 1024 * 20 # Minimum filesize for downloaded images.
IMAGES_DEFAULT = 25 # Number of images to download if not specified at command line.
IMGUR_URL_PREFIX = "http://i.imgur.com/" # Prefix for Imgur URLs.
THREADS = 5 # Number of threads to spawn.

# Globals
queue_image_ids = queue.Queue() # Queue for random images.
downloaded = 0 # Number of images downloaded.

# Functions
def rand_string(string_length):
    return ''.join([random.choice(CHARS) for x in range(string_length)])

def path_get():
    if sys.platform.startswith('win32'):
        path = os.getcwd()+'\\'+DIR_OUTPUT+'\\'
    else:
        path = os.getcwd()+'/'+DIR_OUTPUT+'/'
    return path

def path_create():
    path = path_get()
    if not os.path.exists(path):
        os.makedirs(path)

def error_print(error):
    if ERRORS_DISPLAY:
        print(error)

# Thread
class ThreadSpawn(threading.Thread):

    def __init__(self, queue, lock):
          threading.Thread.__init__(self)
          self.queue = queue
          self.lock = lock

    def get_images(self, num_pics):
        path = path_get()
        for i in range(num_pics):
            success = False
            while not success:
                image_name = rand_string(5) + IMAGE_EXTENSION
                url = IMGUR_URL_PREFIX+image_name
                req = Request(url)
                data = None

                try:
                    data = urlopen(req)
                except HTTPError as e:
                    error_print("HTTP Error: "+str(e.code)+' '+image_name)
                except URLError as e:
                    error_print("URL Error: "+str(e.reason)+' '+image_name)

                if data:
                    try:
                        data = data.read();

                        # Check if placeholder image.
                        if 'd835884373f4d6c8f24742ceabe74946' == hashlib.md5(data).hexdigest():
                            error_print("Received placeholder image: "+image_name)
                        # Check if image is above minimum size.
                        elif IMAGE_SIZE_MIN > sys.getsizeof(data):
                            error_print("Received image is below minimum size threshold: "+image_name)
                        # Write image to disk.
                        else:
                            success = True
                            self.local_file = open(path+image_name, "wb")
                            self.local_file.write(data)
                            self.local_file.close()
                            lock.acquire()
                            global downloaded
                            downloaded += 1
                            lock.release()
                            print("Downloaded image #"+str(downloaded)+": "+image_name)

                        del data
                    except:
                        error_print("Download failed: "+image_name)

    def run(self):
        while True:
            # Grabs num from queue - note that num is arbitrary and isn't used.
            num = self.queue.get()

            # Grabs a pic.
            self.get_images(1)

            # Signals to queue job is done.
            self.queue.task_done()

# Main
if __name__ == '__main__':
    time_start = time.time()

    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--errors', type=str, default='True', help='Toggle error messages on and off. (Default: True)')
    parser.add_argument('-i', '--images', type=int, default=IMAGES_DEFAULT, help='Number of images to download. (Default: '+str(IMAGES_DEFAULT)+')')
    parser.add_argument('-min', '--min-size', type=int, default=IMAGE_SIZE_MIN, help='Minimum image size in bytes. (Default: '+str(IMAGE_SIZE_MIN)+')')
    parser.add_argument('-o', '--output', type=str, default=DIR_OUTPUT, help='Output folder name. (Default: '+str(DIR_OUTPUT)+')')
    parser.add_argument('-t', '--threads', type=int, default=THREADS, help='Number of threads to spawn. (Default: '+str(THREADS)+')')
    args = parser.parse_args()

    # Error messages.
    if args.errors in ['false','False','No','no','0']:
        ERRORS_DISPLAY = False

    # Minimum image size
    IMAGE_SIZE_MIN = args.min_size #TODO: Do not overwrite CONSTANTS.
    print("Minimum image size is: "+str(IMAGE_SIZE_MIN))

    # Image path.
    DIR_OUTPUT = args.output #TODO: Do not overwrite CONSTANTS.
    path_create()
    print('Output folder is: "'+path_get()+'"')

    # Image limit.
    image_limit = args.images
    print('Retreiving '+str(image_limit)+' random images.')

    # Populate queue with data.
    for n in range(image_limit):
        queue_image_ids.put(n)
   
    # Create shared lock.
    lock = Lock()
   
    # Spawn a pool of threads, and pass them queue instance.
    print("Spawning "+str(args.threads)+" threads.\n")
    for i in range(args.threads):
        t = ThreadSpawn(queue_image_ids, lock)
        t.daemon = True
        t.start()

    # Wait on the queue until everything has been processed.
    queue_image_ids.join()

    # Completion.
    time_end = time.time()
    time_total = round(time_end - time_start, 2)
    rate = round(time_total / image_limit, 2)
    print("\n")
    print('Completed in: '+str(time_total)+' seconds.')
    print("Approximately "+str(rate)+' seconds per image.')
