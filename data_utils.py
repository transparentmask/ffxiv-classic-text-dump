#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import os
from xml_decode import decode
from utils import *
from xml_decode import *
from specials import Specials
import csv
import codecs


UTF8_BOM_LEN = len(codecs.BOM_UTF8)
BASE_DATA_PATH = '../FINAL FANTASY XIV/data'


def sheet_id_to_path(sheet_id):
    return os.path.join(BASE_DATA_PATH,
                        '%0.2X' % ((sheet_id >> 24) & 0xFF),
                        '%0.2X' % ((sheet_id >> 16) & 0xFF),
                        '%0.2X' % ((sheet_id >> 8) & 0xFF),
                        '%0.2X.DAT' % ((sheet_id >> 0) & 0xFF))


def is_xml_file(path):
    with open(path, 'rb') as f:
        contents = f.read()
        return contents[-1] == 241  # '\xF1'


def get_xml_from_path(path):
    if is_xml_file(path) is False:
        return None
    return decode(path)


def get_xml_from_sheet_id(sheet_id=0, sheet_path=None):
    if sheet_path is None:
        sheet_path = sheet_id_to_path(sheet_id)
    xml = get_xml_from_path(sheet_path)
    if xml is None:
        with open(sheet_path, 'rb') as f:
            xml = f.read()
            if ((xml[0] != '\xef' and xml[0] != 239) or (xml[1] != '\xbb' and xml[1] != 187)) and xml[0] != '<':
                return None
            xml = xml.decode('UTF-8')
    return xml[UTF8_BOM_LEN:] if xml[:UTF8_BOM_LEN] == codecs.BOM_UTF8 else xml


# Export CSV
def get_row_indexes(enable_path):
    indexes = []
    with open(enable_path, 'rb') as f:
        ba = bytearray(f.read())
    index = 0
    while index < len(ba):
        start = hex2int(ba[index:index + 4])
        num = hex2int(ba[index + 4:index + 8])
        index += 8
        indexes.extend(list(range(start, start + num)))
    return [[i] for i in indexes]


def get_data_rows(sheet, data_path, offset_path, columns, rows):
    with open(data_path, 'rb') as f:
        ba = bytearray(f.read())
    with open(offset_path, 'rb') as f:
        offsets_ba = bytearray(f.read())
        offsets = [0]
        i = 0
        while i < len(offsets_ba):
            offset = hex2int(offsets_ba[i:i + 4])
            i += 4
            if offset == offsets[-1]:
                continue
            offsets.append(offset)
    index = 0
    for off_index, row in enumerate(rows):
        # end = 0
        # if 'xtx/quest' == sheet.name:
        #     index = offsets[off_index]
        #     end = offsets[off_index + 1] if off_index < len(offsets) - 1 else len(ba)
        index = offsets[off_index]
        end = offsets[off_index + 1] if off_index < len(offsets) - 1 else len(ba)
        for col in columns:
            if (end > 0 and index >= end) or index >= len(ba):
                break

            if col == 's8' or col == 'u8' or col == 'bool':
                row.append(hex2int(ba[index:index + 1], highAsFlag=(col == 's8')))
                index += 1
            elif col == 's16' or col == 'u16':
                row.append(hex2int(ba[index:index + 2], highAsFlag=(col == 's16')))
                index += 2
            elif col == 'f16':
                row.append(hex2float(ba[index:index + 2]))
                index += 2
            elif col == 's32' or col == 'u32':
                row.append(hex2int(ba[index:index + 4], highAsFlag=(col == 's32')))
                index += 4
            elif col == 'float':
                row.append(hex2float(ba[index:index + 4]))
                index += 4
            elif col == 'str':
                str_len = hex2int(ba[index:index + 2])
                index += 2
                if ba[index] != 0xFF:
                    (string, _) = export_string(ba, index, str_len)
                else:
                    sl = str_len - 1
                    for i in range(1, sl):
                        ba[index + i] ^= 0x73
                    string = ba[index + 1:index + sl]
                string_procceed = Specials.process(string)
                try:
                    row.append(str(process_special_chars_in_utf8(string_procceed), "utf-8"))
                except Exception:
                    print(string)
                    print(string_procceed)
                    exit(0)

                index += str_len


