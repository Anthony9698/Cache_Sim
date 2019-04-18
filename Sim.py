#!/usr/bin/python3
# Currently Running as: ./Sim.py -f Trace2A.trc -s 2048 -b 16 -a 2 -r RR

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


# represents a block in a cache
class CacheBlock:
    'Common base class for all cache blocks'

    # cache block constructor
    def __init__(self):
        self.vi_bit = 0
        self.hex_tag = 0x0
        self.clock = 0

    # returns information about object (toString)
    # example print(cache_block)
    def __repr__(self):
        return str(self.__dict__)


# dictionary used to convert hex numbers to binary
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


# converts a hex string into a binary string
# example: 0x123 = 000100100011
def hex_to_binary_str(hex_str):
    binary_str = "".join(hex2bin_map[i] for i in hex_str)

    return binary_str


def convert_to_hex_tag(bin_addr_str):
    global tagBits
    start = 0
    end = tagBits
    hex_tag = bin_addr_str[start:end]
    hex_tag = hex(int(hex_tag, 2))

    return hex_tag


def convert_to_hex_index(bin_addr_str):
    global tagBits, indexBits
    start = tagBits
    end = tagBits + indexBits
    index = bin_addr_str[start:end]
    index = int(index, 2)

    return index


def calcIndexBits(assocBits, cacheBits, offset):

    if assocBits == 0:
        bits = int(cacheBits - offset)
    else:
        bits = int(cacheBits - (offset + assocBits))

    return bits


def calcTotalIndices(indexBits):
    diff = int(indexBits / 10) * 10
    ndx_bits = indexBits - diff
    total_indices = int(math.pow(2, ndx_bits))

    return total_indices


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


def calcTotalBlocks(assocBits, indexBits):
    bits = assocBits + indexBits
    diff = int(bits / 10) * 10
    blk_bits = bits - diff
    total_blocks = int(math.pow(2, blk_bits))

    return total_blocks


def calcOverheadSz(tagBits, assoc, indexBits):
    overheadBits = (tagBits * assoc) + assoc
    totalIndicesBytes = (math.pow(2, 15)) / 8
    totalOverheadSz = int(overheadBits * totalIndicesBytes)

    return totalOverheadSz


def calcTotalImplementationSz(totalOverhead, cacheBits):
    cacheSz = math.pow(2, cacheBits)
    total_imp_sz = int(totalOverhead + cacheSz)

    return total_imp_sz


# cache miss, tag not set
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


def check_if_cache_empty(cache_obj, index):
    for blk in cache_obj[index]:
        if blk.vi_bit != 0:
            return False

    return True


def tags_match(cache_obj, index, tag):
    global miss_count
    global hit_count
    for blk in cache_obj[index]:
        if blk.vi_bit == 1 and tag == blk.hex_tag:
            hit_count += 1
            return True

    # didn't find a matching tag or valid bit
    # was not set
    miss_count += 1
    return False


def rr_block_replacement(cache_obj, index):
    lowest_clk = sys.maxsize
    highest_clk = - sys.maxsize - 1
    high_ndx = -1
    low_ndx = -1
    loop_count = 0
    for blk in cache_obj[index]:
        if lowest_clk > blk.clock:
            lowest_clk = blk.clock
            low_ndx = loop_count

        loop_count += 1

    loop_count = 0
    for blk in cache_obj[index]:
        if highest_clk < blk.clock:
            highest_clk = blk.clock
            high_ndx = loop_count

        loop_count += 1

    return low_ndx, high_ndx


def update_cache(cache, ndx, tag):
    global miss_count, conflict_count, compulsory_count
    global line_count, rows

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
        col = next_avail_col_blk(cache, ndx)

        # set is full at cache[int_ndx], find blk to replace with RR
        if col == -1:
            conflict_count += 1
            print("-- Conflict MISS!")
            low, high = rr_block_replacement(cache, ndx)
            high_clk = cache[ndx][high].clock
            cache[ndx][low].vi_bit = 1
            cache[ndx][low].hex_tag = tag
            cache[ndx][low].clock = high_clk + 1
            cache[ndx][low].hex_index = hex(ndx)

        else:
            cache[ndx][col].vi_bit = 1
            cache[ndx][col].hex_tag = tag
            cache[ndx][col].hex_index = hex(ndx)

    # return updated cache
    return cache


# appends zero char to hex address if it needs it
def append_zero_char(hex_address):
    if len(hex_address) < 8:
        hex_address = '0' + hex_address

    return hex_address


def return_second_index_address(old_address, bytes_read):
    new_addr_h = int(old_address, 16) + bytes_read
    new_addr_h = str(hex(new_addr_h))[2:]
    new_addr_h = append_zero_char(new_addr_h)

    return new_addr_h


def format_hex_num(unformatted_hex):
    while(len(unformatted_hex) != 8):
        unformatted_hex = '0' + unformatted_hex

    return unformatted_hex


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
print('R-Policy:', sys.argv[10])
print('Generic:')
print('Cache Size:', cacheSz, 'KB')
print('Block Size:', blockSz, 'bytes')
print('Associativity:', associativity)
print('Policy:', sys.argv[10])
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


# making blocks in a set a linked list
for row in cache:
    count = 0
    for col in row:
        col.clock = count
        count += 1

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