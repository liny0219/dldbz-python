from __future__ import annotations
from typing import Callable
from engine.battle_vee import Battle
from utils.singleton import singleton
from utils.stoppable_thread import StoppableThread
from engine.comparator import Comparator
from engine.device_controller import DeviceController


@singleton
class GlobalData:
    def __init__(self, controller: DeviceController = None, comparator: Comparator = None, update_ui: Callable[[str], None] = None, thread: StoppableThread = None):
        self.thread = thread
        self.controller = controller
        self.comparator = comparator
        self.update_ui = update_ui
        self.battle = Battle(self)

    def thread_stoped(self) -> bool:
        return self.thread and self.thread.stopped()
