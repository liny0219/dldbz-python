from __future__ import annotations
from typing import Callable
from utils.singleton import singleton
from utils.stoppable_thread import StoppableThread


@singleton
class app_data:
    def __init__(self, update_ui: Callable[[str, str], None] = None, thread: StoppableThread = None):
        self.thread = thread
        self.update_ui = update_ui

    def thread_stoped(self) -> bool:
        return self.thread and self.thread.stopped()

    def set(self, update_ui: Callable[[str, str], None] = None, thread: StoppableThread = None):
        self.thread = thread
        self.update_ui = update_ui
