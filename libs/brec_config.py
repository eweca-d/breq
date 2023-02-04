from typing import List
import json


class BRecConfig:
    def __init__(self):
        self.version = 3

    @staticmethod
    def value_dict(value: int | str | None):
        if value is None:
            return {'HasValue': True}
        else:
            return {'HasValue': True, 'Value': value}

    def to_monitor_json(self, room_list: List[int], port: int) -> str:
        d = {
            'version': self.version,
            'global': {
                'WebHookUrlsV2': self.value_dict('http://localhost:{}'.format(port))
            },
            'rooms': []
        }

        for room in room_list:
            d['rooms'].append({
                'RoomId': self.value_dict(room),
                'AutoRecord': self.value_dict(None),
            })

        return json.dumps(d)

    def to_record_json(self, room_id: int) -> str:
        d = {
            'version': self.version,
            'global': dict(),
            'rooms': [
                {
                    'RoomId': self.value_dict(room_id),
                    'AutoRecord': self.value_dict(True),
                }
            ]
        }

        return json.dumps(d)


if __name__ == '__main__':
    print(BRecConfig().to_monitor_json([1, 2, 3], 8048))
    print(BRecConfig().to_record_json(1))
