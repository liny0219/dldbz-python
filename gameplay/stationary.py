from __future__ import annotations
import time
from app_data import AppData
from engine.world import world
from engine.battle_pix import battle_pix
from engine.engine import engine
from utils.config_loader import cfg_recollection
from engine.comparator import comparator


class Stationary:
    def __init__(self, app_data: AppData):
        self.loop = int(cfg_recollection.get("common.loop"))
        self.app_data = app_data
        self.Timestartup = time.time()  # 程序启动时间
        self.TimeroundStart = time.time()  # 每轮开始时间

    def thread_stoped(self) -> bool:
        return self.app_data and self.app_data.thread_stoped()

    def update_ui(self, msg: str, type='info'):
        self.app_data and self.app_data.update_ui(msg, type)

    def start(self):
        self.loopNum = 0
        self.run()

    def run(self):
        try:
            retry_count = 0
            is_match = None
            is_pre_match = None
            is_in_world = False
            turn_direction = 1
            while not self.thread_stoped():
                is_pre_match = is_match
                is_match = None
                time.sleep(0.1)
                self.screenshot = engine.device.screenshot(format='opencv')
                is_in_app = True
                if not is_pre_match:
                    is_in_app = engine.check_in_app()
                if not is_in_app:
                    is_match = 'check_not_app'
                    self.update_ui("未检查到游戏")
                    engine.start_app()
                    continue

                is_in_world = world.check_in_world(self.screenshot)
                if is_in_world:
                    is_match = 'is_in_world'
                    self.update_ui("已进入大地图")
                    if turn_direction == 1:
                        world.run_right()
                        turn_direction = 0
                    else:
                        world.run_left()
                        turn_direction = 1
                    continue

                in_battle = battle_pix.is_in_battle(self.screenshot)
                if in_battle:
                    is_match = 'is_in_battle'
                    if battle_pix.is_in_round():
                        is_match = 'is_in_round'
                        battle_pix.btn_auto_battle()
                    elif battle_pix.is_auto_battle_stay():
                        is_match = 'is_auto_battle_stay'
                        battle_pix.btn_auto_battle_start()
                else:
                    world.btn_trim_click()

                if not is_match:
                    retry_count += 1

                if retry_count > 100:
                    self.update_ui("未检测到任何界面")
                    is_match = f'not match {retry_count}'
                    self.update_ui(f"检查{retry_count}次{0.2}秒未匹配到任何执行函数，重启游戏")
                    engine.restart_game()
                continue
        except Exception as e:
            self.update_ui(f"发生错误: {e}")
