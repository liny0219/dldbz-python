from __future__ import annotations
import time
from app_data import AppData
from engine.world import world
from engine.battle_pix import battle
from engine.u2_device import u2_device
from utils.config_loader import cfg_stationary
from gameplay.stationary.constants import State


class Stationary:
    def __init__(self, app_data: AppData):
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
            is_match: State = State.Unknow
            pre_match: State = State.Unknow
            in_battle = False
            is_run = False
            pre_turn_round = None
            turn_round = 0
            battle_total_count = 0
            battle_count = 0
            cfg_stationary.reload()
            cat_run = cfg_stationary.get("cat_run")
            run_enabled = cfg_stationary.get("run_enabled")
            max_battle_count = int(cfg_stationary.get("max_battle_count"))
            max_run_count = int(cfg_stationary.get("max_run_count"))
            battle_wait_time = float(cfg_stationary.get("battle_wait_time"))
            run_count = max_battle_count
            is_cat_lv = 0
            turn_direction = 1
            is_auto_battle = False
            while not self.thread_stoped():
                try:
                    pre_match = is_match
                    if is_match != State.Unknow and is_match is not None:
                        retry_count = 0
                        self.update_ui(f"匹配到的函数 {is_match} ", "debug")

                    is_match = State.Unknow
                    time.sleep(0.1)
                    self.screenshot = u2_device.device.screenshot(format='opencv')
                    is_in_app = True
                    in_battle = False
                    is_auto_battle_stay = False
                    is_round = False
                    is_world = world.check_in_world(self.screenshot)
                    in_battle = battle.is_in_battle(self.screenshot)
                    is_auto_battle_stay = battle.is_auto_battle_stay(self.screenshot)
                    is_round = battle.is_in_round(self.screenshot)

                    if not in_battle:
                        is_in_app = u2_device.check_in_app()
                    if not is_in_app:
                        is_match = State.NotApp
                        self.update_ui("未检查到游戏")
                        u2_device.start_app()
                        continue

                    is_game_title = False
                    if not in_battle:
                        is_game_title = world.check_game_title(self.screenshot)

                    if is_game_title and pre_match != State.Title:
                        is_match = State.Title
                        self.update_ui("find-游戏开始界面")
                        world.btn_trim_click()
                        continue

                    world_start_time = time.time()
                    world_duration = 0
                    world_round_settle = True
                    while is_world and not in_battle and not self.thread_stoped():
                        if world_round_settle:
                            world_round_settle = False
                            turn_round += 1
                            if run_enabled and battle_count >= max_battle_count and not is_run:
                                self.update_ui(f"战斗次数{battle_count}达到上限{max_battle_count}, 开始逃跑")
                                is_run = True
                                run_count = 0

                            if run_enabled and run_count >= max_run_count and is_run:
                                self.update_ui(f"逃跑次数{run_count}达到上限{max_run_count}，开始战斗")
                                is_run = False
                                battle_count = 0
                            if not is_run:
                                self.update_ui(f"总战斗次数: {battle_total_count}")
                                battle_count += 1
                                battle_total_count += 1

                        is_match = State.World
                        if turn_direction == 1:
                            world.run_right()
                            turn_direction = 0
                        else:
                            world.run_left()
                            turn_direction = 1

                        world_duration = time.time() - world_start_time
                        if world_duration > 60:
                            self.update_ui("世界地图循环超时，重新开始")
                            break
                        time.sleep(0.1)
                        self.screenshot = u2_device.device.screenshot(format='opencv')
                        in_battle = battle.is_in_battle(self.screenshot)
                        is_auto_battle_stay = battle.is_auto_battle_stay(self.screenshot)
                        is_round = battle.is_in_round(self.screenshot)
                        if in_battle or is_auto_battle_stay or is_round:
                            break

                    if turn_round != pre_turn_round:
                        self.update_ui("check-是否遇猫")
                        is_cat_lv = battle.is_cat(self.screenshot)
                        if is_cat_lv != 0:
                            self.update_ui(f"find-{is_cat_lv}级猫")
                        pre_turn_round = turn_round

                    if in_battle or is_auto_battle_stay or is_round:
                        is_match = State.Battle
                        if is_cat_lv != 0 and cat_run:
                            battle.btn_quit_battle()
                            self.update_ui(f"遇到猫，逃跑")
                            time.sleep(battle_wait_time)
                            is_auto_battle = False
                            continue
                        if run_enabled and is_run and is_round and is_cat_lv == 0:
                            battle.btn_quit_battle()
                            run_count += 1
                            self.update_ui(f"逃跑次数{run_count},最大次数{max_run_count}，逃跑")
                            time.sleep(battle_wait_time)
                            continue
                        if not is_auto_battle_stay and is_round:
                            if not run_enabled and is_auto_battle:
                                continue
                            is_match = State.BattleAutoStay
                            battle.btn_auto_battle()
                            self.update_ui("点击自动战斗")
                            time.sleep(battle_wait_time)
                            continue
                        if is_auto_battle_stay:
                            if not run_enabled and is_auto_battle:
                                continue
                            is_match = State.BattleInRound
                            battle.btn_auto_battle_start()
                            self.update_ui("点击自动战斗开始")
                            time.sleep(battle_wait_time)
                            is_auto_battle = True
                            continue
                        else:
                            self.screenshot = u2_device.device.screenshot(format='opencv')
                            is_round = battle.is_in_round(self.screenshot)
                            if run_enabled and not is_round and (is_cat_lv == 0 or cat_run):
                                self.update_ui(f"点击取消委托战斗", "debug")
                                battle.btn_auto_battle_stop()
                            else:
                                self.update_ui("点击空白处", "debug")
                                world.btn_trim_click()
                            continue

                    if not is_match or is_match == State.Unknow:
                        retry_count += 1
                        world.btn_trim_click()

                    if retry_count > 300:
                        retry_count = 0
                        self.update_ui("未检测到任何界面")
                        is_match = State.Unknow
                        self.update_ui(f"检查{retry_count}次{0.1}秒未匹配到任何执行函数，重启游戏")
                        u2_device.restart_game()
                    continue
                except Exception as e:
                    self.update_ui(f"发生错误: {e}")
        except Exception as e:
            self.update_ui(f"发生错误: {e}")
