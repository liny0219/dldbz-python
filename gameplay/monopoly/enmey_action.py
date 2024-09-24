import os
from app_data import app_data
from engine.engine import engine
from engine.comparator import comparator
from gameplay.monopoly.config import config
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def enmey_action(monopoly: Monopoly):
    try:
        enemy = config.cfg_enemy_map.get(config.cfg_type)
        action = config.cfg_action_map.get(config.cfg_type)
        current_enemy = None

        if not enemy or not action:
            return

        for key, value in enemy.items():
            if not value:
                continue
            app_data.update_ui(f"开始匹配敌人{key}")
            try:
                normalized_path = os.path.normpath(value)
                result = comparator.template_compare(
                    normalized_path, [(15, 86), (506, 448)],
                    match_threshold=config.cfg_enemy_match_threshold,
                    screenshot=monopoly.screenshot, pack=False)
            except Exception as e:
                app_data.update_ui(f"匹配敌人{key}出现异常{e}")
                continue
            if result:
                current_enemy = key
                app_data.update_ui(f"匹配到敌人{current_enemy}")
                break
            else:
                app_data.update_ui(f"未匹配到敌人{key}")
        if not current_enemy:
            app_data.update_ui("未匹配到任何敌人")
            return

        current_action = action.get(current_enemy)
        if not current_action:
            app_data.update_ui(f"未找到敌人{current_enemy}的行动")
            return
        for value in current_action:
            if len(value) == 0:
                continue
            parts = value.split(',')
            command = parts[0]
            app_data.update_ui(f"执行命令{command}")
            if command == "Click":
                x = int(parts[1])
                y = int(parts[2])
                engine.device.click(x, y)

    except Exception as e:
        app_data.update_ui(f"处理敌人行动出现异常{e}")
