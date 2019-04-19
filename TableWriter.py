#!/usr/bin/python3

from openpyxl import Workbook
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
        f_line = re.sub('')
        print(f_line)

    # cache size
    elif line_count is 5:
        print(f_line)

    # block size
    elif line_count is 6:
        print(f_line)

    # assoc
    elif line_count is 7:
        print(f_line)

    # R-Policy
    elif line_count is 8:
        print(f_line)

    # total blocks
    elif line_count is 10:
        print(f_line)

    # tag bits
    elif line_count is 11:
        print(f_line)

    # index bits and total rows
    elif line_count is 12:
        print(f_line)

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

print("DONE")

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
