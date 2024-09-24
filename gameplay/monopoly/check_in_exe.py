from __future__ import annotations
import time
from app_data import app_data
from gameplay.monopoly.check_in_app import check_in_app
from gameplay.monopoly.config import exe_manager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_in_exe(monoploly: Monopoly):
    if exe_manager.exe_path is None or len(exe_manager.exe_path) == 0:
        return
    if exe_manager.is_exe_running():
        if monoploly.is_running == False:
            monoploly.is_running = True
            time.sleep(5)
            check_in_app(monoploly)
    else:
        monoploly.is_running = False
        app_data.update_ui("模拟器未运行,等待启动")
        time.sleep(2)
        exe_manager.start_exe()
