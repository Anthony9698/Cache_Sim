#!/usr/bin/python3
""" Cache Simulator CS 3853 Spring 2019-Group 8 """


import sys
import math
from random import *


""" Represents a cache block object """
class CacheBlock:
    # cache block constructor
    def __init__(self):
        self.vi_bit = 0
        self.hex_tag = 0x0
        self.clock = 0

    # returns information about cache object (toString)
    def __repr__(self):
        return str(self.__dict__)


""" Determines if number is power of two """
def is_power_of_two(num):
    return num != 0 and ((num & (num - 1)) == 0)


""" Return true if valid replacement policy """
def is_replacement_policy(rp):
    rp = rp.upper()

    if rp == 'RR' or rp == 'RND' or rp == 'LRU':
        return True
    else:
        return False


""" Error checking system arguments for cache """
def error_check_sys_args(cacheSize, blkSize, assoc, rp):
    if is_power_of_two(cacheSize) is False:
        print("Cache size must be power of two")
        sys.exit(-1)

    if is_power_of_two(blkSize) is False:
        print("Block size must be power of two")
        sys.exit(-1)

    if is_power_of_two(assoc) is False:
        print("Associativity must be power of two")
        sys.exit(-1)

    if is_replacement_policy(rp) is False:
        print(rp, "is not a valid replacement policy")
        sys.exit(-1)

    if cacheSize > 8192:
        print("Cache size cannot exceed 8192")
        sys.exit(-1)

    if blkSize > 64:
        print("Block size cannot exceed 64")
        sys.exit(-1)

    if assoc > 16:
        print("Associativity cannot exceed 16")
        sys.exit(-1)

    if sys.argv[1] != "-f":
        print("Not a valid file switch: ", sys.argv[1])
        sys.exit(-1)

    if sys.argv[3] != "-s":
        print("Not a valid size switch: ", sys.argv[3])
        sys.exit(-1)

    if sys.argv[5] != "-b":
        print("Not a valid block size switch: ", sys.argv[5])
        sys.exit(-1)

    if sys.argv[7] != "-a":
        print("Not a valid associativity switch: ", sys.argv[7])
        sys.exit(-1)

    if sys.argv[9] != "-r":
        print("Not a valid replacement switch: ", sys.argv[9])
        sys.exit(-1)


""" Converts a hex string (w/out 0x) to a binary string """
def hex_to_binary_str(hex_str):
    binary_str = "".join(hex2bin_map[i] for i in hex_str)

    return binary_str


""" Takes binary address string and returns hex tag partitioned """
def convert_to_hex_tag(bin_addr_str):
    global tagBits
    start = 0
    end = tagBits
    hex_tag = bin_addr_str[start:end]
    hex_tag = hex(int(hex_tag, 2))

    return hex_tag


""" Takes binary address string and returns index partitioned """
def convert_to_hex_index(bin_addr_str):
    global tagBits, indexBits
    start = tagBits
    end = tagBits + indexBits
    index = bin_addr_str[start:end]
    index = int(index, 2)

    return index


""" Returns the number of bits required for the offset """
def calcIndexBits(assocBits, cacheBits, offset):
    if assocBits == 0:
        bits = int(cacheBits - offset)
    else:
        bits = int(cacheBits - (offset + assocBits))

    return bits


""" Returns the total number of indices in the cache """
def calcTotalIndices(indexBits):
    diff = int(indexBits / 10) * 10
    ndx_bits = indexBits - diff
    total_indices = int(math.pow(2, ndx_bits))

    return total_indices


""" Returns the correct suffix based on the number of bits """
def calcSuffix(bits):
    suffix = "b"
    if bits < 10:
        suffix = "B"

    elif bits >= 10:
        suffix = "KB"

    elif bits >= 20:
        suffix = "MB"

    elif bits >= 30:
        suffix = "GB"

    return suffix


""" Returns the total number of blocks in the cache """
def calcTotalBlocks(assocBits, indexBits):
    bits = assocBits + indexBits
    diff = int(bits / 10) * 10
    blk_bits = bits - diff
    total_blocks = int(math.pow(2, blk_bits))

    return total_blocks


def calcOverheadSz(tagBits, blockBits):
    # tag bit + valid bit * number of blocks / 8
    overheadSz = (math.pow(2, blockBits) * (tagBits + 1)) / 8
    overheadSz = int(overheadSz)
    return overheadSz


