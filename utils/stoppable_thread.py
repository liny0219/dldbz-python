import threading


class StoppableThread(threading.Thread):
    def __init__(self, target=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self._target = target
        self.daemon = True

    def run(self):
        if self._target:
            self._target()

    def stop(self):
        print(f"Stopping thread {self.name}...")
        self._stop_event.set()

    def stopped(self):
        # print(f"Thread {self.name} is stopped {self._stop_event.is_set()}.")
        return self._stop_event.is_set()


