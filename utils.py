#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import struct


def int2hex(value, length=4, bigEndian=False):
    flag = '>' if bigEndian else '<'
    if length == 1:
        flag += 'B'
    elif length == 2:
        flag += 'H'
    elif length == 4:
        flag += 'I'

    if value < 0:
        flag = flag.lower()

    return bytearray(struct.pack(flag, value))


def hex2int(hex_ba, bigEndian=False, highAsFlag=False):
    flag = '>' if bigEndian else '<'
    if len(hex_ba) == 1:
        flag += 'B'
    elif len(hex_ba) == 2:
        flag += 'H'
    elif len(hex_ba) == 4:
        flag += 'I'

    if highAsFlag:
        flag = flag.lower()

    return struct.unpack(flag, hex_ba)[0]


def hex2float(hex_ba, bigEndian=False):
    flag = '>' if bigEndian else '<'
    if len(hex_ba) == 2:
        flag += 'e'
    elif len(hex_ba) == 4:
        flag += 'f'

    return struct.unpack(flag, hex_ba)[0]


def export_string(data, start=0, count=0, terminator='\x00'):
    if count == 0:
        t = data[start:].find(terminator) + start + 1
    else:
        t = start + count
    d = data[start:t]
    return (d[:-1], t)


def process_special_chars_in_utf8(ba):
    i = 0
    count = len(ba)
    while i < count:
        if (ba[i] & 0x80) == 0:
            i += 1
            continue

        if (ba[i] & 0xE0) == 0xC0:
            valid = False
            byte1 = 0
            t = i
            i += 1
            if i < count:
                byte1 = ba[i]
                i += 1
                valid = True
            if (byte1 & 0xC0) != 0x80:
                valid = False
            if not valid:
                for ii in range(t, i):
                    ba[ii] = ord('?')

        elif (ba[i] & 0xF0) == 0xE0:
            valid = False
            byte1 = 0
            byte2 = 0
            t = i
            i += 1
            if i < count:
                byte1 = ba[i]
                i += 1
                if i < count:
                    byte2 = ba[i]
                    i += 1
                    valid = True
            if (byte1 & 0xC0) != 0x80 or (byte2 & 0xC0) != 0x80:
                valid = False
            if not valid:
                for ii in range(t, i):
                    ba[ii] = ord('?')
        else:
            ba[i] = ord('?')
            i += 1

    return ba
