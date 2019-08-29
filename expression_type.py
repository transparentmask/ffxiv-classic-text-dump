#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from enum import Enum, unique


@unique
class PlayerParameter(Enum):
    Player_Gender_Female = 0x04
    EorzeaHour = 0x0B
    Player_SayColor = 0x0D
    Player_ShoutColor = 0x0E
    Player_TellColor = 0x0F
    Player_PartyColor = 0x10
    Player_LinkShell1 = 0x11
    Player_LinkShell2 = 0x12
    Player_LinkShell3 = 0x13
    Player_LinkShell4 = 0x14
    Player_LinkShell5 = 0x15
    Player_LinkShell6 = 0x16
    Player_LinkShell7 = 0x17
    Player_LinkShell8 = 0x18
    # Job = 0x44
    Player_GainLimit = 0x33
    Player_Maelstrom_Rank = 0x34
    Player_TwinAdders_Rank = 0x35
    Player_Immortal_Rank = 0x36

    @staticmethod
    def try_to_string(player_var):
        try:
            enum_var = PlayerParameter(player_var)
            return '〖%s〗' % enum_var.name
        except ValueError:
            return 'player_var(' + str(player_var) + ')'


@unique
class ObjectParameter(Enum):
    SelfName = 0x01
    Name1 = 0x02
    Name2 = 0x03
    ChocoboName = 0x37

    @staticmethod
    def try_to_string(obj_var):
        try:
            enum_var = ObjectParameter(obj_var)
            return '〖%s〗' % enum_var.name
        except ValueError:
            return 'obj_var(' + str(obj_var) + ')'


@unique
class ExpressionType(Enum):
    GreaterThanOrEqualTo = 0xE0  # Followed by two variables
    GreaterThan = 0xE1  # Followed by one variable
    LessThanOrEqualTo = 0xE2  # Followed by two variables
    LessThan = 0xE3  # Followed by one variable
    Equal = 0xE4  # Followed by two variables
    NotEqual = 0xE5  # TODO: Probably

    # TODO: I /think/ I got these right.
    IntegerParameter = 0xE8  # Followed by one variable
    PlayerParameter = 0xE9  # Followed by one variable
    StringParameter = 0xEA  # Followed by one variable
    ObjectParameter = 0xEB  # Followed by one variable

    Byte = 0xF0
    Int16_MinusOne = 0xF1  # Followed by a Int16 that is one too high
    Int16_1 = 0xF2  # Followed by a Int16
    Int16_2 = 0xF4  # Followed by a Int16
    Int24_MinusOne = 0xF5  # Followed by a Int24 that is one too high
    Int24 = 0xF6  # Followed by a Int24

    Int24_SafeZero = 0xFA  # Followed by a Int24, but 0xFF bytes set to 0 instead.
    Int24_Lsh8 = 0xFD  # Followed by a Int24, and left-shifted by 8 bits
    Int32 = 0xFE  # Followed by a Int32

    Decode = 0xFF  # Followed by length (inlcuding length) and data

    @staticmethod
    def is_compare_type(exp_type):
        return exp_type in [ExpressionType.GreaterThanOrEqualTo,
                            ExpressionType.GreaterThan,
                            ExpressionType.LessThanOrEqualTo,
                            ExpressionType.LessThan,
                            ExpressionType.Equal,
                            ExpressionType.NotEqual]

    @staticmethod
    def is_value_type(exp_type):
        return exp_type in [ExpressionType.IntegerParameter,
                            ExpressionType.PlayerParameter,
                            ExpressionType.StringParameter,
                            ExpressionType.ObjectParameter]

    @staticmethod
    def process_compare(exp_type, left, right):
        pass
