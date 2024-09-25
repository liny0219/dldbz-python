from __future__ import annotations
from typing import Callable
from utils.singleton import singleton
from utils.stoppable_thread import StoppableThread


@singleton
class AppData:
    def __init__(self):
        self.thread: StoppableThread = None
        self.update_ui: Callable[[str, str], None] = None

    def thread_stoped(self) -> bool:
        return self.thread and self.thread.stopped()


app_data = AppData()
