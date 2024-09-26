from __future__ import annotations
from typing import TYPE_CHECKING

from engine.world import world
from gameplay.monopoly.action import btn_menu_monopoly
from gameplay.monopoly.constants import State

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_in_world(monopoly: Monopoly):
    if monopoly.state == State.World:
        return
    if monopoly.state and monopoly.state != State.Unknow:
        return
    if world.check_in_world(monopoly.screenshot):
        btn_menu_monopoly()
        return State.World
