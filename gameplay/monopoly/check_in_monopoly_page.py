from __future__ import annotations
from typing import TYPE_CHECKING

from gameplay.monopoly.action import btn_setting_monopoly
from gameplay.monopoly.check_in_select_monopoly import check_in_select_monopoly
from gameplay.monopoly.constants import State
from gameplay.monopoly.select_monopoly import select_monopoly

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_in_monopoly_page(monopoly: Monopoly):
    if monopoly.state == State.MonopolyPage:
        return
    if not monopoly.state or monopoly.state == State.Unknow or monopoly.state == State.Finised:
        if check_in_select_monopoly(monopoly):
            select_monopoly(monopoly)
            btn_setting_monopoly()
            return State.MonopolyPage
