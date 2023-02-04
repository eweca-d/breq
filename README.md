# BReQ

> Bililive Recorder Queue, a customized development of [BililiveRecorder](https://github.com/BililiveRecorder/BililiveRecorder).

BReQ，B站录播姬脚本。


## 使用方法

1. 安装[Python3](https://www.python.org/)
2. `git clone`本项目
3. 下载B站录播姬[CLI版本](https://github.com/BililiveRecorder/BililiveRecorder/releases)
4. 将录播姬CLI与本项目放入同一个文件夹中（建议创建`brec`文件夹放置录播姬CLI程序）
5. 修改`main.py`的参数：
    
    - `BREC_PATH`: 录播姬放置位置
    - `MONITOR_PORT`: WebHook端口，默认为`8048`，不行请尝试其他数值
    - `MAX_WORKERS`: 同时允许录播的数量
    - `ROOM_LIST`: 监测房间的ID列表（请注意，某些房间的rid不是真实房间ID，请使用真实房间ID，可见[seam](https://github.com/eweca-d/seam)或[real-url](https://github.com/wbt5/real-url/)）

6. `python main.py`


## Warning

本项目处于非常早期的开发阶段。


## 主要目标

提供带有优先级的B站录播功能[issue #453](https://github.com/BililiveRecorder/BililiveRecorder/issues/453)。避免过多房间同时开播后，带宽不足的问题。


## 已完成

1. 基于录播数量限制以及`List[RoomId]`排序的优先级录播功能。
    
    - 同时允许$N$个录播工作进行。
    - 当同时工作的数量$n < N$时，新的直播开始将直接录播。
    - 当同时工作的数量$n \geq\ N$时，在录播的房间中优先级最低的工作被搁置，新的直播间开始录播。
    - 当直播间关闭时，若有被搁置的录播工作，将挑选搁置中优先度最高的录播继续进行。
