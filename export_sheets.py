#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import os
from lxml.etree import fromstring
import codecs
from utils import *
from data_utils import *
from data_types import *


EXPORT_PATH = 'sheets'
BASE_SHEET_ID = 16973824


def main():
    try:
        os.makedirs(EXPORT_PATH)
    except OSError:
        pass

    # # xtx/text_directName: 189071391 (data/0B/45/00/1F.DAT)
    # # xtx/quest: 189072473
    # xml = get_xml_from_sheet_id(189072473)
    # sheet_doc = fromstring(xml)
    # for sheet in reversed(list(sheet_doc.iterfind('sheet'))):
    #     sheet_info = SheetInfo(sheet)
    #     print(sheet_info)
    #     export_sheet(sheet_info, EXPORT_PATH)
    #     break
    # exit(0)

    xml = get_xml_from_sheet_id(BASE_SHEET_ID)
    with codecs.open(os.path.join(EXPORT_PATH, 'sheets_list.xml'), 'w', 'utf-8') as f:
        f.write(xml)

    all_xmls = [BASE_SHEET_ID]

    doc = fromstring(xml)
    for sheet_line in doc.iterfind('sheet'):
        sheet_id = int(sheet_line.get('infofile'))
        print('%s: %d (%s)' % (sheet_line.get('name'), sheet_id, sheet_id_to_path(sheet_id)))
        xml = get_xml_from_sheet_id(sheet_id)
        if xml is None:
            print('\t *** Not correct xml')
            continue
        path = os.path.join(EXPORT_PATH, sheet_line.get('name').replace('/', os.sep))
        try:
            os.makedirs(path)
        except OSError:
            pass
        with codecs.open(os.path.join(path, 'sheet.xml'), 'w', 'utf-8') as f:
            f.write(xml)
            sheet_doc = fromstring(xml)
            # data = {}
            for sheet in sheet_doc.iterfind('sheet'):
                sheet_info = SheetInfo(sheet)
                export_sheet(sheet_info, EXPORT_PATH)
            #     export_sheet_json(sheet_info, data)
            # with codecs.open(os.path.join(EXPORT_PATH, sheet_info.name, "data.json"), 'w', 'utf-8') as f:
            #     json.dump(data, f, ensure_ascii=False, indent=4)
        all_xmls.append(sheet_id)

    with open(os.path.join(EXPORT_PATH, 'list.txt'), 'w') as f:
        f.writelines(['%s\n' % sheet_id_to_path(x) for x in all_xmls])


if __name__ == '__main__':
    main()
