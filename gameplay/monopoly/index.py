
import gc
import time
from app_data import app_data
from engine.world import world
from engine.engine import engine

from gameplay.monopoly.action import btn_center_confirm
from gameplay.monopoly.check_battle import check_in_battle, check_in_battle_auto_stay, check_in_battle_in_round
from gameplay.monopoly.check_in_app import check_in_app
from gameplay.monopoly.check_in_continue import check_in_continue, on_continue
from gameplay.monopoly.check_in_monopoly_map import check_in_monopoly_map
from gameplay.monopoly.check_in_monopoly_page import check_in_monopoly_page
from gameplay.monopoly.check_in_monopoly_setting import check_in_monopoly_setting
from gameplay.monopoly.check_in_select_monopoly import check_in_select_monopoly
from gameplay.monopoly.check_in_world import check_in_world
from gameplay.monopoly.check_in_game_title import check_in_game_title
from gameplay.monopoly.config import config, set_config
from gameplay.monopoly.constants import State
from gameplay.monopoly.daemon import daemon
from gameplay.monopoly.ocr import init_ocr_cache
from utils.stoppable_thread import StoppableThread


class Monopoly():
    def __init__(self):
        self.debug = True
        self.screenshot = None

        self.reset_turn()
        self.reset_round()

    def reset_turn(self):
        self.state = State.Unknow
        self.pre_state = State.Unknow
        self.is_running = True
        self.is_in_app = False
        self.wait_duration = 0

        self.find_enemy = False

        self.total_finish_time = 0
        self.total_failed_time = 0
        self.restart = 0
        self.begin_turn = 0
        self.pre_failed_count = 0
        self.started_count = 0
        self.finished_count = 0
        self.total_finish_time = 0
        self.total_failed_time = 0

        self.pre_crossing = -1
        self.current_crossing = -1

        self.reported_finish = False
        self.reported_end = False

        self.enemy = config.cfg_enemy_map.get(config.cfg_type)
        self.action = config.cfg_action_map.get(config.cfg_type)

        if self.enemy and self.action and config.cfg_enemy_check == 1:
            self.find_enemy = True

    def reset_round(self):
        self.round_time_start = time.time()
        self.wait_time = time.time()
        self.roll_time = 0

    def new_trun(self):
        self.begin_turn = time.time()
        self.roll_time = 0
        self.reported_end = False
        self.reported_finish = False
        self.pre_state = State.Unknow
        self.started_count += 1

    def shot(self):
        try:
            app_data.update_ui("-----------开始截图", 'debug')
            if self.screenshot is not None:
                del self.screenshot
                self.screenshot = None
                gc.collect()
            self.screenshot = engine.device.screenshot(format='opencv')
            app_data.update_ui("-----------截图完成", 'debug')
            return self.screenshot
        except Exception as e:
            app_data.update_ui(f"截图异常{e}")
            return None

    def error_loop(self, e):
        time.sleep(3)
        if "device offline" in str(e) or ("device" in str(e) and "not found" in str(e)):
            app_data.update_ui(f"连接断开")
            engine.reconnect()
        else:
            app_data.update_ui(f"发生错误{e}")

    def start(self):
        try:

            if not set_config():
                app_data.update_ui("配置文件加载失败", 'error')
                return
            init_ocr_cache(config.cfg_type)
            self.reset_turn()
            if self.enemy and self.action and config.cfg_enemy_check == 1:
                self.find_enemy = True
            app_data.update_ui(f"大霸启动!", 'stats')
            self.wait_duration = 0
            # 启动一个子线程守护进程,用来检查是否需要重启游戏
            app_data.monopoly_deamon_thread = StoppableThread(target=lambda: daemon(self))
            app_data.monopoly_deamon_thread.start()
            app_data.update_ui(f"守护线程启动", 'debug')
            # 有空整体重构为有限状态机
            while not app_data.thread_stoped():
                try:
                    app_data.update_ui(f"全量检查", 'debug')

                    turn_state = None
                    turn_check_state = None
                    pre_round_state = None
                    round_state = None
                    round_check_state = None
                    self.shot()

                    turn_check_state = check_in_game_title(monopoly=self)
                    if turn_check_state:
                        self.state = State.Title
                        turn_state = self.state
                        time.sleep(3)

                    turn_check_state = check_in_continue(monopoly=self)
                    if turn_check_state:
                        self.state = State.Continue
                        turn_state = self.state
                        time.sleep(3)

                    turn_check_state = check_in_world(monopoly=self)
                    if turn_check_state:
                        self.state = State.World
                        turn_state = self.state
                        self.shot()

                    turn_check_state = check_in_monopoly_page(monopoly=self)
                    if turn_check_state:
                        self.state = State.MonopolyPage
                        turn_state = self.state
                        self.shot()

                    turn_check_state = check_in_monopoly_setting(monopoly=self)
                    if turn_check_state:
                        self.state = State.MonopolySetting
                        # 流转到一下状态
                        self.state = State.MonopolyMap
                        turn_state = self.state

                    self.round_time_start = time.time()

                    in_map = False
                    while not app_data.thread_stoped():
                        app_data.update_ui(f"地图检查", 'debug')
                        round_state = None
                        self.shot()
                        if check_in_battle(monopoly=self):
                            if pre_round_state != State.Battle:
                                app_data.update_ui(f"战斗界面中")
                            round_state = State.Battle

                        if check_in_battle_in_round(monopoly=self):
                            app_data.update_ui(f"战斗中点击委托")
                            round_state = State.BattleInRound
                            self.shot()

                        if check_in_battle_auto_stay(monopoly=self):
                            app_data.update_ui(f"战斗中点击开始委托战斗")
                            round_state = State.BattleAutoStay
                            time.sleep(2)

                        if round_state:
                            self.state = round_state
                            if round_state == State.Battle and pre_round_state == State.Battle:
                                time.sleep(2)
                            pre_round_state = round_state
                        else:
                            round_check_state = check_in_monopoly_map(monopoly=self)
                            if round_check_state == State.Finised:
                                self.state = State.Finised
                                in_map = False
                                round_state = self.state
                                break
                            elif round_check_state:
                                self.state = State.MonopolyMap
                                round_state = self.state

                        if not round_state:
                            if check_in_world(monopoly=self):
                                round_state = State.World
                            if not round_state and check_in_continue(monopoly=self):
                                round_state = State.Continue
                                on_continue()
                            if not round_state and check_in_select_monopoly(monopoly=self):
                                round_state = State.Unknow
                            if round_state:
                                self.state = round_state
                                in_map = False
                                break
                            else:
                                btn_center_confirm()
                                if not in_map:
                                    break
                        else:
                            in_map = True
                            self.state = round_state
                            if round_state != self.pre_state:
                                app_data.update_ui(f"更新状态{self.state}")
                                self.wait_time = time.time()
                                self.pre_state = round_state

                        round_duration = time.time() - self.round_time_start
                        # 检查本轮等待超时
                        if round_duration > config.cfg_round_time:
                            self.state = State.Unknow
                            round_state = self.state
                            in_map = False
                            break

                        # 检查本轮APP状态
                        if check_in_app(monopoly=self):
                            self.state = State.Unknow
                            round_state = self.state
                            in_map = False
                            break

                    if round_state:
                        turn_state = round_state

                    if turn_state and turn_state != State.Unknow:
                        app_data.update_ui(f"当前状态{self.state}", 'debug')
                        if turn_state != self.pre_state:
                            app_data.update_ui(f"更新状态{self.state}")
                            self.wait_time = time.time()
                    else:
                        self.state = State.Unknow
                        world.btn_trim_click()
                        app_data.update_ui("未匹配到任何状态", 'debug')
                    self.pre_state = turn_state

                except Exception as e:
                    self.error_loop(e)
        except Exception as e:
            self.error_loop(e)
