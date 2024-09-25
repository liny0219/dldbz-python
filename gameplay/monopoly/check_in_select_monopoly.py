from __future__ import annotations
from typing import TYPE_CHECKING

from app_data import app_data
from engine.comparator import comparator

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_in_select_monopoly(monopoly: Monopoly):
    if (app_data.thread_stoped()):
        return False
    app_data.update_ui("check-大富翁选择界面中", 'debug')
    if comparator.template_compare(f"./assets/monopoly/page_monopoly.png", screenshot=monopoly.screenshot):
        app_data.update_ui("find-在大富翁选择界面中", 'debug')
        return True
    return False
