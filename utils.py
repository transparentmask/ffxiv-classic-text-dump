#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import struct


DATA_SIZE = {
    's8': 1,
    'u8': 1,
    'bool': 1,
    's16': 2,
    'u16': 2,
    'f16': 2,
    's32': 4,
    'u32': 4,
    'float': 4
}


def int2hex(value, length=4, big_endian=False):
    flag = '>' if big_endian else '<'
    if length == 1:
        flag += 'B'
    elif length == 2:
        flag += 'H'
    elif length == 4:
        flag += 'I'

    if value < 0:
        flag = flag.lower()

    return bytearray(struct.pack(flag, value))


def hex2int(hex_ba, big_endian=False, high_as_flag=False):
    flag = '>' if big_endian else '<'
    if len(hex_ba) == 1:
        flag += 'B'
    elif len(hex_ba) == 2:
        flag += 'H'
    elif len(hex_ba) == 4:
        flag += 'I'

    if high_as_flag:
        flag = flag.lower()

    return struct.unpack(flag, hex_ba)[0]


def hex2float(hex_ba, big_endian=False):
    flag = '>' if big_endian else '<'
    if len(hex_ba) == 2:
        flag += 'e'
    elif len(hex_ba) == 4:
        flag += 'f'

    return struct.unpack(flag, hex_ba)[0]


def export_string(data, start=0, count=0, terminator='\x00'):
    if count == 0:
        end = data[start:].find(terminator) + start + 1
    else:
        end = start + count
    data = data[start:end]
    return (data[:-1], end)


def export_string_bytes(buf, start=0, count=0, terminator=b'\x00'):
    if start == 0:
        start = buf.tell()
    if count == 0:
        while buf.read(1) != terminator:
            pass
        count = buf.tell() - start

    buf.seek(start)
    return buf.read(count)


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
