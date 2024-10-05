from __future__ import annotations
from typing import Callable
from utils.singleton import singleton
from utils.stoppable_thread import StoppableThread
import threading


@singleton
class AppData:
    def __init__(self):
        self.thread: StoppableThread = None
        self.monopoly_deamon_thread: StoppableThread = None
        self.recollection_deamon_thread: StoppableThread = None
        self.update_ui: Callable[[str, str], None] = None

    def thread_stoped(self) -> bool:
        thd = self.thread
        return thd and thd.stopped()

    def thread_monopoly_deamon_stoped(self) -> bool:
        current_thread_id = threading.get_ident()
        thd = self.monopoly_deamon_thread
        if thd and thd.ident != current_thread_id:
            return True
        return thd and thd.stopped()

    def thread_recollection_deamon_stoped(self) -> bool:
        current_thread_id = threading.get_ident()
        thd = self.recollection_deamon_thread
        if thd and thd.ident != current_thread_id:
            return True
        return thd and thd.stopped()


app_data = AppData()