def calcTotalImplementationSz(totalOverhead, cacheBits):
    cache_size = math.pow(2, cacheBits)
    total_imp_sz = int(totalOverhead + cache_size)

    return total_imp_sz


""" Called on cache miss
    Searches for an available block (col) in cache set
    Returns index of available block if vi bit 0 
    Returns -1 if set is full (all blocks vi bit 1) 
"""
def next_avail_col_blk(cache_obj, index):
    global compulsory_count
    col_ndx = 0
    for blk in cache_obj[index]:
        if blk.vi_bit == 0:
            compulsory_count += 1
            avail_col = col_ndx
            return avail_col
        else:
            col_ndx += 1

    return -1


""" Returns the column of the matching tag block """
def get_col_of_matching_tag(cache_obj, index, tag):
    col_ndx = 0
    for blk in cache_obj[index]:
        if blk.hex_tag == tag:
            return col_ndx
        col_ndx += 1

    # return -1 on error
    return -1


""" Returns True if set in cache is empty
    (All blocks vi bit set to 0)

    Returns False if at least one block in
    set has vi bit set to 1
"""
def check_if_cache_empty(cache_obj, index):
    for blk in cache_obj[index]:
        if blk.vi_bit != 0:
            return False

    return True


""" Returns True if the tag passed in matches
    a tag in one of the blocks at cache[index]
    and vi bit is set to 1

    Returns False if none of the tags matched
    or vi bit was set to 0
"""
def tags_match(cache_obj, index, tag):
    for blk in cache_obj[index]:
        if blk.vi_bit == 1 and tag == blk.hex_tag:
            return True

    return False


""" RR Policy (FIFO)

    Returns the index of the block that has
    the lowest clock and the index of the 
    block that has the highest clock

    Block with the lowest clock is the one
    we are replacing. After replacing set 
    the clock of this new block to the
    highest clock + 1

    Example:
                 low            high
        Before: | 0 | 1 | 2 | 3 | 4 |

        After:  | 5 | 1 | 2 | 3 | 4 | 
"""
def rr_block_replacement(cache_obj, index):
    lowest_clk = sys.maxsize
    highest_clk = -sys.maxsize - 1
    high_ndx = -1
    low_ndx = -1
    loop_count = 0

    # loop until index of block with lowest clock is found
    for blk in cache_obj[index]:
        if lowest_clk > blk.clock:
            lowest_clk = blk.clock
            low_ndx = loop_count
        loop_count += 1

    # reset loop count
    loop_count = 0

    # loop until index of block with highest clock is found
    for blk in cache_obj[index]:
        if highest_clk < blk.clock:
            highest_clk = blk.clock
            high_ndx = loop_count
        loop_count += 1

    return low_ndx, high_ndx


""" RND Policy (Random) 
    Returns random index between 0 and assoc - 1 
"""
def rnd_block_replacement():
    global associativity
    rnd_index = randint(0, associativity - 1)
    return rnd_index


""" LRU Policy (Least Recently Used)
    Returns index of block with lowest clock 
"""
def lru_block_replacement(cache_obj, index):
    lowest_clock = sys.maxsize
    victim_block = -1
    ndx = 0

    # find the lowest clock
    for blk in cache_obj[index]:
        if lowest_clock > blk.clock:
            lowest_clock = blk.clock
            victim_block = ndx
        ndx += 1

    # index of block with lowest clock
    return victim_block


