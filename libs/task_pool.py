"""Task pool for running cli tasks in parallel."""

from typing import List, Optional
import multiprocessing as mp
from subprocess import Popen
import time


MAX_PRIORITY = 99999


class TaskPool:
    def __init__(self, num_workers: int):
        self.num_workers = num_workers
        self.working_rids = []
        self.task_pool = []

    def show_task_pool(self):
        tp = []
        for task in self.task_pool:
            if task is None:
                tp.append(None)
            else:
                tp.append(task[1])
        print('task pool:', tp)

    def find_rid(self, rid: int) -> Optional[int]:
        for idx, task in enumerate(self.task_pool):
            if (task is not None) and (task[1] == rid):
                return idx
        return None

    @staticmethod
    def std_cli_task(q: mp.Queue, cmd: List[str]):
        print('start task', cmd)
        p = Popen(cmd)
        while True:
            if q.get() == 'stop':
                p.kill()
                break
            time.sleep(0.1)

    def register_cli_task(self, cmd: List[str], rid: int, priority: int = MAX_PRIORITY):
        q = mp.Queue()
        p = mp.Process(target=self.std_cli_task, args=(q, cmd))
        self.task_pool.append((priority, rid, p, q, cmd))

        if len(self.working_rids) < self.num_workers:
            p.start()
            self.working_rids.append((priority, rid))
        elif priority != MAX_PRIORITY:
            self.working_rids.sort(key=lambda x: x[0])
            if priority < self.working_rids[-1][0]:
                self.stop_task(self.working_rids[-1][1], new_rid=rid, finished=False)

    def run_existing_task(self, rid: Optional[int]):
        if rid is not None:
            # 直接执行新任务
            task_id = self.find_rid(rid)
            if task_id is not None:
                task = self.task_pool[task_id]
                task[2].start()
                self.working_rids.append((task[0], task[1]))
                return

        # 若rid = None，或者rid对应的任务不存在，则从任务池中找一个优先级数值最小的任务执行
        # 在self.working_rids中寻找优先级数值最小的任务直接执行
        max_priority = MAX_PRIORITY + 1
        max_priority_task_idx = None
        for task_idx, task in enumerate(self.task_pool):
            if task is None:
                continue
            if task[0] < max_priority and task[1] not in [x[1] for x in self.working_rids]:
                max_priority = task[0]
                max_priority_task_idx = task_idx

        if max_priority_task_idx is not None:
            task = self.task_pool[max_priority_task_idx]
            task[2].start()
            self.working_rids.append((task[0], task[1]))

    def stop_task(self, rid: int, new_rid: int = None, finished: bool = True):
        """
        condition 0：停止的任务是正在执行的任务
        停止任务 -> 清除任务痕迹 -> 开启一个新的已有任务 -> 若finished = False，则将停止的任务重新加入任务池
        condition 1：停止的任务是未执行的任务
        停止任务 -> 清除任务痕迹 -> 若finished = False，则将停止的任务重新加入任务池
        """
        task_id = self.find_rid(rid)
        if task_id is None:
            return

        self.task_pool[task_id][3].put('stop')

        # record context
        st_priority, _, _, _, st_cmd = self.task_pool[task_id]

        self.task_pool[task_id] = None
        self.working_rids = list(filter(lambda x: x[1] != rid, self.working_rids))

        if rid in [x[1] for x in self.working_rids]:
            # start an existing task
            self.run_existing_task(new_rid)

        # place stop task at the end of the list
        if not finished:
            self.register_cli_task(st_cmd, rid, st_priority)


if __name__ == '__main__':
    tp = TaskPool(2)
    tp.register_cli_task(['timeout', '1000'], rid=0, priority=1)
    time.sleep(0.5)
    tp.show_task_pool()
    tp.register_cli_task(['timeout', '1000'], rid=1)
    time.sleep(0.5)
    tp.show_task_pool()
    tp.register_cli_task(['timeout', '1000'], rid=2, priority=0)
    time.sleep(2)
    print(tp.working_rids)
    tp.show_task_pool()
    tp.stop_task(1)
    time.sleep(2)
    print(tp.working_rids)
    tp.show_task_pool()
    tp.stop_task(0)
    time.sleep(2)
    print(tp.working_rids)
    tp.show_task_pool()
    tp.stop_task(2)
    time.sleep(2)
    print(tp.working_rids)
    tp.show_task_pool()
    tp.stop_task(1)
    time.sleep(2)
    print(tp.working_rids)
    tp.show_task_pool()
