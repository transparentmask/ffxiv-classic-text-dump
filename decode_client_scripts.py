#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import os
from subprocess import Popen, PIPE
from utils import *
import tempfile


BASE_DATA_PATH = '../FINAL FANTASY XIV/client/script'
EXPORT_PATH = 'client/script'

MAGIC_HEADER = b'\x72\x6C\x65\x0C'
MAGIC_HEADER_LEN = len(MAGIC_HEADER) + 4
UNLUA_JAR_PATH = 'unluac_2015_06_13.jar'

MAGIC_HEADER_NO_XOR = b'\x72\x6C\x75\x0B'
MAGIC_HEADER_NO_XOR_LEN = len(MAGIC_HEADER_NO_XOR)

MAGIC_HEADER_SAN = b'\x73\x61\x6E\x65'
MAGIC_HEADER_SAN_LEN = len(MAGIC_HEADER_SAN)

NAME_SEQ = list("_abcdefghijklmnopqrstuvwxyz0123456789_")
NAME_SEQ_REV = list(reversed(NAME_SEQ))


def decode_file_name(name):
    return ''.join([NAME_SEQ_REV[NAME_SEQ.index(char)] for char in list(name)])


def call_unlua(contents):
    temp = tempfile.NamedTemporaryFile()
    temp.write(contents)
    temp.flush()

    proc = Popen(['java', '-jar', UNLUA_JAR_PATH, temp.name], stdout=PIPE)
    decoded = proc.stdout.read()
    temp.close()

    if len(decoded) == 0:
        raise Exception
    return decoded


def decode(file_path, target_path):
    with open(file_path, 'rb') as f:
        contents = bytearray(f.read())

    try:
        if contents.startswith(MAGIC_HEADER):
            length = hex2int(contents[MAGIC_HEADER_LEN:MAGIC_HEADER_LEN + 4])
            start = MAGIC_HEADER_LEN + 4
            if contents[start] == 0xFF:
                start += 1
                for i in range(start, start + length):
                    contents[i] ^= 0x73
            decoded = call_unlua(contents[start:])
            with open(target_path, 'wb') as f:
                f.write(decoded)
        elif contents.startswith(MAGIC_HEADER_NO_XOR):
            length = hex2int(contents[MAGIC_HEADER_NO_XOR_LEN:MAGIC_HEADER_NO_XOR_LEN + 4])
            start = MAGIC_HEADER_NO_XOR_LEN + 4
            if contents[start] == 0xFF:
                start += 1
                for i in range(start, start + length):
                    contents[i] ^= 0x73
            decoded = contents[start:]
            with open(target_path, 'wb') as f:
                f.write(decoded)
        elif contents.startswith(MAGIC_HEADER_SAN):
            length = hex2int(contents[MAGIC_HEADER_SAN_LEN:MAGIC_HEADER_SAN_LEN + 4], bigEndian=True)
            start = MAGIC_HEADER_SAN_LEN + 4
            if contents[start] == 0xFF:
                start += 1
                for i in range(start, start + length):
                    contents[i] ^= 0x73
            decoded = contents[start:]
            with open(target_path, 'wb') as f:
                f.write(decoded)
        else:
            print('not correct file: %s' % file_path)
    except Exception:
        print('decode failed: %s' % file_path)


def main():
    list_dirs = os.walk(BASE_DATA_PATH)
    for root, dirs, files in list_dirs:
        sub_root = root.replace(BASE_DATA_PATH, '', 1).strip(os.sep).split(os.sep)
        target_root = os.path.join(EXPORT_PATH, os.sep.join([decode_file_name(s) for s in sub_root]))
        try:
            os.makedirs(target_root)
        except Exception:
            pass
        for file in files:
            file_path = os.path.join(root, file)
            file = '%s.%s' % (decode_file_name(file.split('.')[0]), 'san' if file.endswith('san') else 'lua')
            target_path = os.path.join(target_root, file)
            decode(file_path, target_path)


if __name__ == '__main__':
    # print(decode_file_name('rq9qpr89r57y9rr'))
    # decode('../FINAL FANTASY XIV/client/script/0p635/0p63589r57y9rr.le.lpb', '')
    main()
