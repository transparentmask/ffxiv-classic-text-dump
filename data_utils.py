#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import codecs
import csv
from io import BytesIO
from specials import Specials
from xml_decode import *

UTF8_BOM_LEN = len(codecs.BOM_UTF8)
BASE_DATA_PATH = '../FINAL FANTASY XIV/data'


def sheet_id_to_path(sheet_id):
    return os.path.join(BASE_DATA_PATH,
                        '%0.2X' % ((sheet_id >> 24) & 0xFF),
                        '%0.2X' % ((sheet_id >> 16) & 0xFF),
                        '%0.2X' % ((sheet_id >> 8) & 0xFF),
                        '%0.2X.DAT' % ((sheet_id >> 0) & 0xFF))


def is_xml_file(path):
    with open(path, 'rb') as file:
        contents = file.read()
        return contents[-1] == 0xF1  # '\xF1'


def get_xml_from_path(path):
    if is_xml_file(path) is False:
        return None
    return decode(path)


def get_xml_from_sheet_id(sheet_id=0, sheet_path=None):
    if sheet_path is None:
        sheet_path = sheet_id_to_path(sheet_id)
    xml = get_xml_from_path(sheet_path)
    if xml is None:
        with open(sheet_path, 'rb') as file:
            xml = file.read()
            if ((xml[0] != '\xef' and xml[0] != 0xef) or (xml[1] != '\xbb' and xml[1] != 0xbb)) and xml[0] != '<':
                return None
            xml = xml.decode('UTF-8')
    return xml[UTF8_BOM_LEN:] if xml[:UTF8_BOM_LEN] == codecs.BOM_UTF8 else xml


# Export CSV
def get_row_indexes(enable_path):
    indexes = []
    with open(enable_path, 'rb') as file:
        ba = bytearray(file.read())
    index = 0
    while index < len(ba):
        start = hex2int(ba[index:index + 4])
        num = hex2int(ba[index + 4:index + 8])
        index += 8
        indexes.extend(list(range(start, start + num)))
    return [[i] for i in indexes]


def get_data_rows(sheet, block_path, data_path, offset_path, columns, rows, export_bin=False):
    with open(data_path, 'rb') as file:
        ba = bytearray(file.read())

    # merge same value in offset list
    with open(offset_path, 'rb') as file:
        offsets_ba = bytearray(file.read())
        offsets = [0]
        i = 0
        while i < len(offsets_ba):
            offset = hex2int(offsets_ba[i:i + 4])
            i += 4
            if offset == offsets[-1]:
                continue
            offsets.append(offset)

    size = len(ba)
    buf = BytesIO()
    buf.write(ba)
    buf.seek(0)

    if export_bin:
        block_file = open(block_path, 'wb')
    index = 0
    # print(data_path)
    for off_index, row in enumerate(rows):
        index = offsets[off_index]
        end = offsets[off_index + 1] if off_index < len(offsets) - 1 else len(ba)
        buf.seek(index)
        for col in columns:
            if (0 < end <= buf.tell()) or index >= size:
                break

            if col == 'str':
                str_len = hex2int(buf.read(2))
                if buf.read(1) != b'\xff':
                    _bytes = export_string_bytes(buf, buf.tell() - 1, str_len)
                else:
                    _bytes = bytes(map(lambda b: b ^ 0x73, buf.read(str_len - 1)))
                # if _bytes[-1] == 0x00:
                    # _bytes = _bytes[:-1]
                if export_bin:
                    block_file.write(int2hex(len(_bytes), 2))
                    block_file.write(_bytes)
                if _bytes[-1] == 0x00:
                    _bytes = _bytes[:-1]
                row.append(Specials.process(_bytes) if _bytes else '')
                # row.append(str(Specials.process(_bytes), 'utf8') if _bytes else '')
            else:
                byte = buf.read(DATA_SIZE[col])
                if export_bin:
                    block_file.write(byte)
                if col[0] == 'f':
                    row.append(hex2float(byte))
                elif col[0] == 's':
                    row.append(hex2int(byte, high_as_flag=True))
                else:
                    row.append(hex2int(byte))
    if export_bin:
        block_file.close()


def export_sheet(sheet, export_path, export_bin=False, return_dict=None):
    path = os.path.join(export_path, sheet.name, "%s.csv" % (sheet.lang if sheet.lang is not None and sheet.lang else "data"))
    # print(export_path)
    index_list = ["No"]
    index_list.extend(sheet.index_params)
    type_list = ["No"]
    type_list.extend(sheet.type_params)
    with codecs.open(path, 'w', 'utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(index_list)
        writer.writerow(type_list)
        for block in sheet.blocks:
            # print(block)
            block_name = '%s_%s.bin' % (sheet.lang, block.data) if sheet.lang is not None and sheet.lang else '%s.bin' % block.data
            block_path = os.path.join(export_path, sheet.name, block_name)
            enable_path = sheet_id_to_path(block.enable)
            offset_path = sheet_id_to_path(block.offset)
            data_path = sheet_id_to_path(block.data)
            if os.path.exists(enable_path):
                rows = get_row_indexes(enable_path)
                if os.path.exists(data_path) and os.path.exists(offset_path):
                    get_data_rows(sheet, block_path, data_path, offset_path, sheet.type_params, rows, export_bin)
                    writer.writerows(rows)

                    if return_dict is not None:
                        for row in rows:
                            key = str(row[0])
                            if key not in return_dict:
                                return_dict[key] = {}
                            for index, value in enumerate(row[1:]):
                                return_dict[key][str(sheet.index_params[index])] = value

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
