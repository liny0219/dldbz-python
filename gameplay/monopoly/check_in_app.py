from __future__ import annotations
import time
from app_data import app_data
from engine.engine import engine
from typing import TYPE_CHECKING
from gameplay.monopoly.constants import State
if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_in_app(monopoly: Monopoly):
    monopoly.is_in_app = engine.check_in_app()
    if not monopoly.is_in_app:
        app_data.update_ui("未检查到游戏")
        engine.start_app()
        app_data.update_ui("启动游戏")
        monopoly.reset_round()
        monopoly.restart += 1
        monopoly.state = State.Unknow
        time.sleep(3)
        return True
    return False
