#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import codecs
import json


class Specials:
    SPECIAL_INFOS = []

    def __init__(self, _bytearray):
        self.bytearray = _bytearray

    @classmethod
    def init_infos(cls, special_file="specials.json"):
        if len(Specials.SPECIAL_INFOS) > 0:
            return

        with codecs.open('specials.json', 'r', 'utf-8') as f:
            sp = json.load(f)
            for info in sp:
                info['func'] = eval('%s.do_%s' % (cls.__name__, info['action']))
                if not callable(info['func']):
                    continue

                i = int(info['key'], 16)
                bits = []
                for b in range(int(len(info['key']) / 2)):
                    bits.append((i >> (b * 8)) & 0xFF)
                info['key'] = bytearray(reversed(bits))
                info['values'] = [bytearray(v, 'utf-8') for v in info['values']]
                Specials.SPECIAL_INFOS.append(info)

    @classmethod
    def process(cls, _bytearray):
        cls.init_infos()
        instance = cls(_bytearray)
        return instance.do_process()

    def do_process(self):
        for info in Specials.SPECIAL_INFOS:
            info['func'](self, info)

        return self.bytearray

    def do_replace(self, special_info):
        for v in special_info['values']:
            self.bytearray = self.bytearray.replace(special_info['key'], v)


if __name__ == '__main__':
    string = Specials.process(b'\xe3\x83\x87\xe3\x83\x95\xe3\x82\xa9\xe3\x83\xab\xe3\x83\x88\xe3\x83\x88\xe3\x83\xbc\xe3\x82\xaf')
    print(string)
