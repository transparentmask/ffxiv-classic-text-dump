#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import traceback
from io import BytesIO

from expression_type import ExpressionType, PlayerParameter, ObjectParameter
from integer_type import IntegerType
from tag_type import TagType

SPECIAL_START = b'\x02'  # 0x02
SPECIAL_END = b'\x03'  # 0x03

ALL_REF_SHEETS = {}


class Specials:
    funcs = {}

    def __init__(self, _bytes=None, _buf=None, length=0):
        if _bytes is not None:
            self.buf = BytesIO()
            self.buf.write(_bytes)
            self.buf.seek(0)
            self.length = length if length else len(_bytes)
        elif _buf:
            self.buf = _buf
            self.length = length
        self.result = ""

        if not self.funcs:
            for name, member in TagType.__members__.items():
                formatted = ''.join([s if s.isalpha() and s.islower() else '_' + s.lower() for s in name]).lstrip('_')
                if formatted[-2] == '_' and formatted[-3].isdecimal():
                    tmp = formatted[-1]
                    formatted = formatted[:-2] + tmp
                self.funcs[member] = getattr(self, 'process_type_' + formatted, None)

    @classmethod
    def process(cls, _bytes=None, _buf=None, length=0):
        instance = cls(_bytes, _buf, length)
        return instance.do_process()

    def do_process(self):
        end = self.buf.tell() + self.length
        static_bytes = bytearray()
        while self.buf.tell() < end:
            _byte = self.buf.read(1)
            if _byte == SPECIAL_START:
                tag = ord(self.buf.read(1))
                try:
                    tag_type = TagType(tag)
                except ValueError:
                    print('0x%.2x is not a valid TagType' % tag)
                    break
                if static_bytes:
                    self.result += str(static_bytes, 'utf8')
                    static_bytes = bytearray()
                length = IntegerType.get_value(self.buf)
                # start = self.buf.tell()
                if tag_type in self.funcs and self.funcs[tag_type] is not None:
                    self.result += self.funcs[tag_type](self.buf, tag_type, length)
                else:
                    print(tag_type)
                    print('TagType 0x%.2X not processed!!' % tag)
                    print('length: %d' % length)

                    pos = self.buf.tell()
                    left = pos - 10 if pos > 10 else 0
                    before = pos - left
                    self.buf.seek(left)
                    print('%s [%.2X] %s' % (' '.join(map(lambda b: '%.2X' % b, self.buf.read(before))),
                                            ord(self.buf.read(1)),
                                            ' '.join(map(lambda b: '%.2X' % b, self.buf.read(length + 0x20)))))
                    exit(0)
                if self.buf.read(1) != SPECIAL_END:
                    self.buf.seek(self.buf.tell()-1)
                    print(self.buf.read(1))
                    print('tag 0x%.2x not finish correctly' % tag)
                    # size = self.buf.tell() - start
                    # self.buf.seek(self.buf.tell() - 17 if self.buf.tell() - 17 > 0 else 0)
                    # _bytes = self.buf.read(length + 0x20)
                    # print(' '.join(map(lambda b: '%.2X' % b, _bytes)))
                    #
                    # print('-----------------------')
                    #
                    # self.buf.seek(start - 5 if start - 5 > 0 else 0)
                    # print(' '.join(map(lambda b: '%.2X' % b, self.buf.read(size + 0x20))))
                    #
                    # self.buf.seek(start)
                    # self.funcs[tag_type](self.buf, tag_type, length)
                    # exit(0)
            else:
                static_bytes += _byte

        if static_bytes:
            self.result += str(static_bytes, 'utf8')

        return self.result

    def process_expression_for_str(self, _buf, length=0, type_value=None, tag_type=None):
        value = self.process_expression(_buf, length, type_value, tag_type)
        if isinstance(value, bytearray) or isinstance(value, bytes):
            return repr(str(value, 'utf8'))
        # if isinstance(value, str):
        #     return repr(value)
        return str(value)

    def process_expression(self, _buf, length=0, type_value=None, tag_type=None):
        if not type_value:
            type_value = ord(_buf.read(1))
        if isinstance(type_value, ExpressionType):
            type_value = type_value.value
        if type_value < 0xD0:
            return type_value - 1
        if type_value < 0xE0:
            # topLevel?
            return type_value - 1

        try:
            exp_type = ExpressionType(type_value)
        except ValueError:
            if not tag_type.name.startswith('Unknown'):
                print('0x%.2x is not a valid ExpressionType' % type_value)
            _buf.seek(_buf.tell() - 1)
            tmp = _buf.read(length)
            return tmp.hex()

        if ExpressionType.is_compare_type(exp_type):
            left = self.process_expression_for_str(_buf)
            right = self.process_expression_for_str(_buf)
            return exp_type, left, right
        elif exp_type == ExpressionType.Byte:
            return IntegerType.get_value(_buf, IntegerType.Byte)
        elif exp_type == ExpressionType.Int16_MinusOne:
            int_type = IntegerType.Byte if 0 < length < 2 else IntegerType.Int16
            return IntegerType.get_value(_buf, int_type) - 1
        elif exp_type == ExpressionType.Int16_1 or exp_type == ExpressionType.Int16_2:
            return IntegerType.get_value(_buf, IntegerType.Int16)
        elif exp_type == ExpressionType.Int24_MinusOne:
            int_type = IntegerType.Int16 if 0 < length < 3 else IntegerType.Int24
            return IntegerType.get_value(_buf, int_type) - 1
        elif exp_type == ExpressionType.Int24:
            return IntegerType.get_value(_buf, IntegerType.Int24)
        elif exp_type == ExpressionType.Int24_Lsh8:
            return IntegerType.get_value(_buf, IntegerType.Int24) << 8
        elif exp_type == ExpressionType.Int24_SafeZero:
            v16 = ord(_buf.read(1))
            v8 = ord(_buf.read(1))
            v0 = ord(_buf.read(1))

            v = 0
            if v16 != 0xFF:
                v |= (v16 << 16)
            if v8 != 0xFF:
                v |= (v8 << 8)
            if v0 != 0xFF:
                v |= v0
            return v
        elif exp_type == ExpressionType.Int32:
            return IntegerType.get_value(_buf, IntegerType.Int32)
        elif exp_type == ExpressionType.IntegerParameter:
            return 'int_var(' + str(self.process_expression(_buf)) + ')'
        elif exp_type == ExpressionType.PlayerParameter:
            player_var = self.process_expression(_buf)
            return PlayerParameter.try_to_string(player_var)
        elif exp_type == ExpressionType.StringParameter:
            return 'str_var(' + str(self.process_expression(_buf)) + ')'
        elif exp_type == ExpressionType.ObjectParameter:
            obj_var = self.process_expression(_buf)
            return ObjectParameter.try_to_string(obj_var)
        elif exp_type == ExpressionType.Decode:
            exp_len = IntegerType.get_value(_buf)
            value = Specials.process(_buf=_buf, length=exp_len)
            return value
        else:
            # pos = _buf.tell()
            # left = pos - 10 if pos > 10 else 0
            # before = pos - left
            # _buf.seek(left)
            # print('%s [%.2X] %s' % (' '.join(map(lambda b: '%.2X' % b, _buf.read(before))), _buf.read(1), ' '.join(map(lambda b: '%.2X' % b, _buf.read(length + 0x20)))))

            print('ExpressionType 0x%.2X not processed!!' % type_value)
            exit(0)

    def process_type_value(self, _buf, tag, length):
        return str(self.process_expression(_buf, length - 1))

    def process_type_if(self, _buf, tag, length):
        start = _buf.tell()
        end = start + length
        try:
            result = self.process_expression(_buf, tag_type=tag)
            if isinstance(result, tuple):
                (exp_type, left, right) = result
                condition = '%s(%s, %s)' % (exp_type.name, str(left), str(right))
            else:
                condition = str(result)
        except Exception:
            traceback.print_exc()
            _buf.seek(start)
            print(_buf.read(1))
            _buf.seek(start-16 if start-16 > 0 else 0)
            _bytes = _buf.read(0x4D)
            print(' '.join(map(lambda b: '%.2X' % b, _bytes)))
            _buf.seek(start)
            (exp_type, left, right) = self.process_expression(_buf)
            exit(0)
        true_value = self.process_expression_for_str(_buf) if _buf.tell() < end else ''
        false_value = self.process_expression_for_str(_buf) if _buf.tell() < end else ''

        if _buf.tell() < end:
            falses = [false_value]
            while _buf.tell() < end:
                falses.append(self.process_expression_for_str(_buf))
            false_value = '[%s]' % ', '.join(falses)

        return '<If(%s)>%s<Else>%s</If>' % (condition, str(true_value), str(false_value))

    def process_type_switch(self, _buf, tag, length):
        end = _buf.tell() + length
        case_switch = self.process_expression(_buf)
        cases = []
        while _buf.tell() < end:
            case = self.process_expression_for_str(_buf)
            cases.append(str(case))
        if isinstance(case_switch, int):
            try:
                return cases[case_switch - 1]
            except Exception:
                pass
        elif isinstance(case_switch, str) and case_switch.startswith('【'):
            try:
                case_index = int(case_switch.strip('【】')) - 1
                return cases[case_index]
            except Exception:
                pass
        return '<Switch %s>%s</Switch>' % (case_switch, '; '.join(['%d: %s' % (i + 1, v) for i, v in enumerate(cases)]))

    def process_type_line_break(self, _buf, tag, length):
        if length:
            _buf.read(length)
        return '<LineBreak>'

    def process_type_sheet(self, _buf, tag, length):
        return self._process_type_generic_element_with_variable_arguments(_buf, tag, length, 2, 0xFF)

    def process_type_sheet_en(self, _buf, tag, length):
        return self._process_type_generic_element_with_variable_arguments(_buf, tag, length, 3, 0xFF)

    def process_type_sheet_de(self, _buf, tag, length):
        return self._process_type_generic_element_with_variable_arguments(_buf, tag, length, 3, 0xFF)

    def process_type_sheet_fr(self, _buf, tag, length):
        return self._process_type_generic_element_with_variable_arguments(_buf, tag, length, 3, 0xFF)

    def process_type_sheet_ja(self, _buf, tag, length):
        return self._process_type_generic_element_with_variable_arguments(_buf, tag, length, 3, 0xFF)

    def process_type_clickable(self, _buf, tag, length):
        return self._process_type_generic_element_with_variable_arguments(_buf, tag, length, 1, 0xFF)

    def _process_type_generic_element_with_variable_arguments(self, _buf, tag, length, min_paras, max_paras):
        end = _buf.tell() + length
        params = []
        while _buf.tell() < end and len(params) < max_paras:
            v = self.process_expression_for_str(_buf)
            params.append(v)

        if (min_paras == 2 and params[1].isdecimal()) or \
            (min_paras == 3 and params[2].isdecimal()):

            if min_paras == 2:
                try:
                    _dict = ALL_REF_SHEETS[params[0]]
                    _line = _dict[params[1]]
                    _value = _line[params[2]] if len(params) > 2 else _line
                    return '【%s】' % str(_value)
                except Exception:
                    pass
            else:
                pass

            params[0] = repr(params[0])

        return '%s(%s)' % (tag.name, ', '.join(params))

    def process_type_soft_hyphen(self, _buf, tag, length):
        if length:
            _buf.read(length)
        return ''

    def process_type_dash(self, _buf, tag, length):
        if length:
            _buf.read(length)
        return '-'

    def process_type_emphasis(self, _buf, tag, length):
        return self._process_type_generic_surrounding_tag(_buf, tag, length)

    def process_type_emphasis_2(self, _buf, tag, length):
        return self._process_type_generic_surrounding_tag(_buf, tag, length)

    def _process_type_generic_surrounding_tag(self, _buf, tag, length):
        if length != 1:
            print('%s wrong len' % tag.name)
            exit(0)
            return ''
        status = IntegerType.get_value(_buf)
        if status == 0:
            return '</%s>' % tag.name
        elif status == 1:
            return '<%s>' % tag.name
        print('%s wrong data' % tag.name)
        exit(0)
        return ''

    def process_type_color(self, _buf, tag, length):
        type_value = ord(_buf.read(1))
        if length == 1 and type_value == 0xEC:
            return '</%s>' % tag.name

        color = self.process_expression(_buf, type_value=type_value)
        if isinstance(color, str):
            return '<%s %s>' % (tag.name, color)
        return '<%s #%.2X%.2X%.2X%.2X>' % (tag.name, (color >> 16) & 0xFF, (color >> 8) & 0xFF, (color >> 0) & 0xFF, (color >> 24) & 0xFF)

    def process_type_color_2(self, _buf, tag, length):
        return self.process_type_color(_buf, tag, length)

    def process_type_indent(self, _buf, tag, length):
        if length:
            _buf.read(length)
        return '\t'
        # return bytes(b'\x09')  # 'TAB'

    def process_type_gui(self, _buf, tag, length):
        return self._process_type_generic_element(_buf, tag, length, 1, False)

    def process_type_highlight(self, _buf, tag, length):
        return self._process_type_generic_element(_buf, tag, length, 0, True)

    def process_type_time(self, _buf, tag, length):
        return self._process_type_generic_element(_buf, tag, length, 1, False)

    def process_type_time_2(self, _buf, tag, length):
        return self._process_type_generic_element(_buf, tag, length, 1, True)

    def process_type_two_digit_value(self, _buf, tag, length):
        return self._process_type_generic_element(_buf, tag, length, 0, True)

    def process_type_split(self, _buf, tag, length):
        (args, content) = self._process_type_generic_element(_buf, tag, length, 3, False, not_format=True)
        using_family = (args[-1] == 2 or args[-1] == '2')
        orginal_name = args[1].replace('\'', '')
        if orginal_name== '<Highlight>[SelfName]</Highlight>':
            return '[SelfName_FamilyName]' if using_family else '[SelfName_GivenName]'
        if orginal_name == '<Highlight>[Name1]</Highlight>':
            return '[Name1_FamilyName]' if using_family else '[Name1_GivenName]'
        if orginal_name == '<Highlight>[Name2]</Highlight>':
            return '[Name2_FamilyName]' if using_family else '[Name2_GivenName]'

        return '<Split(%s, %s)[%s]>' % (orginal_name, args[2], args[-1])
        # return self._process_type_generic_element_format(tag, args, content)

    def process_type_wait(self, _buf, tag, length):
        return self._process_type_generic_element(_buf, tag, length, 1, False)

    def _process_type_generic_element(self, _buf, tag, length, arg_count, has_content, not_format=False):
        if not length:
            return '<%s/>' % tag.name
        end = _buf.tell() + length
        args = [tag.name]
        for _ in range(arg_count):
            arg = self.process_expression_for_str(_buf, length=end-_buf.tell()-1)
            args.append(arg)

        content = self.process_expression_for_str(_buf) if has_content else None
        if not_format:
            return args, content
        return self._process_type_generic_element_format(tag, args, content)

    def _process_type_generic_element_format(self, tag, args, content):
        result = '<%s' % ' '.join(args)
        if content:
            result += '>%s</%s>' % (content, tag.name)
        else:
            result += '/>'
        return result

    def process_type_format(self, _buf, tag, length):
        end = _buf.tell() + length
        arg1 = self.process_expression_for_str(_buf)
        arg2 = _buf.read(end - _buf.tell()).hex()
        return 'Format(%s, %s)' % (arg1, arg2)

    def process_type_unknown_26(self, _buf, tag, length):
        end = _buf.tell() + length
        values = []
        while _buf.tell() < end:
            value = self.process_expression_for_str(_buf, length, tag_type=tag)
            values.append(value)
        return '<Unknown26>%s</Unknown26>' % (', '.join(values))

    def process_type_unknown_2d(self, _buf, tag, length):
        value = self.process_expression_for_str(_buf, length, tag_type=tag)
        return '<Unknown2D>%s</Unknown2D>' % value

    def process_type_unknown_2f(self, _buf, tag, length):
        value = self.process_expression_for_str(_buf, length, tag_type=tag)
        return '<Unknown2F>%s</Unknown2F>' % value

    def process_type_unknown_tmp(self, _buf, tag, length):
        start = _buf.tell()

        seek_len = _buf.tell() - 8
        add_len = 16
        if seek_len < 0:
            add_len -= seek_len
            seek_len = 0
        _buf.seek(seek_len)
        print(' '.join(map(lambda b: '%.2X' % b, _buf.read(length + add_len))))

        _buf.seek(start)
        arg = self.process_expression(_buf)

        return bytes()
