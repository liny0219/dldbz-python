from __future__ import annotations
from typing import TYPE_CHECKING

from app_data import app_data
from engine.comparator import comparator
from gameplay.monopoly.action import btn_play_monopoly
from gameplay.monopoly.constants import State
from gameplay.monopoly.select_game_mode import select_game_mode
from gameplay.monopoly.settle import report_finish

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_in_monopoly_setting(monopoly: Monopoly):
    if monopoly.state == State.MonopolySetting or monopoly.state == State.MonopolyMap:
        return
    if check_in_setting(monopoly):
        report_finish()
        app_data.update_ui(f"设置大富翁挑战设定")
        select_game_mode()
        app_data.update_ui(f"开始大富翁,当前第 {monopoly.started_count+1} 轮")
        btn_play_monopoly()
        monopoly.new_trun()
        return State.MonopolySetting


def check_in_setting(monopoly: Monopoly):
    if (app_data.thread_stoped()):
        return False
    app_data.update_ui("check-大富翁设置界面中", 'debug')
    if comparator.template_compare("./assets/monopoly/monopoly_setting.png", screenshot=monopoly.screenshot):
        app_data.update_ui("find-大富翁设置界面中", 'debug')
        return True
    return False
