from __future__ import annotations
from engine.battle_vee import Battle
from utils.singleton import singleton
from utils.stoppable_thread import StoppableThread
from engine.comparator import Comparator
from engine.device_controller import DeviceController


@singleton
class GlobalData:
    def __init__(self, controller: DeviceController = None, comparator: Comparator = None, updateUI=None, thread: StoppableThread = None):
        self.thread = thread
        self.controller = controller
        self.comparator = comparator
        self.updateUI = updateUI
        self.battle = Battle(self)
