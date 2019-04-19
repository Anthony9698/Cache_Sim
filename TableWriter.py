#!/usr/bin/python3

from openpyxl import Workbook
import sys
import re

if len(sys.argv) < 2:
    print("--- Input file required ---")
    sys.exit(-1)


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
         "Total Blocks",
         "Tag Bits",
         "Index Bits",
         "Total Rows",
         "Total CA",
         "Hits",
         "Misses",
         "Comp Misses",
         "Conflict Misses",
         "Miss Rate %")]


file_name = sys.argv[1]
try:
    input_file = open(file_name, "r")
except FileNotFoundError:
    raise FileNotFoundError("Input file does not exist")

line_count = 1
new_row = []
for line in input_file:
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
        new_row = []
        trace_file = f_line
        new_row.append(trace_file)

    # cache size
    elif line_count is 5:
        cache_size = f_line
        new_row.append(cache_size)

    # block size
    elif line_count is 6:
        block_size = f_line.split("bytes")
        block_size = block_size[0] + "B"
        new_row.append(block_size)

    # assoc
    elif line_count is 7:
        assoc = f_line
        new_row.append(assoc)

    # R-Policy
    elif line_count is 8:
        r_policy = f_line
        new_row.append(r_policy)

    # total blocks
    elif line_count is 10:
        total_blocks = f_line.split("(")
        total_blocks = total_blocks[0]
        new_row.append(total_blocks)

    # tag bits
    elif line_count is 11:
        tag_bits = f_line
        new_row.append(tag_bits)

    # index bits and total rows
    elif line_count is 12:
        index_line_elements = f_line.split(",")
        index_bits = index_line_elements[0]
        index_line_elements = f_line.split(":")
        total_indices = index_line_elements[1]
        new_row.append(index_bits)
        new_row.append(total_indices)

    # total cache accesses
    elif line_count is 17:
        total_CA = f_line
        new_row.append(total_CA)

    # Hits
    elif line_count is 18:
        hits = f_line
        new_row.append(hits)

    # Misses
    elif line_count is 19:
        misses = f_line
        new_row.append(misses)

    # Compulsory misses
    elif line_count is 20:
        comp_misses = f_line
        new_row.append(comp_misses)

    # Conflict misses
    elif line_count is 21:
        conflict_misses = f_line
        new_row.append(conflict_misses)

    # Miss rate
    elif line_count is 26:
        miss_rate = line.split("=")
        miss_rate = miss_rate[1]
        new_row.append(miss_rate)

    line_count += 1

    if line_count == 27:
        data.append(new_row)
        line_count = 1

# write all rows to table
for row in data:
    sheet.append(row)

wb.save(file_path)
