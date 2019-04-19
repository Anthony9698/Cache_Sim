#!/usr/bin/python3

#from openpyxl import Workbook
import sys
import re
data = sys.stdin.readlines()

line_count = 1
for line in data:
    # strip newline and tab characters from every line
    line = line.strip('\n')
    line = line.strip('\t')
    line = line.replace("\t", "")
    line = line.replace("\t\t", "")
    line = line.replace(" ", "")
    f_line = re.findall(':(.*)', line)
    f_line = ''.join(f_line)

    # if empty line, skip
    if len(line.strip()) == 0:
        line_count += 1
        continue

    # Trace file line
    if line_count is 3:
        print(f_line)

    # cache size
    elif line_count is 5:
        print(f_line)

    # block size
    elif line_count is 6:
        block_size = f_line.split("bytes")
        block_size = f_line[0] + "B"
        print(block_size)

    # assoc
    elif line_count is 7:
        print(f_line)

    # R-Policy
    elif line_count is 8:
        print(f_line)

    # total blocks
    elif line_count is 10:
        total_blocks = f_line.split("(")
        total_blocks = total_blocks[0]
        print(total_blocks)

    # tag bits
    elif line_count is 11:
        print(f_line)

    # index bits and total rows
    elif line_count is 12:
        index_line_elements = f_line.split(",")
        index_bits = index_line_elements[0]
        index_line_elements = f_line.split(":")
        total_indices = index_line_elements[1]

        print(index_bits)
        print(total_indices)

    # total cache accesses
    elif line_count is 17:
        print(f_line)

    # Hits
    elif line_count is 18:
        print(f_line)

    # Misses
    elif line_count is 19:
        print(f_line)

    # Compulsory misses
    elif line_count is 20:
        print(f_line)

    # conflict misses
    elif line_count is 21:
        print(f_line)

    line_count += 1

''''
# create Workbook object
wb = Workbook()

# set file path
file_path = "/home/anthony/PycharmProjects/Cache_Sim/demo.xlsx"

# select demo.xlsx
sheet = wb.active

data = [('Trace File',
         "Cache Size",
         "Block Size",
         "Assoc",
         "R-Policy",
         "Tag Bits",
         "Index Bits",
         "Hits",
         "Misses",
         "Miss Rate %")]


# append all rows
for row in data:
    sheet.append(row)

r = 10
c = 11

sheet.cell(row=r, column=c).value = "FUCK"

# save file
wb.save(file_path)

'''
