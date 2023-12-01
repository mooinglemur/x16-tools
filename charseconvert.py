#!/bin/env python3

# This utility converts between ASCII and CX16 character sets

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

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()
        self.exit(2, f"\nError: {message}\n")

parser = MyParser(
    epilog="The -c parameter is the conversion type. Valid values are asc2pet or pet2asc. The default is asc2pet."
)
parser.add_argument("-c", metavar="<type>", help='Conversion type', default='asc2pet', choices=['asc2pet','pet2asc'])
parser.add_argument("-i", metavar="input.txt", type=argparse.FileType('rb'), help='Input file', required=True)
parser.add_argument("-o", metavar="output.txt", type=argparse.FileType('wb'), help='Output file', required=True)

args = parser.parse_args()

inp = args.i.read()

if (args.c == 'asc2pet'):
    for byte in inp:
        if byte < 0x41: # non-printables, numbers and symbols that are the same in PETSCII as ASCII
            pass
        elif byte < 0x5b: # uppercase letters
            byte += 0x80
        elif byte < 0x61: # symbols in between (£ == \,↑ = ^, ← = _, and we leave the backtick alone even though it becomes PETSCII)
            pass
        elif byte < 0x7b: # lowercase letters
            byte -= 0x20
        args.o.write(byte.to_bytes())
elif (args.c == 'pet2asc'):
    for byte in inp:
        if byte < 0x41: # non-printables, numbers and symbols that are the same in PETSCII as ASCII
            pass
        elif byte < 0x5b: # lowercase letters
            byte += 0x20
        elif byte < 0x61: # symbols in between (£ == \,↑ = ^, ← = _)
            pass
        elif byte < 0x7b: # uppercase letters in the wrong spot
            byte -= 0x20
        elif byte < 0xc1: # non-printables and graphics that don't correspond to ASCII
            pass
        elif byte < 0xe0: # uppercase letters
            byte -= 0x80
        args.o.write(byte.to_bytes())
