#!/usr/bin/python3
# Example run: ./Sim.py -f TinyTrace.trc -s 1024 -b 16 -a 2 -r RR


import sys
import math


cacheSz = int(sys.argv[4])
blockSz = int(sys.argv[6])
associativity = int(sys.argv[8])
offset = math.log(blockSz, 2)

# TODO(1): implement RR, RND, and LRU(bonus if we can)
#       replacement policies


# TODO(2): calculate...
#                   > Total Cache Accesses (hits + misses)
#                   > Cache Hits
#                   > Cache Misses
#                   > Compulsory Misses
#                   > Conflict Misses


# TODO(3): create appropriate arrays (multidimensional if assoc > 1)
#       to set up cache using this object.
#       Example: CacheSize: 4096, ASSOC: 2
#       CacheBlock cache[4096][2]
#                         ^    ^
#                      INDEX# SET#
# represents a block in a cache
class CacheBlock:
    'Common base class for all cache blocks'
    hit_count = 0
    miss_count = 0

    # cache block constructor
    def __init__(self, hex_index=0, hex_tag=0, hex_data=0):
        self.hex_index = hex_index
        self.vi_bit = 0
        self.hex_index = hex_tag

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


# TODO(4): use tag and index info returned from this
#       method to create cache block objects
def get_hex_for_tag_index(src_b, tag_bits, index_bits):
    tag_bit_str = ''
    index_bit_str = ''

    # prints instruction address in binary (for debugging)
    print(src_b)

    # sections bits for tag and index
    for bit in src_b:
        if len(tag_bit_str) != tag_bits:
            tag_bit_str += bit

        elif len(index_bit_str) != index_bits:
            index_bit_str += bit

    tag_hex = hex(int(tag_bit_str, 2))
    index_hex = hex(int(index_bit_str, 2))

    # printing index and tag values in hex (for debugging)
    print("INDEX: ", index_hex)
    print("TAG: ", tag_hex)
    print("=============================")

    #return tag_hex, index_hex


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


def next_avail_col(cache, hex_index):
    index = 0
    int_index = int(hex_index, 10)
    for blk in cache[int_index]:
        if blk.vi_bit == 0:
            return index
        else:
            index += 1
    return index


cacheBits = int(math.log(cacheSz, 2)) + 10
assocBits = int(math.log(associativity, 2))
indexBits = calcIndexBits(assocBits, cacheBits, offset)
totalIndices = calcTotalIndices(indexBits)
totalIndicesSuffix = calcSuffix(indexBits)
tagBits = int(32 - (offset + indexBits))
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
print('Cache Size:', cacheSz, 'KB')
print('Block Size:', blockSz, 'bytes')
print('Associativity:', associativity)
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
print('-----Results-----')
print('Cache Hit Rate:%')

# setting up cache
rows = int(math.pow(indexBits, 2))
cols = int(associativity)
cache = [[CacheBlock() for j in range(cols)] for i in range(rows)]

# parsing
file_name = sys.argv[2]
try:
    input_file = open(file_name, "r")
except FileNotFoundError:
    raise FileNotFoundError("Input file does not exist")

non_zero_count = 0
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
        bytes_read = ''.join(line_tokens[5:7])
        instr_addr_str = ''.join(line_tokens[10:18])

    if line_prefix == 'dst':
        dstM = ''.join(line_tokens[6:14])
        srcM = ''.join(line_tokens[33:41])

        # sets string instruction address to binary string
        # example: 0x7C81EB33 = 01111100100000011110101100110011
        instr_addr_str_b = hex_to_binary_str(instr_addr_str)

        # print current instruction address (testing for now)
        print("Instruction Address: ", instr_addr_str)

        # prints hex tag and hex index
        get_hex_for_tag_index(instr_addr_str_b, tagBits, indexBits)
