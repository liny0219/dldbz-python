
from __future__ import annotations
from engine.comparator import comparator
from engine.u2_device import u2_device
from app_data import app_data
from gameplay.monopoly.config import config
from gameplay.monopoly.constants import State
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def btn_not_continue():
    u2_device.device.click(362, 362)


def btn_continue():
    u2_device.device.click(536, 362)


def on_continue():
    if config.cfg_isContinue == 0:
        btn_not_continue()
        app_data.update_ui("点击-不继续游戏")
    else:
        btn_continue()
        app_data.update_ui("点击-继续游戏")


def check_in_continue(monopoly: Monopoly):
    app_data.update_ui("check-是否继续游戏弹窗", 'debug')
    coord = comparator.template_compare(f"./assets/monopoly/monopoly_continue.png", screenshot=monopoly.screenshot)
    if coord:
        app_data.update_ui("find-是否继续游戏弹窗")
        return State.Continue
    return False
