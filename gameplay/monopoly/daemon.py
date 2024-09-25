

from __future__ import annotations
from typing import TYPE_CHECKING
import time
from app_data import app_data
from gameplay.monopoly.check_idle_wait import check_idle_wait
from gameplay.monopoly.check_in_app import check_in_app
from gameplay.monopoly.check_net_state import check_net_state
if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def daemon(monopoly: Monopoly):
    try:
        while not app_data.thread_monopoly_deamon_stoped():
            try:
                app_data.update_ui('守护线程检查', 'debug')
                check_net_state(monopoly)
                check_idle_wait(monopoly)
                check_in_app(monopoly)
            except Exception as e:
                app_data.update_ui(f"守护线程循环异常{e}")
            time.sleep(10)
    except Exception as e:
        app_data.update_ui(f"守护线程异常停止{e}")
