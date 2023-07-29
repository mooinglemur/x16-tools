#!/bin/env python3

# This tool converts from a raw VERA 8bpp bitmap to a custom RLE format
# using 4bpp, with an optional palette header.
#
# The RLE data is comprised of one or two unit types, depending on
# the number of repeats.  e.g.: Zero repeats means a single instance,
# one repeat means two of the same color in sequence.
#
# Type 1: 0x00-0xef # when number of repeats is 0-14 
#     low nibble = color
#     high nibble = number of repeats
# Type 2: 0xf0-0xff, 0x00-0xff # when number of repeats is 15+
#     first byte: low nibble = color
#     second byte = number of repeats - 15

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

s_cnt = 0 # source counter
d_cnt = 0 # dest counter
r_rpt = 0 # current repeat counter
p_cnt = 0 # palette entry count
color = 0 # default color


def do_output():
    global r_rpt
    global d_cnt
    global last_color
    if r_rpt < 15:
        oint = last_color + (r_rpt*16)
        args.o.write(oint.to_bytes(1, 'little'))
        d_cnt += 1
    else:
        oint = last_color + 240
        args.o.write(oint.to_bytes(1, 'little'))
        oint = r_rpt - 15
        args.o.write(oint.to_bytes(1, 'little'))
        d_cnt += 2

def inner_loop():
    global color
    global last_color
    global s_cnt
    global r_rpt
    while (ibyte := args.i.read(1)):
        color = ord(ibyte) & 0x0f
        s_cnt += 1
        if color != last_color:
            do_output()
            return True
        elif r_rpt == 255:
            do_output()
            return True
        r_rpt += 1
    return False
        

def outer_loop():
    global color
    global last_color
    global r_rpt
    global s_cnt
    n_getnew = True # whether to get new input color (first pass)
    while True:
        if n_getnew:
            ibyte = args.i.read(1)
            if not ibyte: # end of file
                return
            color = ord(ibyte) & 0x0f
            n_getnew = False
            s_cnt += 1
        last_color = color
        r_rpt = 0
        if not inner_loop():
            do_output()
            return

def color8to4(n):
    return (n * 15 + 135) >> 8 # uses rounding to so 0xFF becomes 0x0F, but 0xF0 rounds to 0x0E, etc.

def process_pal():
    global d_cnt
    global p_cnt
    state = 0
    for line in args.p:
        if state == 0: # JASC-PAL
            state = 1
            continue
        if state == 1: # 0100
            state = 2
            continue
        if state == 2: # number of lines
            state = 3
            continue
        if state == 3:
            rgb = [int(n) for n in line.split()]
            rgbval = color8to4(rgb[0]) << 8
            rgbval = rgbval | (color8to4(rgb[1]) << 4)
            rgbval = rgbval | color8to4(rgb[2])
            args.o.write(rgbval.to_bytes(2, 'little')) # this does our little-endian word
            d_cnt += 2
            p_cnt += 1


parser = argparse.ArgumentParser()
parser.add_argument("-i", metavar="input.bin", type=argparse.FileType('rb'), help='8bpp raw input image', required=True)
parser.add_argument("-p", metavar="palette.pal", type=argparse.FileType('r'), help='JASC (Paint Shop Pro) palette input file', required=False)
parser.add_argument("-o", metavar="output.bin", type=argparse.FileType('wb'), help='RLE-encoded 4bpp output image', required=True)
parser.add_argument("-r", action='store_true', help='Add RLX header 0x52 0x4C 0x58 0x00 to the beginning of the output file', required=False)

args = parser.parse_args()

print("Working...")
if (args.r):
    args.o.write(b'\x52\x4C\x58\x00')
    d_cnt += 4
if (args.p):
    process_pal()
outer_loop()
print("Finished: RLE input size: {}, palette size: {} ({} bytes), output size: {}".format(s_cnt, p_cnt, p_cnt*2, d_cnt));
