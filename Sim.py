#!/usr/bin/python3
import sys
import math

cacheSz = int(sys.argv[4])
blockSz = int(sys.argv[6])
associativity = int(sys.argv[8])
offsetBits = int(math.log(blockSz, 2))

miss_count = 0
hit_count = 0
compulsory_count = 0
conflict_count = 0


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


# TODO: FIX CALCULATION
def calcOverheadSz(tagBits, assoc, indexBits):
    overheadBits = (tagBits * assoc) + assoc
    totalIndicesBytes = (math.pow(2, 15)) / 8
    OverheadSz = int(overheadBits * totalIndicesBytes)

    return OverheadSz


# TODO: FIX CALCULATION
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


""" Returns True and increments hit count if 
    the tag passed in matches a tag in one of
    the blocks at cache[index] and vi bit is
    set to 1
    
    Returns False and increments miss count if
    none of the tags matched or vi bit was
    set to 0
"""
def tags_match(cache_obj, index, tag):
    global miss_count
    global hit_count
    for blk in cache_obj[index]:
        if blk.vi_bit == 1 and tag == blk.hex_tag:
            hit_count += 1
            return True

    miss_count += 1
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
    highest_clk = - sys.maxsize - 1
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


""" Returns updated cache after processing tag passed in """
def update_cache(cache, ndx, tag):
    global miss_count, conflict_count, compulsory_count

    # every block in set has a vi bit set to zero
    if check_if_cache_empty(cache, ndx) is True:
        compulsory_count += 1
        miss_count += 1
        col = 0
        cache[ndx][col].vi_bit = 1
        cache[ndx][col].hex_tag = tag
        cache[ndx][col].hex_index = hex(ndx)

    # check if current tag matches any block in the blk set at cache[int_ndx]
    elif tags_match(cache, ndx, tag) is False:

        # get the ndx of the next available block in cache
        col = next_avail_col_blk(cache, ndx)

        # set is full at cache[int_ndx], find blk to replace with R-Policy
        if col == -1:
            conflict_count += 1
            low, high = rr_block_replacement(cache, ndx)
            high_clk = cache[ndx][high].clock
            cache[ndx][low].vi_bit = 1
            cache[ndx][low].hex_tag = tag
            cache[ndx][low].clock = high_clk + 1
            cache[ndx][low].hex_index = hex(ndx)

        # set wasn't full, add block
        else:
            cache[ndx][col].vi_bit = 1
            cache[ndx][col].hex_tag = tag
            cache[ndx][col].hex_index = hex(ndx)

    # return updated cache
    return cache


def access_cache(hex_address, bytes_read):
    global cache, blockSz, rows, miss_count

    binary_addr_str = hex_to_binary_str(hex_address)
    hex_tag = convert_to_hex_tag(binary_addr_str)
    index = convert_to_hex_index(binary_addr_str)
    cache = update_cache(cache, index, hex_tag)

    # string of binary offset
    offset_binary_nums = binary_addr_str[-offsetBits:]

    # add bytes read to this binary offset
    binary_offset = int(offset_binary_nums, 2) + bytes_read

    ''' if binary offset after add is more than block size
        find out how many cache blocks it accesses'''
    if binary_offset > blockSz:
        access_count = float(binary_offset / blockSz)

        if math.ceil(access_count) == int(access_count):
            access_count = int(access_count - 1)
        else:
            access_count = int(access_count)

        count = 0
        ''' while there are more cache blocks to access'''
        while count < access_count:
            index += 1

            ''' if index is more than total rows,
                increment tag and get new index '''
            if index >= rows:
                hex_index_str = hex_to_binary_str(hex(index)[2:])
                index = int(hex_index_str[-indexBits:], 2)
                hex_tag = hex(int(hex_tag, 16) + 1)

            cache = update_cache(cache, index, hex_tag)
            count += 1


cacheBits = int(math.log(cacheSz, 2)) + 10
assocBits = int(math.log(associativity, 2))
indexBits = calcIndexBits(assocBits, cacheBits, offsetBits)
totalIndices = calcTotalIndices(indexBits)
totalIndicesSuffix = calcSuffix(indexBits)
tagBits = 32 - (offsetBits + indexBits)
totalBlocks = calcTotalBlocks(assocBits, indexBits)
totalBlocksBits = int(assocBits + indexBits)
totalBlocksSuffix = calcSuffix(totalBlocksBits)
totalOverheadSz = calcOverheadSz(tagBits, associativity, indexBits)
totalImplementationSz = calcTotalImplementationSz(totalOverheadSz, cacheBits)
totalOverSz_str = format(totalOverheadSz, ",d")
totalImpSz_str = format(totalImplementationSz, ",d")
totalOverheadSz_kb_str = str(int(totalOverheadSz / 1024))
totalImpSz_kb_str = str(int(totalImplementationSz / 1024))


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


# setting up cache
rows = int(math.pow(2, indexBits))
cols = int(associativity)
cache = [[CacheBlock() for j in range(cols)] for i in range(rows)]

# parsing
file_name = sys.argv[2]
try:
    input_file = open(file_name, "r")
except FileNotFoundError:
    raise FileNotFoundError("Input file does not exist")

line_count = 1
# for every eip and dstm instruction
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

    if line_prefix == 'EIP':
        bytes_read = int(''.join(line_tokens[5:7]))
        instr_addr_str = ''.join(line_tokens[10:18])

        # access cache at this address
        access_cache(instr_addr_str, bytes_read)

    if line_prefix == 'dst':
        # parsing out dstM and srcM from line
        dstM = ''.join(line_tokens[6:14])
        srcM = ''.join(line_tokens[33:41])

        # assume 4 byte read and writes
        bytes_read = 4

        # check if dstM address is in the cache
        if dstM != '00000000':
            access_cache(dstM, bytes_read)

        # check if srcM address is in the cache
        if srcM != '00000000':
            access_cache(srcM, bytes_read)

        line_count += 2

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