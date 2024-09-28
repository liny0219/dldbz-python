
from enum import Enum


class State(Enum):
    Unknow = 0,
    World = 1,
    Title = 2,
    Continue = 3,
    Battle = 7,
    BattleInRound = 8,
    BattleAutoStay = 9,
    NetError = 10,
    NotApp = 11,
