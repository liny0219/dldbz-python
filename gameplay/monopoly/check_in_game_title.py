from __future__ import annotations
from typing import TYPE_CHECKING

from engine.world import world
from gameplay.monopoly.action import btn_center_confirm
from gameplay.monopoly.constants import State

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_in_game_title(monopoly: Monopoly):
    if monopoly.state == State.Title:
        return
    if monopoly.state and monopoly.state != State.Unknow:
        return
    if world.check_game_title(monopoly.screenshot):
        btn_center_confirm()
        return State.Title
