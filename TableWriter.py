#!/usr/bin/python3

from openpyxl import Workbook
import sys
data = sys.stdin.readlines()

for line in data:
    line = line.strip('\n')
    line = line.strip('\t')

    print(line)

''''
# create Workbook object
wb = Workbook()

# set file path
file_path = "/home/anthony/Desktop/demo.xlsx"

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

# save file
wb.save(file_path)
'''

