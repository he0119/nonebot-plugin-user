from enum import IntEnum


class SessionLevel(IntEnum):
    LEVEL0 = 0
    LEVEL1 = 1
    LEVEL2 = 2
    LEVEL3 = 3
    NONE = 0
    PRIVATE = 1
    GROUP = 2
    CHANNEL = 3


class SessionIdType(IntEnum):
    TYPE0 = 0
    TYPE1 = 1
    TYPE2 = 2
    TYPE3 = 3
    TYPE4 = 4
    TYPE5 = 5
    TYPE6 = 6
    TYPE7 = 7
    GLOBAL = 0
    USER = 1
    GROUP = 6
    GROUP_USER = 7
