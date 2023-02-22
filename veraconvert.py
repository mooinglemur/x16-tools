#!/bin/env python3

# This utility converts raw VERA tile data from one bit depth to another.
# It can optionally extract tiles from a sort of "map" that is wider than one tile

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
parser.add_argument("-m", metavar="<map width>", type=int, help='Input map width in tiles, default is 1 tile', default=1, choices=range(1,65))
parser.add_argument("-x", metavar="<tile width>", type=int, help='Tile width, default is 8', default=8, choices=[8,16])
parser.add_argument("-y", metavar="<tile height>", type=int, help='Tile height, default is 8', default=8, choices=[8,16])
parser.add_argument("-b", metavar="<bpp>", type=int, help='Input file BPP, default is 8', default=8, choices=[1,2,4,8])
parser.add_argument("-d", metavar="<bpp>", type=int, help='Output file BPP, default is 4', default=4, choices=[1,2,4,8])
parser.add_argument("-i", metavar="input.bin", type=argparse.FileType('rb'), help='Indexed tilemap input file', required=True)
parser.add_argument("-o", metavar="output.bin", type=argparse.FileType('wb'), help='Output tile data for VERA', required=True)
parser.add_argument("-p", metavar="output.idx", type=argparse.FileType('wb'), help='Output tile palette index file (only useful for 8bpp input, and 4bpp or 2bpp output)')


args = parser.parse_args()

o_tile = [] # Output tile data, one pixel per element
o_pal = 0
t_idx = 0
t_byte = 0

while (byte := args.i.read(1)):
    bint = ord(byte)
    # After grabbing a single byte of tile data input

    # Set this tile's palette for the purposes of -p
    o_pal = (bint >> 4) & 0x0f

    # Extract the individual pixels out of the source byte
    # And put them into the output pixels
    for i in range(math.floor(8/args.b)):
        bint = rol(bint, args.b, 8)
        o_tile.append(bint & (2**args.b-1))

    t_byte += 1
    # See if it's time to write out the output tile
    if (t_byte >= args.x * args.y * (args.b/8)):
        obyte = 0
        while (len(o_tile) > 0):
            # Coalesce the output pixels into bytes
            for i in range(math.floor(8/args.d)):
                obyte = rol(obyte, args.d, 8)
                obyte = (obyte & (0xff ^ (2**args.d-1))) | (o_tile.pop(0) & (2**args.d-1))
            # Write out the combined byte
            args.o.write(obyte.to_bytes(1, 'little'))
        if (args.p):
            args.p.write(o_pal.to_bytes(1, 'little'))
        o_tile = []
        t_idx += 1
        t_byte = 0

    # Seek to where to grab the next input byte
    col_offset = math.floor((t_idx % args.m) * (args.x / (8/args.b)) + (t_byte % (args.x / (8/args.b))))
    row_offset = math.floor((math.floor(t_idx / args.m) * args.y) + math.floor((t_byte / math.floor(8/args.b)) / args.x))
    bytes_per_row = math.floor((args.m * args.x) / math.floor(8/args.b))

    # print("x: {} y: {} tile: {} byte: {} bpr: {} offset: {}".format(col_offset, row_offset, t_idx, t_byte, bytes_per_row, row_offset * bytes_per_row + col_offset))

    args.i.seek(row_offset * bytes_per_row + col_offset)