""" Returns updated cache after processing tag passed in """
def update_cache(cache, ndx, tag):
    global hit_count
    global miss_count
    global conflict_count
    global compulsory_count

    # every block in set has a vi bit set to zero
    if check_if_cache_empty(cache, ndx) is True:
        compulsory_count += 1
        miss_count += 1
        col = 0
        cache[ndx][col].vi_bit = 1
        cache[ndx][col].hex_tag = tag
        cache[ndx][col].hex_index = hex(ndx)

    # if tags don't match, find available block to insert new block
    elif tags_match(cache, ndx, tag) is False:

        # increment miss count
        miss_count += 1

        # get the ndx of the next available block in cache
        col = next_avail_col_blk(cache, ndx)

        # set is full at cache[int_ndx], find blk to replace with R-Policy
        if col == -1:
            conflict_count += 1

            # select block using RR
            if r_policy == 'RR':
                low, high = rr_block_replacement(cache, ndx)
                high_clk = cache[ndx][high].clock
                cache[ndx][low].clock = high_clk + 1
                col = low

            # select block using RND
            elif r_policy == 'RND':
                rnd_ndx = rnd_block_replacement()
                col = rnd_ndx


            # select block using LRU
            elif r_policy == 'LRU':
                low_clk_ndx = lru_block_replacement(cache, ndx)
                col = low_clk_ndx

        # insert new block
        cache[ndx][col].vi_bit = 1
        cache[ndx][col].hex_tag = tag
        cache[ndx][col].hex_index = hex(ndx)

    # tags matched, increment hit count
    else:
        hit_count += 1

        if r_policy == 'LRU':
            col = get_col_of_matching_tag(cache, ndx, tag)
            cache[ndx][col].clock = global_clock

    # return updated cache
    return cache


""" Reads number of bytes at specified address """
def access_cache(hex_address, bytes_read):
    global cache, blockSz, rows, miss_count

    # address passed in represented in a binary string
    binary_addr_str = hex_to_binary_str(hex_address)

    # getting the tag and index from this bit string
    hex_tag = convert_to_hex_tag(binary_addr_str)
    index = convert_to_hex_index(binary_addr_str)

    # update the cache using this index and hex tag
    cache = update_cache(cache, index, hex_tag)

    # string of binary offset
    offset_binary_nums = binary_addr_str[-offsetBits:]

    # add bytes read to this binary offset
    binary_offset = int(offset_binary_nums, 2) + bytes_read

    """" binary offset after add is more than block size,
         find out how many cache blocks it accesses """
    if binary_offset > blockSz:
        # number of times index overflowed
        access_count = float(binary_offset / blockSz)

        # determines how many times to increase index
        if math.ceil(access_count) == int(access_count):
            access_count = int(access_count - 1)
        else:
            access_count = int(access_count)

        count = 0
        # while there are more cache blocks to access
        while count < access_count:
            index += 1

            # if index overflows, increase tag
            if index >= rows:
                max_tag = int(math.pow(2, tagBits))

                hex_index_str = hex_to_binary_str(hex(index)[2:])
                index = int(hex_index_str[-indexBits:], 2)
                int_tag = int(hex_tag, 16) + 1

                # tag overflowed, set to zero
                if int_tag >= max_tag:
                    int_tag = 0

                # convert back to hex str
                hex_tag = hex(int_tag)

            cache = update_cache(cache, index, hex_tag)
            count += 1


# print this if user enters incorrect number of arguments
if len(sys.argv) < 11:
    print("Options: ")
    print(" -f \t\t Trace File")
    print(" -s \t\t Cache Size in KB <1, 2, 4, 8, 8192>")
    print(" -b \t\t Block Size in bytes <4, 8, 16, 32, 64>")
    print(" -a \t\t Associativity <1, 2, 4, 8, 16>")
    print(" -r \t\t Replacement Policy: <RR, RND, LRU>")
    print("\nExample: ./Sim.py -f Trace1.trc -s 64 -a 4 -b 16 -r RR")
    sys.exit(-1)


""" Cache info set from system arguments """
cacheSz = int(sys.argv[4])
blockSz = int(sys.argv[6])
associativity = int(sys.argv[8])
offsetBits = int(math.log(blockSz, 2))
r_policy = sys.argv[10]


""" Validate system arguments """
error_check_sys_args(cacheSz, blockSz, associativity, r_policy)


""" Initializing hit/miss counts"""
hit_count = 0
miss_count = 0
compulsory_count = 0
conflict_count = 0


""" global clock for LRU replacement """
global_clock = 0


