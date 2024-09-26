from __future__ import annotations
from typing import TYPE_CHECKING

from app_data import app_data
from engine.battle_pix import battle_pix
from engine.world import world
from gameplay.monopoly.check_bp_number import check_bp_number
from gameplay.monopoly.check_crossing import check_crossing, turn_auto_crossing
from gameplay.monopoly.check_map_accept_confirm import check_accept_confirm
from gameplay.monopoly.check_map_confirm import check_map_confirm
from gameplay.monopoly.check_map_distance import check_map_distance
from gameplay.monopoly.check_map_can_roll_dice import check_map_can_roll_dice
from gameplay.monopoly.check_map_end import check_map_end
from gameplay.monopoly.check_map_event import check_map_event
from gameplay.monopoly.check_map_final_confirm import btn_final_confirm, check_map_final_confirm
from gameplay.monopoly.check_map_info_confirm import check_map_info_confirm
from gameplay.monopoly.check_roll_rule import check_roll_rule
from gameplay.monopoly.config import config
from gameplay.monopoly.constants import State
from gameplay.monopoly.ocr import is_number
from gameplay.monopoly.roll_dice import roll_dice
from gameplay.monopoly.settle import report_end, report_finish

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_in_monopoly_map(monopoly: Monopoly):
    new_state = None
    if check_map_can_roll_dice(monopoly):
        monopoly.shot()
        new_state = State.MonopolyMap
        input_bp = 0
        rule_text = ""
        if config.cfg_check_roll_rule == 1:
            number = check_map_distance(monopoly)
            if is_number(number):
                input_bp = check_roll_rule(number)
                rule_text = f"期望: {input_bp},"
            max_bp = check_bp_number(monopoly.screenshot)
            app_data.update_ui(f"距离终点 {number}，当前BP: {max_bp}, {rule_text} 模式: {config.cfg_bp_type}")
            if config.cfg_bp_type == "max":
                if input_bp > max_bp:
                    input_bp = max_bp
            else:
                if input_bp == max_bp:
                    input_bp = max_bp
                else:
                    input_bp = 0
        monopoly.roll_time += 1
        roll_dice(input_bp, monopoly.roll_time)

    if not new_state and world.check_stage(monopoly.screenshot):
        new_state = State.MonopolyMap
        battle_pix.cmd_skip()

    if not new_state and check_map_event(monopoly):
        new_state = State.MonopolyMap

    if not new_state and check_map_confirm(monopoly):
        new_state = State.MonopolyMap

    if not new_state and check_accept_confirm(monopoly):
        new_state = State.MonopolyMap

    if not new_state and check_map_info_confirm(monopoly):
        new_state = State.MonopolyMap

    if not new_state and check_map_end(monopoly):
        report_end(monopoly)

    if not new_state and check_map_final_confirm(monopoly):
        btn_final_confirm()
        report_finish(monopoly)
        new_state = State.Finised

    if not new_state:
        crossing_index = check_crossing(monopoly)
        if crossing_index != -1:
            new_state = State.MonopolyMap
            turn_auto_crossing(monopoly, crossing_index)
            monopoly.pre_crossing = crossing_index
    return new_state
