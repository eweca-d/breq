from typing import List
import os
from subprocess import Popen
import multiprocessing as mp
import json
from libs.task_pool import TaskPool
from libs.web_hook_listener import set_listener
from libs.brec_config import BRecConfig


BREC_PATH = r'brec\BililiveRecorder.Cli.exe'
MONITOR_PORT = 8048
MAX_WORKERS = 2
ROOM_LIST = [
]


class BRecManager:
    def __init__(self):
        self.task_pool = TaskPool(MAX_WORKERS)
        self.room_list = ROOM_LIST
        self.room_monitor_process, self.room_monitor = self.monitor_rooms(ROOM_LIST, MONITOR_PORT)

    @staticmethod
    def monitor_rooms(room_list: List[int], port: int) -> tuple[Popen, mp.Queue]:
        if not os.path.exists('monitor'):
            os.mkdir('monitor')

        with open(os.path.join('monitor', 'config.json'), 'w') as f:
            f.write(BRecConfig().to_monitor_json(room_list, port))

        p = Popen([BREC_PATH, 'run', 'monitor'])
        web_hook_listener = set_listener(port)
        return p, web_hook_listener

    @staticmethod
    def prepare_record(room_id: int):
        room_id_str = str(room_id)
        if not os.path.exists(room_id_str):
            os.mkdir(room_id_str)
            with open(os.path.join(room_id_str, 'config.json'), 'w') as f:
                f.write(BRecConfig().to_record_json(room_id))

    def run(self):
        # prepare record folders
        for room_id in self.room_list:
            self.prepare_record(room_id)

        while True:
            web_hook_info = self.room_monitor.get()
            web_hook_info = web_hook_info.split('\r\n')[-1]
            web_hook_info = json.loads(web_hook_info)
            event_type = web_hook_info['EventType']
            room_id = web_hook_info['EventData']['RoomId']
            if event_type == 'StreamStarted':
                print('StreamStarted: {}'.format(room_id))
                self.task_pool.register_cli_task([BREC_PATH, 'run', str(room_id)], room_id,
                                                 priority=ROOM_LIST.index(room_id))
            elif event_type == 'StreamEnded':
                print('StreamEnded: {}'.format(room_id))
                self.task_pool.stop_task(room_id)


if __name__ == '__main__':
    BRecManager().run()