""" Calculations necessary to setup cache """
cacheBits = int(math.log(cacheSz, 2)) + 10
assocBits = int(math.log(associativity, 2))
indexBits = calcIndexBits(assocBits, cacheBits, offsetBits)
totalIndices = calcTotalIndices(indexBits)
totalIndicesSuffix = calcSuffix(indexBits)
tagBits = 32 - (offsetBits + indexBits)
totalBlocks = calcTotalBlocks(assocBits, indexBits)
totalBlocksBits = int(assocBits + indexBits)
totalBlocksSuffix = calcSuffix(totalBlocksBits)
totalOverheadSz = calcOverheadSz(tagBits, totalBlocksBits)
totalImplementationSz = calcTotalImplementationSz(totalOverheadSz, cacheBits)
totalOverSz_str = format(totalOverheadSz, ",d")
totalImpSz_str = format(totalImplementationSz, ",d")
totalOverheadSz_kb_str = str(int(totalOverheadSz / 1024))
totalImpSz_kb_str = str(int(totalImplementationSz / 1024))


""" Printing information about cache """
print("Cache Simulator CS 3853 Spring 2019-Group 8")
print('Cmd Line:', sys.argv[0], sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
      sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10])
print('Trace File:', sys.argv[2])
print('Generic:')
print('Cache Size:', cacheSz, 'KB')
print('Block Size:', blockSz, 'bytes')
print('Associativity:', associativity)
print('R-Policy:', sys.argv[10])
print('-----Calculated Values-----')
print('Total #Blocks:', totalBlocks, totalBlocksSuffix, '(2^' + str(totalBlocksBits) + ')')
print('Tag Size:', tagBits, 'bits')
print('Index Size:', indexBits, 'bits, Total Indices:', totalIndices, totalIndicesSuffix)
print('Overhead:', totalOverSz_str, 'bytes (or ' + totalOverheadSz_kb_str + ' KB)')
print('Total Implementation Memory Size:', totalImpSz_str, 'bytes (or ' + totalImpSz_kb_str + ' KB)')


""" Dictionary used to convert hex numbers to binary """
hex2bin_map = {
    "0": "0000",
    "1": "0001",
    "2": "0010",
    "3": "0011",
    "4": "0100",
    "5": "0101",
    "6": "0110",
    "7": "0111",
    "8": "1000",
    "9": "1001",
    "a": "1010",
    "b": "1011",
    "c": "1100",
    "d": "1101",
    "e": "1110",
    "f": "1111",
}


""" Setting up cache (2D array) """
rows = int(math.pow(2, indexBits))
cols = int(associativity)
cache = [[CacheBlock() for j in range(cols)] for i in range(rows)]


""" declaring input file as second system argument """
file_name = sys.argv[2]
try:
    input_file = open(file_name, "r")
except FileNotFoundError:
    raise FileNotFoundError("Input file does not exist")


""" Parse every line for EIP, dstM, and srcM addresses """
for line in input_file:
    # strip newline and tab characters from every line
    line = line.strip('\n')
    line = line.strip('\t')

    # if empty line, skip
    if len(line.strip()) == 0:
        continue

    # break the line into a list of individual chars
    line_tokens = list(line)
    line_prefix = ''.join(line_tokens[0:3])

    # EIP address line
    if line_prefix == 'EIP':
        bytes_read = int(''.join(line_tokens[5:7]))
        instr_addr_str = ''.join(line_tokens[10:18])

        # access cache at this address
        access_cache(instr_addr_str, bytes_read)

    # Beginning of dstM/srcM address line
    if line_prefix == 'dst':
        # parsing out dstM and srcM from line
        dstM = ''.join(line_tokens[6:14])
        srcM = ''.join(line_tokens[33:41])

        # assume 4 byte read and writes
        bytes_read = 4

        # check if dstM address is in the cache (dstM != 0)
        if dstM != '00000000':
            access_cache(dstM, bytes_read)

        # check if srcM address is in the cache (srcM != 0)
        if srcM != '00000000':
            access_cache(srcM, bytes_read)

    # increment global clock (LRU)
    global_clock += 1

total_cache_accesses = hit_count + miss_count
miss_rate = miss_count / total_cache_accesses
miss_rate = '{:.4%}'.format(miss_rate)

print("***** Cache Simulation Results *****\n")
print("Total Cache Accesses:   ", total_cache_accesses)
print("Cache Hits:\t\t", hit_count)
print("Cache Misses:\t\t", miss_count)
print("--- Compulsory Misses:\t   ", compulsory_count)
print("--- Conflict Misses:\t   ", conflict_count, "\n\n")
print("***** *****  CACHE MISS RATE:  ***** *****\n")
print("Miss Rate = ", miss_rate)
input_file.close()