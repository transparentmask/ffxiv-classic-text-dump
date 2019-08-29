#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from enum import Enum, unique
from utils import hex2int

@unique
class IntegerType(Enum):
    Byte = 0xF0
    ByteTimes256 = 0xF1
    Int16 = 0xF2
    Int24 = 0xFA
    Int32 = 0xFE

    @staticmethod
    def get_value(_buf, type_value=None, length=0):
        if not type_value:
            type_value = ord(_buf.read(1))
        if isinstance(type_value, IntegerType):
            type_value = type_value.value
        if type_value < 0xF0:
            return type_value - 1

        integer_type = IntegerType(type_value)
        if integer_type == IntegerType.Byte:
            return ord(_buf.read(1))
        elif integer_type == IntegerType.ByteTimes256:
            return ord(_buf.read(1)) * 256
        elif integer_type == IntegerType.Int16:
            return hex2int(_buf.read(2), big_endian=True)
        elif integer_type == IntegerType.Int24:
            return hex2int(bytearray(b'\x00') + _buf.read(3), big_endian=True)
        elif integer_type == IntegerType.Int32:
            return hex2int(_buf.read(4), big_endian=True)
