
from enum import Enum


class State(Enum):
    Finised = -1,
    Unknow = 0,
    World = 1,
    Title = 2,
    Continue = 3,
    MonopolyPage = 4,
    MonopolySetting = 5,
    MonopolyMap = 6,
    Battle = 7,
    BattleInRound = 8,
    BattleAutoStay = 9
