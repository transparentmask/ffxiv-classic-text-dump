#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import os
from lxml.etree import fromstring
import codecs
from utils import *
from data_utils import *
from data_types import *


EXPORT_PATH = 'sheets_new'
EXPORT_BIN = False


def main():
    try:
        os.makedirs(EXPORT_PATH)
    except OSError:
        pass

    with open('new_xml_list.txt', 'r') as f:
        new_xml_list = f.readlines()
    new_xml_list = [x.strip() for x in new_xml_list]

    for new_xml in new_xml_list:
        new_xml_path = os.path.join(BASE_DATA_PATH, new_xml)
        try:
            xml = get_xml_from_path(new_xml_path)
            if xml is None:
                with open(path, 'rb') as f:
                    xml = f.read().decode('UTF-8')
            xml = xml[UTF8_BOM_LEN:] if xml[:UTF8_BOM_LEN] == codecs.BOM_UTF8 else xml
            sheet_doc = fromstring(xml)
        except Exception:
            continue
        if sheet_doc.find('sheet').get('infofile') is not None:
            print('%s: (%s)' % (sheet_doc.find('sheet').get('name'), new_xml_path))
            continue
        if sheet_doc.find('sheet').get('lang') is None:
            continue
        print('%s: (%s)' % (sheet_doc.find('sheet').get('name'), new_xml_path))
        path = os.path.join(EXPORT_PATH, sheet_doc.find('sheet').get('name').replace('/', os.sep))
        try:
            os.makedirs(path)
        except OSError:
            pass
        with codecs.open(os.path.join(path, 'sheet.xml'), 'w', 'utf-8') as f:
            f.write(xml)
            for sheet in sheet_doc.iterfind('sheet'):
                sheet_info = SheetInfo(sheet)
                # if sheet_info.lang and sheet_info.lang not in ['chs', 'ja', 'en']:
                #     continue
                export_sheet(sheet_info, EXPORT_PATH, EXPORT_BIN)


if __name__ == '__main__':
    main()
