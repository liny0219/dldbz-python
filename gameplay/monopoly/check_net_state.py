from __future__ import annotations
from typing import TYPE_CHECKING

from engine.u2_device import u2_device
from engine.world import world
from gameplay.monopoly.config import config
from gameplay.monopoly.constants import State

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_net_state(monopoly: Monopoly):
    if monopoly.state == State.NetError:
        return
    if monopoly.state and monopoly.state != State.Unknow:
        return
    if monopoly.screenshot is None:
        monopoly.shot()
    if world.check_net_state(monopoly.screenshot):
        if config.cfg_net_retry == 1:
            btn_retry()
        else:
            btn_back_menu()


def btn_back_menu():
    u2_device.device.click(380, 309)


def btn_retry():
    u2_device.device.click(576, 310)
