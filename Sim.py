#!/usr/bin/python3


import sys
import math

print("testing....................................")

cacheSz = int(sys.argv[4])
blockSz = int(sys.argv[6])
associativity = int(sys.argv[8])
offset = math.log(blockSz, 2)


hex2bin_map = {
   "0":"0000",
   "1":"0001",
   "2":"0010",
   "3":"0011",
   "4":"0100",
   "5":"0101",
   "6":"0110",
   "7":"0111",
   "8":"1000",
   "9":"1001",
   "a":"1010",
   "b":"1011",
   "c":"1100",
   "d":"1101",
   "e":"1110",
   "f":"1111",
}


def hex_to_binary_str(hex_str):
    binary_str = "".join(hex2bin_map[i] for i in hex_str)

    return binary_str


# OIT- offset index tag
def get_hex_for_OIT(src_b, tag_bits, index_bits):
    tag_bit_str = ''
    index_bit_str = ''
    offset_bit_str = ''

    for bit in src_b:
        if len(tag_bit_str) != tag_bits:
            tag_bit_str += bit

        elif len(index_bit_str) != index_bits:
            index_bit_str += bit

        else:
            offset_bit_str += bit

    tag_hex = hex(int(tag_bit_str, 2))
    index_hex = hex(int(index_bit_str, 2))
    offset_hex = hex(int(offset_bit_str, 2))

    return tag_hex, index_hex, offset_hex


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

    if non_zero_count == 10:
        break

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
        srcM_b = hex_to_binary_str(srcM)

        # print info about EIP, dstM, and srcM
        print("0x" + instr_addr_str + ":(" + bytes_read + ")")
        if dstM != '00000000':
            print("0x--->" + dstM + ":(04)")
        if srcM != '00000000':
            print("0x-->" + srcM_b + ":(04)")
            tag_hex, index_hex, offset_hex = get_hex_for_OIT(srcM_b, tagBits, indexBits)

        non_zero_count += 1
