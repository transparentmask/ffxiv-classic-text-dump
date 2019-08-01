#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import sys
import os
from utils import *


def scramble_buffer(buf, size):
    start = 0
    end = size - 1
    while start < end:
        buf[start], buf[end] = buf[end], buf[start]
        start += 2
        end -= 2


def decode(path):
    # print(path)
    with open(path, 'rb') as f:
        ba = bytearray(f.read())
    if ba[-1] != '\xF1' and ba[-1] != 0xF1:
        return str(ba, 'utf-8')

    dst_len = len(ba) - 1
    scramble_buffer(ba, dst_len)

    xA = (dst_len * 7) & 0xFFFF
    xB = hex2int(ba[6:8]) ^ 0x6C6D

    start = 0
    end = dst_len - 1
    while start < end:
        tmp = hex2int(ba[start: start + 2]) ^ xA
        ba[start: start + 2] = int2hex(tmp, length=2)
        if start == 0:
            if (ba[0] != '\xef' and ba[0] != 0xef) or (ba[1] != '\xbb' and ba[1] != 0xbb):
                return None
        start += 4

    start = 2
    while start < end:
        tmp = hex2int(ba[start: start + 2]) ^ xB
        ba[start: start + 2] = int2hex(tmp, length=2)
        start += 4

    if ba[-2] != 10:
        ba[-2] ^= (xA & 0xFF)
        ba[-2] ^= (xB & 0xFF)

    try:
        return str(ba[:-1], 'utf-8')
    except UnicodeDecodeError:
        return str(process_special_chars_in_utf8(ba[:-1]), 'utf-8')


def main():
    if len(sys.argv) < 2:
        return

    for path in sys.argv[1:]:
        if not os.path.exists(path):
            continue
        print(decode(path))


if __name__ == '__main__':
    main()
