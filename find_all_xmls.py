#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import os

BASE_DATA_PATH = '../data'
EXPORT_PATH = 'sheets'
MAIN_LIST = os.path.join(EXPORT_PATH, 'list.txt')


def main():
    with open(MAIN_LIST, 'r') as f:
        main_list = f.readlines()
    main_list = [x.strip() for x in main_list]

    list_dirs = os.walk(BASE_DATA_PATH)
    for root, dirs, files in list_dirs:
        for file in files:
            path = os.path.join(root, file)
            if path in main_list:
                continue
            with open(path, 'rb') as f:
                contents = f.read()
                if len(contents) > 0 and (contents[-1] == '\xF1' or contents[-1] == '>'):
                    print(path.replace(BASE_DATA_PATH + '/', ''))


if __name__ == '__main__':
    main()
