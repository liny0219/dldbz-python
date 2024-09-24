
from __future__ import annotations
from engine.comparator import comparator
from engine.engine import engine
from app_data import app_data
from gameplay.monopoly.config import config
from gameplay.monopoly.constants import State
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def btn_not_continue():
    engine.device.click(362, 362)


def btn_continue():
    engine.device.click(536, 362)


def on_continue():
    if config.cfg_isContinue == 0:
        btn_not_continue()
    else:
        btn_continue()


def check_in_continue(monopoly: Monopoly):
    app_data.update_ui("check-是否继续游戏", 'debug')
    coord = comparator.template_compare(f"./assets/monopoly/monopoly_continue.png", screenshot=monopoly.screenshot)
    if coord:
        app_data.update_ui("find-继续游戏")
        return State.Continue
    return False
