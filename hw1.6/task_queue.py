from datetime import datetime, timedelta
from collections import deque
import hashlib

from typing import Tuple


class Task:
    def __init__(self, length: int, data: str):
        self.data = data
        self.length = length
        self.is_free = True
        self.execution_time: datetime

    def take_on(self):
        self.is_free = False
        self.execution_time = datetime.now()

    def is_overdue(self, timed: int) -> bool:
        return datetime.now() - timedelta(seconds=timed) > self.execution_time


class TaskQueue:
    def __init__(self):
        self.queue_idx = deque()
        self.task_dict = dict()

    @staticmethod
    def get_md5(length: int, data: str):
        m = hashlib.md5()
        m.update(str(length).encode())
        m.update(data.encode())
        m.update(str(datetime.now()).encode())
        return m.hexdigest()

    def add(self, length: int, data: str) -> str:
        idx = self.get_md5(length, data)
        task = Task(length, data)
        self.task_dict[idx] = task
        self.queue_idx.append(idx)
        return idx

    def get(self, timed) -> Tuple[str, Task]:
        for task_idx in self.queue_idx:
            task = self.task_dict[task_idx]
            if task.is_free or task.is_overdue(timed):
                task.take_on()
                return task_idx, task
        raise ValueError

    def ack(self, idx: str) -> None:
        if idx in self.queue_idx:
            self.queue_idx.remove(idx)
            self.task_dict.pop(idx)
        else:
            raise KeyError

    def check_in(self, idx: str) -> bool:
        return idx in self.task_dict
