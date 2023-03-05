#!/bin/env python3

# This utility converts raw VERA bitmap data from one bit depth to another.

# Copyright 2023 MooingLemur

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import math

def rol(n,rotations,width):
    return (2**width-1)&(n<<rotations|n>>(width-rotations))

parser = argparse.ArgumentParser()
parser.add_argument("-b", metavar="<bpp>", type=int, help='Input file BPP, default is 8', default=8, choices=[1,2,4,8])
parser.add_argument("-d", metavar="<bpp>", type=int, help='Output file BPP, default is 4', default=4, choices=[1,2,4,8])
parser.add_argument("-i", metavar="input.bin", type=argparse.FileType('rb'), help='Input bitmap', required=True)
parser.add_argument("-o", metavar="output.bin", type=argparse.FileType('wb'), help='Output bitmap', required=True)


args = parser.parse_args()

o_tile = [] # Output bitmap data, one pixel per element
o_pal = 0
t_byte = 0

while (byte := args.i.read(1)):
    bint = ord(byte)
    # After grabbing a single byte of tile data input

    # Extract the individual pixels out of the source byte
    # And put them into the output pixels
    for i in range(math.floor(8/args.b)):
        bint = rol(bint, args.b, 8)
        o_tile.append(bint & (2**args.b-1))

obyte = 0
while (len(o_tile) > 0):
    # Coalesce the output pixels into bytes
    for i in range(math.floor(8/args.d)):
        obyte = rol(obyte, args.d, 8)
        obyte = (obyte & (0xff ^ (2**args.d-1))) | (o_tile.pop(0) & (2**args.d-1))
    # Write out the combined byte
    args.o.write(obyte.to_bytes(1, 'little'))
