import time
import cv2
from datetime import datetime
from engine.comparator import comparator
from engine.world import world
from engine.engine import engine
from engine.battle_pix import battle_pix
from utils.config_loader import cfg_monopoly, reload_config, cfg_startup
from app_data import AppData
import json
import os
from enum import Enum
import gc
import traceback

from utils.exe_manager import ExeManager


class State(Enum):
    Finised = -1,
    Unknow = 0,
    World = 1,
    Title = 2,
    Continue = 3,
    MonopolyPage = 4,
    MonopolySetting = 5,
    MonopolyMap = 6,
    Battle = 7,
    BattleInRound = 8,
    BattleAutoStay = 9


exe_manager = ExeManager()


class Monopoly():
    def __init__(self, app_data: AppData):
        self.app_data = app_data
        self.debug = True
        self.crood_range = [(474, 116), (937, 397)]
        self.cfg_type = "801"
        self.cfg_crossing = None
        self.cfg_ticket = 0
        self.cfg_lv = 5
        self.cfg_auto_battle = 1
        self.cfg_isContinue = 1
        self.cfg_check_interval = 0.05
        self.cfg_check_roll_dice_interval = 0.2
        self.cfg_check_roll_dice_time = 2
        self.cfg_check_roll_rule = 1
        self.cfg_check_roll_rule_wait = 0.2
        self.screenshot = None
        self.wait_duration = 0
        self.cfg_r801 = []
        self.cfg_r802 = []
        self.cfg_r803 = []
        self.award_map = {}
        self.cfg_enemy_map = {}
        self.cfg_action_map = {}
        self.cfg_enemy_match_threshold = 0.5
        self.cfg_enemy_check = 0
        self.cfg_bp_type = "max"
        self.total_finish_time = 0
        self.total_failed_time = 0
        self.pre_crossing = -1
        self.current_crossing = -1
        self.is_running = True
        self.reset()

    def thread_stoped(self) -> bool:
        return self.app_data and self.app_data.thread_stoped()

    def update_ui(self, msg: str, type='info'):
        self.app_data and self.app_data.update_ui(msg, type)

    def set_config(self):
        reload_config()
        battle_pix.set(self.app_data)
        try:
            self.cfg_ticket = int(cfg_monopoly.get("ticket"))
            self.cfg_lv = int(cfg_monopoly.get("lv"))
            self.cfg_type = cfg_monopoly.get("type")
            self.cfg_crossing = cfg_monopoly.get(f"crossing.{self.cfg_type}")
            self.cfg_auto_battle = int(cfg_monopoly.get("auto_battle"))
            self.cfg_isContinue = int(cfg_monopoly.get("isContinue"))
            self.cfg_check_interval = float(cfg_monopoly.get("check_interval"))
            self.cfg_check_roll_dice_interval = float(cfg_monopoly.get("check_roll_dice_interval"))
            self.cfg_check_roll_dice_time = int(cfg_monopoly.get("check_roll_dice_time"))
            self.cfg_check_roll_rule = int(cfg_monopoly.get("check_roll_rule"))
            self.cfg_check_roll_rule_wait = float(cfg_monopoly.get("check_roll_rule_wait"))
            self.cfg_bp_type = cfg_monopoly.get("bp_type")
            self.cfg_r801 = cfg_monopoly.get("bp.801")
            self.cfg_r802 = cfg_monopoly.get("bp.802")
            self.cfg_r803 = cfg_monopoly.get("bp.803")
            self.cfg_enemy_map = cfg_monopoly.get("enemy")
            self.cfg_action_map = cfg_monopoly.get("action")
            self.cfg_enemy_match_threshold = float(cfg_monopoly.get("enemy_match_threshold"))
            self.cfg_enemy_check = int(cfg_monopoly.get("enemy_check"))
            self.cfg_round_time = int(cfg_monopoly.get("round_time"))*60
            self.cfg_wait_time = int(cfg_monopoly.get("wait_time"))*60
            self.cfg_exe_path = cfg_startup.get("exe_path")
            exe_manager.set_exe_path(self.cfg_exe_path)
            return True
        except Exception as e:
            self.update_ui(f"{e}")
            return False

    def reset_round(self):
        self.round_time_start = time.time()
        self.wait_time = time.time()
        self.roll_time = 0

    def reset(self):
        self.wait_duration = 0
        self.pre_count = 0
        self.started_count = 0
        self.finished_count = 0
        self.begin_turn = 0
        self.pre_state = State.Unknow
        self.total_finish_time = 0
        self.total_failed_time = 0
        self.restart = 0
        self.reported_finish = False
        self.reported_end = False
        self.find_enemy = False
        self.award_map = {}

        self.is_in_app = True
        self.state = State.Unknow
        self.enemy = self.cfg_enemy_map.get(self.cfg_type)
        self.action = self.cfg_action_map.get(self.cfg_type)
        self.reset_round()

    def new_trun(self):
        self.begin_turn = time.time()
        self.roll_time = 0
        self.reported_end = False
        self.reported_finish = False
        self.pre_state = State.Unknow
        self.started_count += 1

    def report_end(self):
        if not self.reported_finish:
            self.finished_count += 1
            self.reported_finish = True
            self.update_ui(f"find-完成一局", 'debug')

    def report_finish(self):
        if not self.reported_end:
            now = time.time()
            turn_duration = (now - self.begin_turn) / 60
            if self.started_count == 0:
                self.finished_count = 0
                turn_duration = 0

            failed_count = self.started_count - self.finished_count
            if failed_count > self.pre_count:
                self.total_failed_time += turn_duration
            else:
                self.total_finish_time += turn_duration

            self.pre_count = failed_count

            if failed_count < 0:
                failed_count = 0
                self.total_failed_time = 0
                self.total_finish_time = 0

            avg_finish_duration = self.total_finish_time / self.finished_count if self.finished_count > 0 else 0
            avg_failed_duration = self.total_failed_time / failed_count if failed_count > 0 else 0

            total_duration = (self.total_finish_time + self.total_failed_time)

            msg1 = f"成功{self.finished_count}次, 翻车{failed_count}次, 重启{self.restart}次"
            msg2 = f"本轮{turn_duration:.1f}分钟,成功平均{avg_finish_duration:.1f}分钟,翻车平均{avg_failed_duration:.1f}分钟"
            msg3 = f"扔骰子{self.roll_time}次, 总耗时{total_duration:.1f}分钟"
            self.update_ui(f"{msg1},{msg2},{msg3}", 'stats')
            self.reported_end = True

    def check_in_app(self):
        self.is_in_app = engine.check_in_app()
        if not self.is_in_app:
            self.update_ui("未检查到游戏")
            engine.start_app()
            self.update_ui("启动游戏")
            self.reset_round()
            self.restart += 1
            self.state = State.Unknow
            time.sleep(3)
            return True
        return False

    def check_in_game_title(self):
        if self.state == State.Title:
            return
        if self.state and self.state != State.Unknow:
            return
        if world.check_game_title(self.screenshot):
            self.btn_center_confirm()
            return State.Title

    def check_in_game_continue(self):
        if self.state == State.Continue:
            return
        if self.state and self.state != State.Unknow:
            return
        if self.check_continue():
            self.on_continue()
            return State.Continue

    def check_in_world(self):
        if self.state == State.World:
            return
        if self.state and self.state != State.Unknow:
            return
        if world.check_in_world(self.screenshot):
            self.btn_menu_monopoly()
            return State.World

    def check_in_monopoly_page(self):
        if self.state == State.MonopolyPage:
            return
        if not self.state or self.state == State.Unknow or self.state == State.Finised:
            if self.check_page_monopoly():
                self.select_monopoly()
                self.btn_setting_monopoly()
                return State.MonopolyPage

    def check_in_monopoly_setting(self):
        if self.state == State.MonopolySetting or self.state == State.MonopolyMap:
            return
        if self.check_monopoly_setting():
            self.report_finish()
            self.update_ui(f"设置大富翁挑战设定")
            self.set_game_mode()
            self.update_ui(f"开始大富翁,当前第 {self.started_count+1} 轮")
            self.btn_play_monopoly()
            self.new_trun()
            return State.MonopolySetting

    def check_in_battle(self):
        if battle_pix.is_in_battle(self.screenshot):
            return State.Battle

    def check_in_battle_in_round(self, state):
        if state == State.BattleInRound or state == State.BattleAutoStay:
            return
        if battle_pix.is_in_round(self.screenshot):
            if (self.find_enemy):
                self.on_get_enmey()
            if self.cfg_auto_battle == 1:
                self.update_ui(f"点击委托战斗", 'debug')
                battle_pix.btn_auto_battle()
            else:
                battle_pix.btn_attack()
            return State.BattleInRound

    def check_in_battle_auto_stay(self):
        if battle_pix.is_auto_battle_stay(self.screenshot):
            battle_pix.btn_auto_battle_start()
            self.update_ui(f"点击开始委托战斗", 'debug')
            return State.BattleAutoStay

    def check_in_monopoly_map(self):
        new_state = None
        if self.can_roll_dice():
            self.shot()
            new_state = State.MonopolyMap
            input_bp = 0
            rule_text = ""
            if self.cfg_check_roll_rule == 1:
                number = self.check_map_distance(self.screenshot)
                if self.is_number(number):
                    input_bp = self.check_roll_rule(number)
                    rule_text = f"期望: {input_bp},"
                max_bp = self.check_bp_number(self.screenshot)
                self.update_ui(f"距离终点 {number}，当前BP: {max_bp}, {rule_text} 模式: {self.cfg_bp_type}")
                if self.cfg_bp_type == "max":
                    if input_bp > max_bp:
                        input_bp = max_bp
                else:
                    if input_bp == max_bp:
                        input_bp = max_bp
                    else:
                        input_bp = 0
            self.roll_time += 1
            self.roll_dice(input_bp, self.roll_time)

        if not new_state and world.check_stage(self.screenshot):
            new_state = State.MonopolyMap
            battle_pix.cmd_skip()

        if not new_state and self.check_evtent():
            new_state = State.MonopolyMap

        if not new_state and self.check_confirm():
            new_state = State.MonopolyMap

        if not new_state and self.check_accept_confirm():
            new_state = State.MonopolyMap

        if not new_state and self.check_info_confirm():
            new_state = State.MonopolyMap

        if not new_state and self.check_end():
            self.report_end()

        if not new_state and self.check_final_confirm():
            self.btn_final_confirm()
            self.report_finish()
            new_state = State.Finised

        if not new_state:
            crossing_index = self.check_crossing()
            if crossing_index != -1:
                new_state = State.MonopolyMap
                self.turn_auto_crossing(crossing_index)
                self.pre_crossing = crossing_index
        return new_state

    def check_in_monopoly_round_end(self, round_state):
        if time.time() - self.round_time_start > self.cfg_round_time:
            return True
        if round_state == State.Finised:
            return True
        return False

    def shot(self):
        try:
            self.update_ui("-----------开始截图", 'debug')
            if self.screenshot is not None:
                del self.screenshot
                self.screenshot = None
                gc.collect()
            self.screenshot = engine.device.screenshot(format='opencv')
            self.update_ui("-----------截图完成", 'debug')
            return self.screenshot
        except Exception as e:
            self.update_ui(f"截图异常{e}")
            return None

    def start(self):
        try:
            if not self.set_config():
                self.update_ui("配置文件加载失败", 'error')
                return
            self.reset()
            if self.enemy and self.action and self.cfg_enemy_check == 1:
                self.find_enemy = True
            self.update_ui(f"大霸启动!", 'stats')
            self.wait_duration = 0
            # 有空整体重构为有限状态机
            while not self.thread_stoped():
                try:
                    self.update_ui(f"全量检查", 'debug')
                    time.sleep(self.cfg_check_interval)

                    turn_state = None
                    turn_check_state = None
                    pre_round_state = None
                    round_state = None
                    round_check_state = None
                    self.check_in_exe()
                    self.check_state(self.wait_duration)
                    self.check_idle_wait()
                    self.shot()

                    turn_check_state = self.check_in_game_title()
                    if turn_check_state:
                        self.state = State.Title
                        turn_state = self.state
                        time.sleep(3)

                    turn_check_state = self.check_in_game_continue()
                    if turn_check_state:
                        self.state = State.Continue
                        turn_state = self.state
                        time.sleep(3)

                    turn_check_state = self.check_in_world()
                    if turn_check_state:
                        self.state = State.World
                        turn_state = self.state
                        self.shot()

                    turn_check_state = self.check_in_monopoly_page()
                    if turn_check_state:
                        self.state = State.MonopolyPage
                        turn_state = self.state
                        self.shot()

                    turn_check_state = self.check_in_monopoly_setting()
                    if turn_check_state:
                        self.state = State.MonopolySetting
                        # 流转到一下状态
                        self.state = State.MonopolyMap
                        turn_state = self.state

                    self.round_time_start = time.time()

                    in_map = False
                    while not self.thread_stoped():
                        self.update_ui(f"地图检查", 'debug')
                        self.check_idle_wait()
                        round_state = None
                        self.shot()
                        if self.check_in_battle():
                            if pre_round_state != State.Battle:
                                self.update_ui(f"战斗界面中")
                            round_state = State.Battle

                        if self.check_in_battle_in_round(self.state):
                            self.update_ui(f"战斗中点击委托")
                            round_state = State.BattleInRound
                            self.shot()

                        if self.check_in_battle_auto_stay():
                            self.update_ui(f"战斗中点击开始委托战斗")
                            round_state = State.BattleAutoStay
                            time.sleep(2)

                        if round_state:
                            self.state = round_state
                            if round_state == State.Battle and pre_round_state == State.Battle:
                                time.sleep(2)
                            pre_round_state = round_state
                        else:
                            round_check_state = self.check_in_monopoly_map()
                            if round_check_state == State.Finised:
                                self.state = State.Finised
                                in_map = False
                                round_state = self.state
                                break
                            elif round_check_state:
                                self.state = State.MonopolyMap
                                round_state = self.state

                        if not round_state:
                            if self.check_in_world():
                                round_state = State.World
                            if not round_state and self.check_continue():
                                round_state = State.Continue
                                self.on_continue()
                            if not round_state and self.check_page_monopoly():
                                round_state = State.Unknow
                            if round_state:
                                self.state = round_state
                                in_map = False
                                break
                            else:
                                self.btn_center_confirm()
                                if not in_map:
                                    break
                        else:
                            in_map = True
                            self.state = round_state
                            if round_state != self.pre_state:
                                self.update_ui(f"更新状态{self.state}")
                                self.wait_time = time.time()
                                self.pre_state = round_state
                            time.sleep(self.cfg_check_interval)

                        round_duration = time.time() - self.round_time_start
                        # 检查本轮等待超时
                        if round_duration > self.cfg_round_time:
                            exe_manager.stop_exe()
                            self.state = State.Unknow
                            round_state = self.state
                            in_map = False
                            break

                        # 检查本轮APP状态
                        if self.check_state(round_duration):
                            self.state = State.Unknow
                            round_state = self.state
                            in_map = False
                            break

                    if round_state:
                        turn_state = round_state

                    if turn_state and turn_state != State.Unknow:
                        self.update_ui(f"当前状态{self.state}", 'debug')
                        if turn_state != self.pre_state:
                            self.update_ui(f"更新状态{self.state}")
                            self.wait_time = time.time()
                    else:
                        self.state = State.Unknow
                        world.btn_trim_click()
                        self.update_ui("未匹配到任何状态", 'debug')
                    self.pre_state = turn_state

                except Exception as e:
                    self.error_loop(e)
        except Exception as e:
            self.error_loop(e)

    def error_loop(self, e):
        time.sleep(3)
        if "device offline" in str(e) or ("device" in str(e) and "not found" in str(e)):
            self.update_ui(f"连接断开")
            if not engine.reconnect():
                exe_manager.start_exe()
        else:
            self.update_ui(f"地图循环出现异常！{e}")

    def check_idle_wait(self):
        self.update_ui("check-检查空闲等待", 'debug')
        self.check_in_exe()
        self.wait_duration = time.time() - self.wait_time
        if self.wait_duration > self.cfg_wait_time:
            min = self.cfg_wait_time/60
            self.error(f"{int(min)}分钟未匹配到任何执行函数，重启游戏")
            if exe_manager.exe_path and len(exe_manager.exe_path) > 0:
                self.update_ui("由于设置模拟器路径,重启模拟器")
                exe_manager.stop_exe()
            engine.restart_game()
            self.restart += 1
            self.state = State.Unknow
            self.reset_round()
            time.sleep(3)
            return State.Unknow

    def check_state(self, time):
        return self.check_in_app()

    def check_in_exe(self):
        if exe_manager.exe_path is None or len(exe_manager.exe_path) == 0:
            return
        if exe_manager.is_exe_running():
            if self.is_running == False:
                self.is_running = True
                time.sleep(5)
                self.check_in_app()
        else:
            self.is_running = False
            self.update_ui("模拟器未运行,等待启动")
            time.sleep(2)
            exe_manager.start_exe()

    def is_number(self, value):
        return isinstance(value, (int, float))

    def ocr_number(self, screenshot, crop_type="left"):
        if screenshot is None:
            return None
        width = screenshot.shape[1]
        crop_img = None
        scale_src = None
        retry_src = None
        list_img = []
        result = self.process_image(screenshot)

        if not self.is_number(result):
            retry_src = screenshot
            self.write_ocr_log(result, screenshot, 'screenshot')
            result = self.process_image(retry_src)

        self.write_ocr_log(result, retry_src, 'retry_src')

        if not self.is_number(result):
            list_img.append(retry_src)
            crop_src = screenshot
            self.update_ui("未识别到距离，裁剪重试")

            if crop_type == "left":
                crop_offset = 0.31
                crop_img = crop_src[:, int(crop_offset * width):]
            else:
                crop_offset = 0.33
                left = int(crop_offset * width)
                right = int((1 - crop_offset) * width)
                crop_img = crop_src[:, left:right]
            result = self.process_image(crop_img)
            if self.is_number(result):
                self.update_ui("裁剪识别成功")

        self.write_ocr_log(result, crop_img, 'crop_img')

        if not self.is_number(result):
            list_img.append(crop_img)
            scale_src = screenshot
            self.update_ui("未识别到距离，缩小重试")
            offset = 10
            scale_image = cv2.copyMakeBorder(scale_src, offset, offset, offset, offset,
                                             cv2.BORDER_CONSTANT, value=[0, 0, 0])
            self.write_ocr_log(result, scale_image, '')
            result = self.process_image(scale_image)
            if self.is_number(result):
                self.update_ui("缩小识别成功")

        self.write_ocr_log(result, scale_src, 'scale_src')

        if not self.is_number(result):
            list_img.append(scale_image)
            self.update_ui("未识别到距离，预处理重试")
            for i in range(len(list_img)):
                pro_img = list_img[i]
                if (len(pro_img) == 0):
                    continue
                process_img = comparator.process_image(pro_img, threshold_value=120)
                result = comparator.get_num_in_image(process_img)
                self.write_ocr_log(result, process_img, f'process_image_{i}')
                del pro_img
                del process_img
            if self.is_number(result):
                self.update_ui("预处理识别成功")
        del crop_img
        del scale_src
        del retry_src
        del list_img
        return result

    def process_image(self, current_image, threshold=100):
        result = None
        try:
            if current_image is None or len(current_image) == 0:
                return None
            resized_image = cv2.resize(current_image, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
            image = resized_image
            # 分离图像的 BGR 通道
            if resized_image is None or len(resized_image) == 0:
                return None
            if len(resized_image.shape) == 3:
                b_channel, g_channel, r_channel = cv2.split(resized_image)
                # 对每个通道应用阈值操作
                _, b_thresh = cv2.threshold(b_channel, threshold, 255, cv2.THRESH_BINARY)
                _, g_thresh = cv2.threshold(g_channel, threshold, 255, cv2.THRESH_BINARY)
                _, r_thresh = cv2.threshold(r_channel, threshold, 255, cv2.THRESH_BINARY)
                # 将阈值处理后的通道合并回彩色图像
                threshold_image = cv2.merge([b_thresh, g_thresh, r_thresh])
                image = threshold_image
            if image is None or len(image) == 0:
                return None
            result = comparator.get_num_in_image(image)
        except Exception as e:
            self.update_ui(f"process_image异常{e},{traceback.format_exc()}")
        finally:
            del current_image
            del resized_image
            del image
        return result

    def write_ocr_log(self, result, current_image, type):
        if self.is_number(result) or len(current_image) == 0:
            return
        if current_image is None or len(current_image) == 0:
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_path = 'debug_images'
        file_name = f'current_image_{timestamp}_{type}.png'
        os.makedirs(debug_path, exist_ok=True)  # 确保目录存在
        engine.cleanup_large_files(debug_path, 10)  # 清理大于 10 MB 的文件
        cv2.imwrite(os.path.join(debug_path, file_name), current_image)
        return file_name

    def roll_dice(self, bp=0, roll_time=None):
        start_point = (846, 440)
        x, y = start_point
        if bp > 0:
            offset = 58 * bp
            end_point = (x, y - offset)
            engine.long_press_and_drag(start_point, end_point)
            time.sleep(0.5)
            engine.device.click(x, y)
        if bp == 0:
            engine.device.click(x, y)
        self.update_ui(f"第{roll_time}次投骰子, BP: {bp}")
        for i in range(self.cfg_check_roll_dice_time):
            time.sleep(self.cfg_check_roll_dice_interval)
            self.btn_center_confirm()

    def can_roll_dice(self):
        self.update_ui("check-是否可以掷骰子", 'debug')
        if (self.thread_stoped()):
            return False
        if comparator.template_compare("./assets/monopoly/roll_dice.png", [(780, 400), (900, 460)], screenshot=self.screenshot):
            self.update_ui("find-可以掷骰子", 'debug')
            return True
        else:
            return False

    def select_monopoly(self):
        x = 920
        start_y = 140
        end_y = 380
        current_y = start_y
        select = False
        while not select:
            self.shot()
            select = self.find_monopoly()
            if select:
                x, y = select
                if self.check_page_monopoly():
                    engine.device.click(x, y)
                    self.update_ui(f"选择大富翁模式:{self.cfg_type}")
                break
            if (self.thread_stoped()):
                return
            if current_y >= end_y:
                break
            next_y = current_y + 25
            engine.device.swipe(x, current_y, x, next_y, 0.1)
            current_y = next_y

    def find_monopoly(self):
        if (self.thread_stoped()):
            return False
        if self.cfg_type == "801":
            return self.find_power()
        if self.cfg_type == "802":
            return self.find_wealth()
        if self.cfg_type == "803":
            return self.find_fame()

    def find_fame(self):
        template_path = "./assets/monopoly/find_fame.png"
        return comparator.template_compare(template_path, self.crood_range, True, screenshot=self.screenshot)

    def find_wealth(self):
        template_path = "./assets/monopoly/find_wealth.png"
        return comparator.template_compare(template_path, self.crood_range, True, screenshot=self.screenshot)

    def find_power(self):
        template_path = "./assets/monopoly/find_power.png"
        return comparator.template_compare(template_path, self.crood_range, True, screenshot=self.screenshot)

    def set_game_mode(self):
        init_ticket = 1
        init_lv = 0
        while self.cfg_ticket < init_ticket and not self.thread_stoped():
            self.reduce_ticket()
            init_ticket -= 1
        while self.cfg_ticket > init_ticket and not self.thread_stoped():
            self.add_ticket()
            init_ticket += 1
        while self.cfg_lv > init_lv and not self.thread_stoped():
            self.add_lv()
            init_lv += 1
        while self.cfg_lv < init_lv and not self.thread_stoped():
            self.reduce_lv()
            init_lv -= 1

    def add_ticket(self):
        engine.device.click(373, 220)

    def reduce_ticket(self):
        engine.device.click(243, 220)

    def add_lv(self):
        engine.device.click(715, 220)

    def reduce_lv(self):
        engine.device.click(588, 220)

    def turn_auto_crossing(self, crossing_index):
        if self.thread_stoped():
            return
        if not self.cfg_crossing or not self.cfg_crossing[crossing_index]:
            return
        rule = self.cfg_crossing[crossing_index]
        move_step = self.check_move_distance(self.screenshot)
        if not self.is_number(move_step):
            self.update_ui(f"未检测到移动步数,{move_step}")
        self.update_crossing_msg(f"find-大富翁路口{crossing_index}, 移动步数{move_step}")
        default = rule["default"]
        if not self.is_number(move_step):
            if default:
                self.update_crossing_msg(f"未检测到移动步数，使用默认方向{default}")
                self.turn_direction(default)
            else:
                self.update_crossing_msg(f"未检测到移动步数，无默认方向")
            return

        direction_result = None

        try:
            # 遍历 rule 的键
            for direction, range_str in rule.items():
                if direction == "default":
                    continue
                rule_json = f"[{range_str}]"
                ranges = json.loads(rule_json)
                for start, end in ranges:
                    if start <= move_step < end:
                        self.update_crossing_msg(
                            f"find-大富翁路口{crossing_index}规则, 方向{direction}--剩余步数规则 {start}<={move_step}<{end}")
                        # 匹配到方向，执行相应的动作
                        direction_result = direction
                        break
                if direction_result is not None:
                    break
            if direction_result is None:
                direction_result = default
                self.update_crossing_msg(f"匹配不到任何规则使用默认转向{default}")
                if default is None:
                    self.update_crossing_msg(f"没有设置默认转向,将会卡住,请设置配置")
        except Exception as e:
            self.update_ui(f"解析选择方向自定义规则异常{e}")
            return None
        self.turn_direction(direction_result)

    def turn_direction(self, direction):
        if direction == "left":
            engine.device.click(402, 243)
            self.update_crossing_msg("选择左转")
        if direction == "right":
            engine.device.click(558, 243)
            self.update_crossing_msg("选择右转")
        if direction == "up":
            engine.device.click(480, 150)
            self.update_crossing_msg("选择上转")
        if direction == "down":
            engine.device.click(480, 330)
            self.update_crossing_msg("选择下转")

    def update_crossing_msg(self, msg):
        if self.current_crossing == self.pre_crossing:
            return
        self.update_ui(msg)

    def check_page_monopoly(self):
        if (self.thread_stoped()):
            return False
        self.update_ui("check-大富翁选择界面中", 'debug')
        if comparator.template_compare(f"./assets/monopoly/page_monopoly.png", screenshot=self.screenshot):
            self.update_ui("find-在大富翁选择界面中", 'debug')
            return True
        return False

    def check_page_monopoly_map(self):
        if (self.thread_stoped()):
            return False
        self.update_ui("check-大富翁地图界面中", 'debug')
        if comparator.template_compare(f"./assets/monopoly/monopoly_map.png", screenshot=self.screenshot):
            self.update_ui("find-在大富翁地图界面中", 'debug')
            return True
        return False

    def check_monopoly_setting(self):
        if (self.thread_stoped()):
            return False
        self.update_ui("check-大富翁选择模式界面中", 'debug')
        if comparator.template_compare("./assets/monopoly/monopoly_setting.png", screenshot=self.screenshot):
            self.update_ui("find-在大富翁选择模式界面中", 'debug')
            return True
        return False

    def check_crossing(self):
        self.update_ui("check-大富翁路口", 'debug')
        if (self.thread_stoped()):
            return -1
        current_crossing = self.check_crossing_index()
        if current_crossing != -1:
            self.current_crossing = current_crossing
            self.update_crossing_msg(f"当前在大富翁路口格子{current_crossing}")
            return current_crossing
        return -1

    def check_crossing_index(self):
        if (self.thread_stoped()):
            return None
        num = None
        strType = -1

        if self.cfg_type == "801":
            num = [46, 36, 30, 15]
            strType = "power"
        if self.cfg_type == "802":
            num = [45, 34, 10]
            strType = "wealth"
        if self.cfg_type == "803":
            num = [41, 20]
            strType = "fame"
        if not num or not strType:
            return -1
        for i in range(len(num)):
            if comparator.template_compare(f"./assets/monopoly/{strType}_crossing_{num[i]}.png", screenshot=self.screenshot):
                return i
        return -1

    def check_move_distance(self, screenshot):
        number = None
        try:
            x, y, width, height = 863, 421, 30, 20
            currentshot = screenshot
            if len(currentshot) == 0:
                currentshot = self.shot()
            current_image = currentshot[y:y+height, x:x+width]

            number = self.ocr_number(current_image, crop_type="center")
            self.update_ui(f"check-剩余步数")
            if not self.is_number(number):
                time.sleep(self.cfg_check_roll_rule_wait)
                currentshot = self.shot()
                current_image = currentshot[y:y+height, x:x+width]
                number = self.ocr_number(current_image)
            return number
        except Exception as e:
            self.update_ui(f"check-剩余步数异常{e},{number}")
            return None

    def check_confirm(self):
        self.update_ui("check-奖励确认界面", 'debug')
        coord = comparator.template_compare(f"./assets/monopoly/btn_confirm_award.png",
                                            return_center_coord=True, screenshot=self.screenshot)
        if coord:
            self.update_ui("find-奖励确认界面", 'debug')
            engine.device.click(coord[0], coord[1])
            return True
        return False

    def check_accept_confirm(self):
        self.update_ui("check-奖励入账确认界面", 'debug')
        points_with_colors = [(688, 55, [253, 251, 252]), (528, 59, [244, 243, 241]),
                              (533, 74, [233, 229, 226]), (513, 80, [198, 194, 191])]
        if comparator.match_point_color(points_with_colors, screenshot=self.screenshot):
            self.update_ui("find-奖励入账确认界面", 'debug')
            self.btn_accept_confirm()
            return True
        return False

    def check_info_confirm(self):
        self.update_ui("check-信息确认界面", 'debug')
        flod = [(68, 483, [98, 97, 95]), (61, 472, [170, 165, 161]),
                (61, 493, [171, 170, 168]), (51, 482, [172, 171, 166])]
        unflod = [(72, 483, [183, 180, 175]), (57, 483, [149, 146, 141]),
                  (57, 483, [149, 146, 141]), (63, 493, [126, 128, 125])]
        check_list = [flod, unflod]
        for check in check_list:
            if comparator.match_point_color(check, screenshot=self.screenshot):
                self.update_ui("find-信息确认界面", 'debug')
                self.btn_center_confirm()
                return True
        return False

    def check_final_confirm(self):
        self.update_ui("check-最终确认界面", 'debug')
        points_with_colors = [(533, 102, [168, 167, 165]), (533, 111, [168, 167, 165]),
                              (533, 121, [180, 179, 177]), (487, 106, [243, 242, 238]),
                              (487, 115, [236, 235, 233]), (441, 112, [236, 235, 233]),
                              (432, 119, [211, 210, 208])]
        if comparator.match_point_color(points_with_colors, screenshot=self.screenshot):
            self.update_ui("find-最终确认界面", 'debug')
            return True
        return False

    def check_continue(self):
        self.update_ui("check-是否继续游戏", 'debug')
        coord = comparator.template_compare(f"./assets/monopoly/monopoly_continue.png", screenshot=self.screenshot)
        if coord:
            self.update_ui("find-继续游戏")
            return State.Continue
        return False

    def check_evtent(self):
        self.update_ui("check-事件", 'debug')
        coord = comparator.template_compare(f"./assets/monopoly/btn_options.png",
                                            return_center_coord=True, screenshot=self.screenshot)
        if coord:
            self.update_ui("find-事件", 'debug')
            x, y = coord
            offfset = 120
            engine.device.click(x + offfset, y)
            return True
        return False

    def check_end(self):
        self.update_ui("check-是否结束", 'debug')
        points_with_colors = [
            (486, 111, [233, 232, 228]),
            (486, 111, [233, 232, 228]),
            (486, 111, [233, 232, 228]),
            (486, 111, [233, 232, 228]),
            (159, 174, [102, 96, 82]),
            (164, 175, [53, 43, 31]),
            (442, 113, [236, 235, 233])]
        if comparator.match_point_color(points_with_colors, screenshot=self.screenshot):
            self.update_ui("find-结算")
            return True
        return False

    def check_map_distance(self, screenshot):
        number = None
        if (screenshot is None):
            return 0
        try:
            x, y, width, height = 708, 480, 28, 20
            currentshot = screenshot
            if len(currentshot) == 0:
                currentshot = self.shot()
            current_image = currentshot[y:y+height, x:x+width]
            number = self.ocr_number(current_image)
            if not self.is_number(number):
                self.update_ui(f"检查距离失败")
                time.sleep(self.cfg_check_roll_rule_wait)
                currentshot = self.shot()
                current_image = currentshot[y:y+height, x:x+width]
                number = self.ocr_number(current_image)
            return number
        except Exception as e:
            self.update_ui(f"检查距离出现异常{e} {number}")
            return None

    def check_roll_rule(self, number):
        if not number:
            self.update_ui("检查距离失败", 'debug')
            return 0
        try:
            rules_map = {
                "801": self.cfg_r801,
                "802": self.cfg_r802,
                "803": self.cfg_r803
            }
            rule = rules_map.get(self.cfg_type, "")
            if not rule:
                return 0
            rule_json = f"[{rule}]"
            ranges = json.loads(rule_json)
            for start, end, bp in ranges:
                if start >= number > end:
                    return bp
            return 0
        except Exception as e:
            self.update_ui(f"检查自定义扔骰子规则出现异常 {str(e)}")
            return 0

    def check_bp_number(self, screenshot):
        if screenshot is None:
            return 0
        bp3 = [865, 456]
        bp2 = [848, 456]
        bp1 = [832, 456]
        pt_bp1 = screenshot[bp1[1], bp1[0]]
        pt_bp2 = screenshot[bp2[1], bp2[0]]
        pt_bp3 = screenshot[bp3[1], bp3[0]]
        b_bp1 = pt_bp1[0]
        b_bp2 = pt_bp2[0]
        b_bp3 = pt_bp3[0]
        g_bp1 = pt_bp1[1]
        g_bp2 = pt_bp2[1]
        g_bp3 = pt_bp3[1]
        r_bp1 = pt_bp1[2]
        r_bp2 = pt_bp2[2]
        r_bp3 = pt_bp3[2]
        limit = 100
        result = 0
        if r_bp1 > limit and g_bp1 > limit and b_bp1 > limit:
            result = 1
        if r_bp2 > limit and g_bp2 > limit and b_bp2 > limit:
            result = 2
        if r_bp3 > limit and g_bp3 > limit and b_bp3 > limit:
            result = 3

        print(f"r_bp1:{r_bp1},r_bp2:{r_bp2},r_bp3:{r_bp3}")
        del pt_bp1
        del pt_bp2
        del pt_bp3
        return result

    def on_get_enmey(self):
        try:
            enemy = self.cfg_enemy_map.get(self.cfg_type)
            action = self.cfg_action_map.get(self.cfg_type)
            current_enemy = None

            if not enemy or not action:
                return

            for key, value in enemy.items():
                if not value:
                    continue
                self.update_ui(f"开始匹配敌人{key}")
                try:
                    normalized_path = os.path.normpath(value)
                    result = comparator.template_compare(
                        normalized_path, [(15, 86), (506, 448)], match_threshold=self.cfg_enemy_match_threshold, screenshot=self.screenshot, pack=False)
                except Exception as e:
                    self.update_ui(f"匹配敌人{key}出现异常{e}")
                    continue
                if result:
                    current_enemy = key
                    self.update_ui(f"匹配到敌人{current_enemy}")
                    break
                else:
                    self.update_ui(f"未匹配到敌人{key}")
            if not current_enemy:
                self.update_ui("未匹配到任何敌人")
                return

            current_action = action.get(current_enemy)
            if not current_action:
                self.update_ui(f"未找到敌人{current_enemy}的行动")
                return
            for value in current_action:
                if len(value) == 0:
                    continue
                parts = value.split(',')
                command = parts[0]
                self.update_ui(f"执行命令{command}")
                if command == "Click":
                    x = int(parts[1])
                    y = int(parts[2])
                    engine.device.click(x, y)

        except Exception as e:
            self.update_ui(f"处理敌人行动出现异常{e}")

    def on_continue(self):
        if self.cfg_isContinue == 0:
            self.btn_not_continue()
        else:
            self.btn_continue()

    def btn_accept_confirm(self):
        engine.device.click(484, 470)

    def btn_center_confirm(self):
        engine.device.click(480, 254)

    def btn_final_confirm(self):
        engine.device.click(480, 410)

    def btn_menu_monopoly(self):
        engine.device.click(455, 459)

    def btn_setting_monopoly(self):
        engine.device.click(843, 448)

    def btn_play_monopoly(self):
        engine.device.click(600, 430)
        pass

    def btn_not_continue(self):
        engine.device.click(362, 362)

    def btn_continue(self):
        engine.device.click(536, 362)

    def error(self, msg):
        print(msg)
        self.update_ui(msg)
