import time
from engine_vee.world import world_vee
from engine_vee.engine import engine_vee
from global_data import GlobalData


class Monopoly():
    def __init__(self, global_data: GlobalData):
        self.thread = global_data.thread
        self.update_ui = global_data.update_ui

    def start(self):
        looptime = 0
        engine_vee.check_in_app()  # 检查是否在游戏中，不在则启动游戏
        # 检查是否进入了游戏的世界，可以定义 in_world 函数来检查特定的界面元素是否存在
        while not world_vee.in_world() and looptime < 100:
            if (self.thread.stopped()):
                return
            # 可能的界面操作，确保界面响应
            engine_vee.device.click(362, 362)  # 大富翁选择不继续
            looptime += 1
            time.sleep(1)  # 等待一秒钟
        if looptime == 100:
            engine_vee.restart_game()  # 重新启动游戏的函数需要定义
        self.update_ui("进入游戏")
