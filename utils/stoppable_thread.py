import threading
import time
from typing import Any, Callable, Optional


class StoppableThread(threading.Thread):
    def __init__(self,
                 target: Optional[Callable] = None,
                 name: Optional[str] = None,
                 args: tuple = (),
                 kwargs: dict = None
                 ) -> None:

        if kwargs is None:
            kwargs = {}

        super().__init__(name=name)
        self._stop_event = threading.Event()
        self._target = target
        self._args = args
        self._kwargs = kwargs
        self.daemon = True
        self._running = False
        self._exception = None

    def run(self) -> None:
        self._running = True
        try:
            if self._target:
                self._target(*self._args, **self._kwargs)
        except Exception as e:
            self._exception = e
            raise
        finally:
            self._running = False
            del self._target, self._args, self._kwargs

    def stop(self) -> None:
        print(f"Stopping thread {self.name}...")
        self._stop_event.set()

    def stopped(self) -> bool:
        return self._stop_event.is_set()

    def is_running(self) -> bool:
        return self._running and self.is_alive()

    def get_exception(self) -> Optional[Exception]:
        return self._exception
