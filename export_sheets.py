#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from lxml.etree import fromstring
from data_utils import *
from data_types import *
from specials import ALL_REF_SHEETS


EXPORT_PATH = 'sheets_new'
EXPORT_BIN = False
BASE_SHEET_ID = 16973824
FIRST_SHEETS = [
    'xtx/text_attrName', 'xtx/command', 'xtx/itemKind', 'xtx/text_equipPtName','xtx/displayName', 'xtx/placeName',
    'xtx/itemName', 'itemData', 'xtx/journalxtxSea', 'xtx/journalxtxFst', 'xtx/journalxtxWil', 'xtx/journalxtxRoc',
    'xtx/text_jobName', 'xtx/text_skillName', 'xtx/quest', 'xtx/achievement', 'xtx/facility', 'gcRank', 'xtx/gcRank',
    'xtx/guildleve', 'xtx/attributive'
]

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

    doc = fromstring(xml)
    ordered_sheets = list(FIRST_SHEETS)
    for sheet_line in doc.iterfind('sheet'):
        if sheet_line.get('name') in ordered_sheets:
            ordered_sheets[ordered_sheets.index(sheet_line.get('name'))] = sheet_line
            pass
        else:
            ordered_sheets.append(sheet_line)

    for sheet_line in ordered_sheets:
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
            return_dict = {} if sheet_line.get('name') in FIRST_SHEETS else None
            for sheet in sheet_doc.iterfind('sheet'):
                sheet_info = SheetInfo(sheet)
                # if sheet_info.lang and sheet_info.lang not in ['chs', 'ja', 'en']:
                #     continue
                export_sheet(sheet_info, EXPORT_PATH, EXPORT_BIN, return_dict)

            if return_dict is not None:
                ALL_REF_SHEETS[sheet_line.get('name')] = return_dict

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
