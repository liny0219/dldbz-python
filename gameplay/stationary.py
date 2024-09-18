from __future__ import annotations
import time
from app_data import AppData
from engine.world import world
from engine.battle_pix import battle_pix
from engine.engine import engine
from utils.config_loader import cfg_recollection


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
            pre_match = None
            in_battle = False
            turn_direction = 1
            while not self.thread_stoped():
                try:
                    pre_match = is_match
                    is_match = None
                    time.sleep(0.1)
                    self.screenshot = engine.device.screenshot(format='opencv')
                    if is_match != 'None':
                        self.update_ui(f"匹配到的函数 {is_match} ", "debug")
                        retry_count = 0
                    is_in_app = True

                    if not in_battle:
                        is_in_app = engine.check_in_app()
                    if not is_in_app:
                        is_match = 'check_not_app'
                        self.update_ui("未检查到游戏")
                        engine.start_app()
                        continue

                    is_game_title = False
                    if not in_battle:
                        is_game_title = world.check_game_title(self.screenshot)

                    if is_game_title and pre_match != 'check_game_title':
                        is_match = 'check_game_start'
                        self.update_ui("find-游戏开始界面")
                        world.btn_trim_click()
                        continue

                    if turn_direction == 1:
                        world.run_right()
                        turn_direction = 0
                    else:
                        world.run_left()
                        turn_direction = 1

                    in_battle = battle_pix.is_in_battle(self.screenshot)
                    if in_battle:
                        is_match = 'is_in_battle'
                        is_auto_stay = battle_pix.is_auto_battle_stay()
                        if not is_auto_stay and battle_pix.is_in_round(self.screenshot):
                            is_match = 'is_in_round'
                            battle_pix.btn_auto_battle()
                        elif battle_pix.is_auto_battle_stay():
                            is_match = 'is_auto_battle_stay'
                            battle_pix.btn_auto_battle_start()
                        else:
                            world.btn_trim_click()
                            continue
                    if not is_match:
                        retry_count += 1

                    if retry_count > 300:
                        self.update_ui("未检测到任何界面")
                        is_match = f'not match {retry_count}'
                        self.update_ui(f"检查{retry_count}次{0.1}秒未匹配到任何执行函数，重启游戏")
                        engine.restart_game()
                    continue
                except Exception as e:
                    self.update_ui(f"发生错误: {e}", "debug")
        except Exception as e:
            self.update_ui(f"发生错误: {e}")