def export_sheet(sheet, export_path):
    export_path = os.path.join(export_path, sheet.name, "%s.csv" % (sheet.lang if sheet.lang is not None else "data"))
    # print(export_path)
    with codecs.open(export_path, 'w', 'utf-8') as csvfile:
        writer = csv.writer(csvfile)
        head = ["No"]
        head.extend(sheet.type_params)
        writer.writerow(head)
        for block in sheet.blocks:
            # print(block)
            enable_path = sheet_id_to_path(block.enable)
            offset_path = sheet_id_to_path(block.offset)
            data_path = sheet_id_to_path(block.data)
            if os.path.exists(enable_path):
                rows = get_row_indexes(enable_path)
                if os.path.exists(data_path) and os.path.exists(offset_path):
                    get_data_rows(sheet, data_path, offset_path, sheet.type_params, rows)
                    writer.writerows(rows)
                else:
                    if not os.path.exists(offset_path):
                        print("\t***%s offset missing: %s" % (sheet.lang, offset_path))
                    if not os.path.exists(data_path):
                        print("\t***%s data missing: %s" % (sheet.lang, data_path))
            else:
                print("\t***%s enable missing: %s" % (sheet.lang, enable_path))
                if not os.path.exists(offset_path):
                    print("\t***%s offset missing: %s" % (sheet.lang, offset_path))
                if not os.path.exists(data_path):
                    print("\t***%s data missing: %s" % (sheet.lang, data_path))


# Export JSON
def get_row_indexes_json(enable_path):
    indexes = []
    with open(enable_path, 'rb') as f:
        ba = bytearray(f.read())
    index = 0
    while index < len(ba):
        start = hex2int(ba[index:index + 4])
        num = hex2int(ba[index + 4:index + 8])
        index += 8
        indexes.extend(list(range(start, start + num)))
    return [str(i) for i in indexes]


def get_row_data_json(data_path, offset_path, columns, data, rows, lang):
    with open(data_path, 'rb') as f:
        ba = bytearray(f.read())
    with open(offset_path, 'rb') as f:
        offsets_ba = bytearray(f.read())
        offsets = []
        for i in range(len(rows)):
            offsets.append(hex2int(offsets_ba[i * 4:i * 4 + 4]))

    index = 0
    for off_index, row in enumerate(rows):
        index = offsets[off_index]
        end = offsets[off_index + 1] if off_index < len(offsets) - 1 else len(ba)
        if row not in data or lang not in data[row]:
            print('err')
            continue

        r = data[row][lang]
        for col in columns:
            if index >= end:
                break

            if col == 's8' or col == 'u8' or col == 'bool':
                r.append(hex2int(ba[index:index + 1], highAsFlag=(col == 's8')))
                index += 1
            elif col == 's16' or col == 'u16':
                r.append(hex2int(ba[index:index + 2], highAsFlag=(col == 's16')))
                index += 2
            elif col == 'f16':
                r.append(hex2float(ba[index:index + 2]))
                index += 2
            elif col == 's32' or col == 'u32':
                r.append(hex2int(ba[index:index + 4], highAsFlag=(col == 's32')))
                index += 4
            elif col == 'float':
                r.append(hex2float(ba[index:index + 4]))
                index += 4
            elif col == 'str':
                str_len = hex2int(ba[index:index + 2])
                index += 2
                if ba[index] != 0xFF:
                    (string, _) = export_string(ba, index, str_len)
                    r.append(str(process_special_chars_in_utf8(string), "utf-8"))
                else:
                    sl = str_len - 1
                    for i in range(1, sl):
                        ba[index + i] ^= 0x73
                    r.append(str(process_special_chars_in_utf8(ba[index + 1:index + sl]), 'utf-8'))

                index += str_len


def export_sheet_json(sheet, data):
    for block in sheet.blocks:
        enable_path = sheet_id_to_path(block.enable)
        offset_path = sheet_id_to_path(block.offset)
        data_path = sheet_id_to_path(block.data)
        if not os.path.exists(enable_path):
            print("\t***%s enable missing: %s" % (sheet.lang, enable_path))
            continue
        if not os.path.exists(data_path):
            print("\t***%s offset missing: %s" % (sheet.lang, offset_path))
            continue
        if not os.path.exists(offset_path):
            print("\t***%s data missing: %s" % (sheet.lang, data_path))
            continue

        rows = get_row_indexes_json(enable_path)
        for row in rows:
            if row not in data:
                data[row] = {}
            if sheet.lang is None:
                data[row]['data'] = []
            elif sheet.lang not in data[row]:
                data[row][sheet.lang] = []
        get_row_data_json(data_path, offset_path, sheet.type_params, data, rows, sheet.lang if sheet.lang is not None else 'data')
