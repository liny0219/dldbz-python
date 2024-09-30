from enum import Enum


class App_Client(Enum):
    NTES = 'com.netease.ma167'
    Bilibili = 'com.netease.ma167.bilibili'


class MATCH_CONFIDENCE(Enum):
    HIGH = 0,
    MID = 1,
    LOW = 2,
    VERY_LOW = 3


class BUTTON_STATUS(Enum):
    UNKNOWN = 0
    ACTIVE = 1
    DISABLE = 2
    NOT_EXIST = 3


class ROLE_HP_STATUS(Enum):
    DEAD = 0
    LOW = 1
    MID = 2
    HIGH = 3


class ROLE_MP_STATUS(Enum):
    LOW = 0
    HIGH = 1
