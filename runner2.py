#!/usr/bin/python3

import os
import time

cache_size = 1
block_size = 2
assoc = 1

while assoc != 16:

    if cache_size == 128 and block_size == 64:
        cache_size = 1
        block_size = 4
        assoc *= 2

    elif cache_size == 128:
        block_size *= 2
        cache_size = 1

    command = 'wine CacheSim.exe -f Trace2A.trc -s ', str(cache_size), " -b ", str(block_size), ' -a ', str(assoc), ' -r RR'
    command = ''.join(command)
    os.system(command)
    cache_size *= 2
    time.sleep(5)