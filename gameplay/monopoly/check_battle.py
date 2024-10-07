
from __future__ import annotations
from app_data import app_data
from engine.battle_pix import battle
from gameplay.monopoly.config import config
from gameplay.monopoly.constants import State
from gameplay.monopoly.constants import State
from typing import TYPE_CHECKING

from gameplay.monopoly.enmey_action import enmey_action
if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_in_battle(monopoly: Monopoly):
    if battle.is_in_battle(monopoly.screenshot):
        return State.Battle


def check_in_battle_in_round(monopoly: Monopoly):
    state = monopoly.state
    if state == State.BattleInRound or state == State.BattleAutoStay:
        return
    if battle.is_in_round(monopoly.screenshot):
        if (monopoly.find_enemy):
            enmey_action(monopoly)
        if config.cfg_auto_battle == 1:
            app_data.update_ui(f"点击委托战斗", 'debug')
            battle.btn_auto_battle()
        else:
            battle.btn_attack()
        return State.BattleInRound


def check_in_battle_auto_stay(monopoly: Monopoly):
    if battle.is_auto_battle_stay(monopoly.screenshot):
        battle.btn_auto_battle_start()
        app_data.update_ui(f"点击开始委托战斗", 'debug')
        return State.BattleAutoStay
