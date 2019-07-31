#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import os


class Block:
    def __init__(self, block_file):
        self.begin = int(block_file.get('begin'))
        self.count = int(block_file.get('count'))
        self.offset = int(block_file.get('offset'))
        self.enable = int(block_file.get('enable'))
        self.data = int(block_file.text)

    def __str__(self):
        return "begin: %d; count: %d; offset: %d; enable: %d; data: %d" % (self.begin, self.count, self.offset, self.enable, self.data)


class SheetInfo:
    def __init__(self, sheet):
        self.name = sheet.get('name').replace('/', os.sep)
        self.mode = sheet.get('mode')
        self.column_max = int(sheet.get('column_max'))
        self.column_count = int(sheet.get('column_count'))
        self.cache = sheet.get('cache')
        self.type = sheet.get('type')
        self.lang = sheet.get('lang')
        self.type_params = []
        for type_param in sheet.iterfind('type/param'):
            self.type_params.append(type_param.text)
        self.index_params = []
        for index_param in sheet.iterfind('type/index'):
            self.index_params.append(int(index_param.text))
        self.blocks = []
        for block_file in sheet.iterfind('block/file'):
            self.blocks.append(Block(block_file))
