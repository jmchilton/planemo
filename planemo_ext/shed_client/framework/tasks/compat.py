from uuid import uuid4
from threading import Thread


def shared_task(callable):
    return Task(callable)


class Task(object):

    def __init__(self, callable):
        self._callable = callable

    def __call__(self, *args, **kwds):
        return self._callable(*args, **kwds)

    def apply_async(self, args=(), kwds={}, **options):
        thread = TaskThread(self._callable, args, kwds)
        result = Result(thread)
        thread.start()
        return result

    def delay(self, *args, **kwds):
        return self.apply_async(args, kwds)


class TaskThread(Thread):

    def __init__(self, callbable, args, kwds):
        self._callable = callable
        self._args = args
        self._kwds = kwds
        self.exception = None

    def run(self):
        try:
            result_value = self._callable(*self._args, **self._kwds)
        except Exception as e:
            self.exception = e
        self.result_value = result_value


class Result(object):

    def __init__(self, thread):
        self._thread = thread
        self.id = str(uuid4())

    def get(self, timeout=None):
        self._thread.join(timeout=timeout)
        return self._thread.result_value

    def ready(self):
        return self._thread.is_alive()

    def waiting(self):
        return not self.ready()

    def failed(self):
        return self._thread.exception is not None

    def maybe_reraise(self):
        e = self._thread.exception
        if e is not None:
            raise e

    def successful(self):
        return self.ready() and not self.failed()
