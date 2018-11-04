#!/usr/bin/env python
#
# Generate a uuid to embed in firmware
# Looks for the following pattern in the input file:
#
#  struct device_guid s_eeprom_guid EEMEM = {
#    {
#        0xff,0xff,0xde,0xad,0xff,0xff,0xde,0xad,
#        0xff,0xff,0xde,0xad,0xff,0xff,0xde,0xad,
#    },
#  };
#
# when that pattern is found, replaces the 2 lines of uuid values with
# values generated from the uuid module

import os
import sys
import uuid
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--ifile", dest="ifilename",
                  help="File to place the generated uuid in")
parser.add_option("-o", "--ofile", dest="ofilename",
                  help="File to place the generated uuid in")
parser.add_option("-t", "--test", action="store_true", dest="test", default=False,
                  help="Don't rewrite the file, output to stdout")

def generate_uuid_lines():
    uid = uuid.uuid4()
    line1 = "0x%s%s,0x%s%s,0x%s%s,0x%s%s,0x%s%s,0x%s%s,0x%s%s,0x%s%s," % (
        uid.hex[0], uid.hex[1], uid.hex[2], uid.hex[3], uid.hex[4], uid.hex[5], uid.hex[6], uid.hex[7],
        uid.hex[8], uid.hex[9], uid.hex[10], uid.hex[11], uid.hex[12], uid.hex[13], uid.hex[14], uid.hex[15])
    line2 = "0x%s%s,0x%s%s,0x%s%s,0x%s%s,0x%s%s,0x%s%s,0x%s%s,0x%s%s," % (
        uid.hex[16], uid.hex[17], uid.hex[18], uid.hex[19], uid.hex[20], uid.hex[21], uid.hex[22], uid.hex[23],
        uid.hex[24], uid.hex[25], uid.hex[26], uid.hex[27], uid.hex[28], uid.hex[29], uid.hex[30], uid.hex[31])
    return (line1, line2)
        
def main(options, args):
    state = 0
    if options.test:
        g = sys.stdout
    else:
        g = open(options.ofilename, "w")
    with open(options.ifilename, "r") as f:
        for line in f.readlines():
            line = line.rstrip()
            if line == "struct device_guid s_eeprom_guid EEMEM = {": # start marker
                state = 1
                line1, line2 = generate_uuid_lines()
                g.write(line+'\n')
            elif state == 1:              # opening brace
                state = 2
                g.write(line+'\n')
            elif state == 2:
                g.write(line1+'\n')
                state = 3
            elif state == 3:
                g.write(line2+'\n')
                state = 0
            else:
                g.write(line+'\n')
             
if __name__ == '__main__':
    (options, args) = parser.parse_args()
    main(options, args)
