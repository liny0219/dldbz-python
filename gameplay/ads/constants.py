
from enum import Enum


class State(Enum):
    Unknow = 0,
    World = 1,
    Title = 2,
    Continue = 3,
    AchievementMenu = 4,
    AchievementPage = 5,
    AdsModal = 6,
    AdsWatch = 7,
    AdsWatchEnd = 8,
    AdsPlaying = 9,
    AdsAwardConfirm = 10,
    AdsFinish = 11,
    AdsType1 = 12,
    NetError = 99,
    NotApp = 100,
