
from __future__ import annotations
import time
from engine.engine import engine
from app_data import app_data
from gameplay.monopoly.config import config
from gameplay.monopoly.constants import State
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_idle_wait(monopoly: Monopoly):
    app_data.update_ui("check-检查空闲等待", 'debug')
    monopoly.wait_duration = time.time() - monopoly.wait_time
    if monopoly.wait_duration > config.cfg_wait_time:
        min = config.cfg_wait_time/60
        app_data.update_ui(f"{int(min)}分钟未匹配到任何执行函数，重启游戏")
        engine.restart_game()
        monopoly.restart += 1
        monopoly.state = State.Unknow
        monopoly.reset_round()
        time.sleep(3)
        return State.Unknow
