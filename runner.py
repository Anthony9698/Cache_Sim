#!/usr/bin/python3

import os

cache_size = 1
block_size = 4
assoc = 1

while assoc != 16:

    if cache_size > 8192 or block_size > 64 or assoc > 16:
        print("CACHE SIZE: ", cache_size)
        print("BLOCK SIZE: ", block_size)
        print("ASSOC: ", assoc)
        exit(-1)

    if cache_size == 8192 and block_size == 64:
        cache_size = 1
        block_size = 4
        assoc *= 2

    elif cache_size == 8192:
        block_size *= 2
        cache_size = 1

    command = './Sim.py -f Trace1.trc -s ', str(cache_size), " -b ", str(block_size), ' -a ', str(assoc), ' -r RR'
    command = ''.join(command)
    os.system(command)

    cache_size *= 2



