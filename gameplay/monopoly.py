import time
import cv2
import datetime
from engine.comparator import comparator
from engine.world import world
from engine.engine import engine
from engine.battle_pix import battle_pix
from utils.config_loader import cfg_monopoly, reload_config
from app_data import AppData
import json
import os
from enum import Enum


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


class Monopoly():
    def __init__(self, global_data: AppData):
        self.global_data = global_data
        self.debug = True
        self.crood_range = [(474, 116), (937, 397)]
        self.cfg_type = "801"
        self.cfg_crossing = None
        self.cfg_ticket = 0
        self.cfg_lv = 5
        self.cfg_auto_battle = 1
        self.cfg_isContinue = 1
        self.cfg_check_interval = 0.2
        self.cfg_check_roll_dice_interval = 0.2
        self.cfg_check_roll_dice_time = 2
        self.cfg_check_roll_rule = 1
        self.cfg_check_roll_rule_time = 8
        self.cfg_check_roll_rule_wait = 0.2
        self.screenshot = None
        self.cfg_r801 = []
        self.cfg_r802 = []
        self.cfg_r803 = []
        self.award_map = {}
        self.cfg_enemy_map = {}
        self.cfg_action_map = {}
        self.cfg_enemy_match_threshold = 0.5
        self.cfg_enemy_check = 0
        self.total_finish_time = 0
        self.pre_check_time = -1
        self.cfg_check_time = 120
        self.pre_crossing = -1
        self.reset()

    def thread_stoped(self) -> bool:
        return self.global_data and self.global_data.thread_stoped()

    def update_ui(self, msg: str, type='info'):
        self.global_data and self.global_data.update_ui(msg, type)

    def set_config(self):
        reload_config()
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
        self.cfg_check_roll_rule_time = int(cfg_monopoly.get("check_roll_rule_time"))
        self.cfg_check_roll_rule_wait = float(cfg_monopoly.get("check_roll_rule_wait"))
        self.cfg_r801 = cfg_monopoly.get("bp.801")
        self.cfg_r802 = cfg_monopoly.get("bp.802")
        self.cfg_r803 = cfg_monopoly.get("bp.803")
        self.cfg_enemy_map = cfg_monopoly.get("enemy")
        self.cfg_action_map = cfg_monopoly.get("action")
        self.cfg_enemy_match_threshold = float(cfg_monopoly.get("enemy_match_threshold"))
        self.cfg_enemy_check = int(cfg_monopoly.get("enemy_check"))
        self.cfg_round_time = int(cfg_monopoly.get("round_time"))*60
        self.cfg_wait_time = int(cfg_monopoly.get("wait_time"))*60
        self.cfg_check_time = int(cfg_monopoly.get("check_time"))

    def reset_round(self):
        self.round_time_start = time.time()
        self.wait_time = time.time()
        self.roll_time = 0

    def reset(self):
        self.started_count = 0
        self.finished_count = 0
        self.total_finish_time = 0
        self.begin_time = time.time()
        self.begin_turn = self.begin_time
        self.total_duration = 0
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
        self.started_count += 1

    def report_end(self):
        if not self.reported_finish:
            self.finished_count += 1
            self.reported_finish = True

    def report_finish(self):
        if not self.reported_end:
            now = time.time()
            total_duration = (now - self.begin_time) / 60
            turn_duration = (now - self.begin_turn) / 60
            failed_count = self.started_count - self.finished_count
            if self.finished_count == 0 and self.started_count == 0:
                turn_duration = 0
                total_duration = 0
            if failed_count < 0:
                failed_count = 0
            self.total_finish_time += turn_duration
            avg_duration = self.total_finish_time / self.finished_count if self.finished_count > 0 else 0
            msg1 = f"完成{self.finished_count}次, 翻车{failed_count}次, 重启{self.restart}次"
            msg2 = f"本轮{turn_duration:.1f}分钟,平均{avg_duration:.1f}分钟 扔骰子{self.roll_time}次, 总耗时{total_duration:.1f}分钟"
            self.update_ui(f"{msg1},{msg2}", 'stats')
            self.reported_end = True

    def check_restart(self):
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
        if self.state == State.Title or self.state != State.Unknow:
            return
        if world.check_game_title(self.screenshot):
            self.update_ui("检查到游戏开始界面")
            self.btn_center_confirm()
            return State.Title

    def check_in_game_continue(self):
        if self.state == State.Continue or self.state != State.Unknow:
            return
        if self.check_continue():
            self.update_ui("检查到继续游戏")
            self.on_continue()
            return State.Continue

    def check_in_world(self):
        if self.state == State.World or self.state != State.Unknow:
            return
        if world.check_in_world(self.screenshot):
            self.btn_menu_monopoly()
            return State.World

    def check_in_monopoly_page(self):
        if self.state == State.MonopolyPage:
            return
        if self.state != State.Unknow and self.state != State.Finised:
            return
        if self.check_page_monopoly():
            self.select_monopoly()
            self.btn_setting_monopoly()
            return State.MonopolyPage

    def check_in_monopoly_setting(self):
        if self.state == State.MonopolySetting:
            return
        if self.state != State.Unknow and self.state != State.Finised:
            return
        if self.check_monopoly_setting():
            self.report_finish()
            self.set_game_mode()
            self.btn_play_monopoly()
            self.new_trun()
            return State.MonopolySetting

    def check_in_battle(self):
        if battle_pix.is_in_battle(self.screenshot):
            return State.Battle

    def check_in_battle_in_round(self):
        if battle_pix.is_in_round(self.screenshot):
            if (self.find_enemy):
                self.on_get_enmey()
            if self.cfg_auto_battle == 1:
                battle_pix.btn_auto_battle()
            else:
                battle_pix.btn_attack()
            return State.BattleInRound

    def check_in_battle_auto_stay(self):
        if battle_pix.is_auto_battle_stay():
            battle_pix.btn_auto_battle_start()
            return State.BattleAutoStay

    def check_in_monopoly_map(self):
        new_state = None
        if self.can_roll_dice():
            new_state = State.MonopolyMap
            input_bp = 0
            if self.cfg_check_roll_rule == 1:
                number = self.check_distance(self.screenshot)
                input_bp = self.check_roll_rule(number)
                max_bp = self.check_bp_number(self.screenshot)
                self.update_ui(f"距离终点 {number}，当前BP: {max_bp}")
                if input_bp > max_bp:
                    input_bp = max_bp
            self.roll_time += 1
            self.roll_dice(input_bp, self.roll_time)

        if world.check_stage(self.screenshot):
            new_state = State.MonopolyMap
            battle_pix.cmd_skip()

        if self.check_evtent():
            new_state = State.MonopolyMap

        if self.check_confirm():
            new_state = State.MonopolyMap

        if self.check_accept_confirm():
            new_state = State.MonopolyMap

        if self.check_info_confirm():
            new_state = State.MonopolyMap

        if self.check_end():
            self.report_end()

        if self.check_final_confirm():
            self.btn_final_confirm()
            self.report_finish()
            new_state = State.Finised

        crossing_index = self.check_crossing()
        if crossing_index != -1:
            new_state = State.MonopolyMap
            self.turn_crossing(crossing_index)
            self.pre_crossing = crossing_index
        return new_state

    def check_in_monopoly_round(self, round_state):
        if time.time() - self.round_time_start > self.cfg_round_time:
            return False
        if round_state == State.Finised:
            return False
        return True

    def start(self):
        self.set_config()
        self.reset()
        if self.enemy and self.action and self.cfg_enemy_check == 1:
            self.find_enemy = True
        self.update_ui(f"大霸启动!", 'stats')
        wait_duration = 0
        run_in_map = False
        while not self.thread_stoped():
            try:
                self.update_ui(f"全量检查", 'debug')
                time.sleep(self.cfg_check_interval)
                self.screenshot = engine.device.screenshot(format='opencv')
                # 每轮执行状态(完整一轮执行状态,包含启动界面\地图\战斗\结算等)
                turn_state = None
                # 每回合执行状态(仅在大富翁地图的回合执行状态,包含大富翁里面扔骰子\事件\结算等)
                round_state = None
                self.check_deamon(wait_duration)
                if not turn_state:
                    turn_state = self.check_in_game_title()
                if not turn_state:
                    turn_state = self.check_in_game_continue()
                if not turn_state:
                    turn_state = self.check_in_world()
                if not turn_state:
                    turn_state = self.check_in_monopoly_page()
                if not turn_state:
                    turn_state = self.check_in_monopoly_setting()
                if turn_state == State.MonopolySetting:
                    self.state = State.MonopolyMap

                self.round_time_start = time.time()
                while True:
                    self.update_ui(f"地图检查", 'debug')
                    round_state = None
                    check_state = self.check_in_battle()
                    if check_state:
                        check_state = self.check_in_battle_in_round()
                        check_state = self.check_in_battle_auto_stay()
                    if not check_state:
                        check_state = self.check_in_monopoly_map()

                    round_state = check_state

                    if round_state:
                        run_in_map = True
                        self.wait_time = time.time()
                    else:
                        self.btn_center_confirm()

                    round_duration = time.time() - self.round_time_start

                    if self.check_deamon(round_duration):
                        run_in_map = False
                        break
                    time.sleep(self.cfg_check_interval)
                    self.screenshot = engine.device.screenshot(format='opencv')
                    is_in_map = self.check_in_monopoly_round(round_state)
                    if not run_in_map or not is_in_map or self.thread_stoped():
                        run_in_map = False
                        break
                if round_state:
                    turn_state = round_state
                if turn_state:
                    self.wait_time = time.time()
                    self.state = turn_state
                    self.update_ui(f"当前状态{self.state}", 'debug')
                else:
                    self.state = State.Unknow
                    world.btn_trim_click()
                    self.update_ui("未匹配到任何状态", 'debug')

                wait_duration = time.time() - self.wait_time
                if wait_duration > self.cfg_wait_time:
                    min = self.cfg_wait_time/60
                    self.error(f"{int(min)}分钟未匹配到任何执行函数，重启游戏")
                    engine.restart_game()
                    self.restart += 1
                    self.state = State.Unknow
                    self.reset_round()
                    time.sleep(3)

            except Exception as e:
                self.update_ui(f"出现异常！{e}")

    def check_deamon(self, time):
        time = int(time)
        if (time % self.cfg_check_time == 0 and time != self.pre_check_time) or self.pre_check_time == -1:
            self.pre_check_time = time
            if time > 0:
                self.update_ui(f"本轮已经运行{time}秒,自检一次")
            return self.check_restart()

    def ocr_number(self, screenshot):
        # if type == 'origin' and not debug:
        #     path = 'debug_images/current_image_20240917_073435_origin.png'
        #     current_image = cv2.imread(path)

        width = screenshot.shape[1]
        process_image_origin = None
        process_image_origin_retry = None
        process_image_crop = None
        process_image_scale = None
        process_image_list = [screenshot]
        result, process_image_origin = self.process_image(screenshot)

        if not result:
            process_image_list.append(process_image_origin)
            retry_src = screenshot

            self.write_ocr_log(result, retry_src, type)
            result, process_image_origin_retry = self.process_image(retry_src)

        if not result:
            process_image_list.append(process_image_origin_retry)
            crop_src = screenshot

            self.update_ui("未识别到距离，裁剪重试")
            crop_offset = 0.33
            crop_img = crop_src[:, int(crop_offset * width):]
            result, process_image_crop = self.process_image(crop_img)
            if result:
                self.update_ui("裁剪识别成功")

        if not result:
            process_image_list.append(process_image_crop)
            scale_src = screenshot

            self.update_ui("未识别到距离，缩小重试")
            offset = 10
            scale_image = cv2.copyMakeBorder(scale_src, offset, offset, offset, offset,
                                             cv2.BORDER_CONSTANT, value=[0, 0, 0])
            result, process_image_scale = self.process_image(scale_image)
            if result:
                self.update_ui("缩小识别成功")

        if not result:
            process_image_list.append(process_image_scale)

            self.update_ui("未识别到距离，预处理重试")
            # 遍历process_image，找到第一个识别成功的图片
            for image in process_image_list:
                image = comparator.process_image(image, 120)
                result = self.process_image(image)
                if result:
                    self.update_ui("预处理识别成功")
                    break
        return result

    def process_image(self, current_image):
        resized_image = cv2.resize(current_image, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
        _, threshold_image = cv2.threshold(resized_image, 100, 255, cv2.THRESH_BINARY)
        process_image = threshold_image
        result = comparator.get_num_in_image(process_image)
        return result, process_image

    def write_ocr_log(self, result, current_image, type):
        if result:
            return
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_path = 'debug_images'
        file_name = f'current_image_{timestamp}_{type}.png'
        os.makedirs(debug_path, exist_ok=True)  # 确保目录存在
        engine.cleanup_large_files(debug_path, 10)  # 清理大于 10 MB 的文件
        cv2.imwrite(os.path.join(debug_path, file_name), current_image)
        return file_name

    def write_awards_with_timestamp(self, award_list, file_path):
        try:
            with open(file_path, 'a', encoding='utf-8') as file:
                # 获取当前时间，格式化为 YYYY-MM-DD HH:MM:SS
                current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                strAward = json.dumps(award_list, ensure_ascii=False)
                file.write(f"{current_time}: {strAward}\n")
            print(f"成功写入文件：{file_path}")
        except Exception as e:
            print(f"写入文件时出错: {e}")

    def roll_dice(self, bp=0, roll_time=None):
        start_point = (846, 440)
        x, y = start_point
        if bp > 0:
            offset = 58 * bp
            end_point = (x, y - offset)
            engine.long_press_and_drag(start_point, end_point)
        if bp == 0:
            engine.device.click(x, y)
        self.update_ui(f"第{roll_time}次投骰子, BP: {bp}")
        for i in range(self.cfg_check_roll_dice_time):
            time.sleep(self.cfg_check_roll_dice_interval)
            self.btn_center_confirm()

    def can_roll_dice(self):
        self.update_ui("开始检查是否可以掷骰子", 'debug')
        if (self.thread_stoped()):
            return False
        if comparator.template_compare("./assets/monopoly/roll_dice.png", [(780, 400), (900, 460)], return_center_coord=True, screenshot=self.screenshot):
            self.update_ui("检查到可以掷骰子", 'debug')
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
            self.screenshot = engine.device.screenshot(format='opencv')
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
            next_y = current_y + 50
            engine.device.swipe(x, current_y, x, next_y, 0.1)
            current_y = next_y

    def find_monopoly(self):
        if (self.thread_stoped()):
            return False
        if self.cfg_type == "801":
            return self.find_previlege()
        if self.cfg_type == "802":
            return self.find_treasure()
        if self.cfg_type == "803":
            return self.find_reputation()

    def find_reputation(self):
        template_path = "./assets/monopoly/find_reputation.png"
        return comparator.template_compare(template_path, self.crood_range, True, screenshot=self.screenshot)

    def find_treasure(self):
        template_path = "./assets/monopoly/find_treasure.png"
        return comparator.template_compare(template_path, self.crood_range, True, screenshot=self.screenshot)

    def find_previlege(self):
        template_path = "./assets/monopoly/find_previlege.png"
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

    def turn_crossing(self, crossing_index):
        if (self.thread_stoped()):
            return
        direction = ""
        if crossing_index != None and self.cfg_crossing and self.cfg_crossing[crossing_index]:
            direction = self.cfg_crossing[crossing_index]
            self.update_crossing_msg(f"匹配到大富翁路口{crossing_index}，选择方向{direction}", crossing_index)
        if direction == "left":
            engine.device.click(402, 243)
            self.update_crossing_msg("选择左转", crossing_index)
        if direction == "right":
            engine.device.click(558, 243)
            self.update_crossing_msg("选择右转", crossing_index)
        if direction == "up":
            engine.device.click(480, 150)
            self.update_crossing_msg("选择上转", crossing_index)
        if direction == "down":
            engine.device.click(480, 330)
            self.update_crossing_msg("选择下转", crossing_index)

    def update_crossing_msg(self, msg, crossing_index):
        if crossing_index == self.pre_crossing:
            return
        self.update_ui(msg)

    def check_page_monopoly(self):
        if (self.thread_stoped()):
            return False
        self.update_ui("开始检查是否在大富翁选择界面中", 'debug')
        if comparator.template_compare(f"./assets/monopoly/page_monopoly.png", screenshot=self.screenshot):
            self.update_ui("检查到在大富翁选择界面中", 'debug')
            return True
        return False

    def check_page_monopoly_map(self):
        if (self.thread_stoped()):
            return False
        self.update_ui("开始检查是否在大富翁地图界面中", 'debug')
        if comparator.template_compare(f"./assets/monopoly/monopoly_map.png", screenshot=self.screenshot):
            self.update_ui("检查到在大富翁地图界面中", 'debug')
            return True
        return False

    def check_monopoly_setting(self):
        if (self.thread_stoped()):
            return False
        self.update_ui("开始检查是否在大富翁选择模式界面中", 'debug')
        if comparator.template_compare("./assets/monopoly/monopoly_setting.png", screenshot=self.screenshot):
            self.update_ui("检查到在大富翁选择模式界面中", 'debug')
            return True
        return False

    def check_crossing(self):
        self.update_ui("开始检查大富翁路口", 'debug')
        if (self.thread_stoped()):
            return -1
        current_crossing = self.check_crossing_index()
        if current_crossing != -1:
            self.update_crossing_msg(f"当前在大富翁路口格子{current_crossing}", current_crossing)
            return current_crossing
        return -1

    def check_crossing_index(self):
        if (self.thread_stoped()):
            return None
        num = None
        strType = -1

        if self.cfg_type == "801":
            num = [46, 36, 30, 15]
            strType = "previlege"
        if self.cfg_type == "802":
            num = [45, 34, 10]
            strType = "treasure"
        if self.cfg_type == "803":
            num = [41, 20]
            strType = "reputation"
        if not num or not strType:
            return -1
        for i in range(len(num)):
            if comparator.template_compare(f"./assets/monopoly/{strType}_crossing_{num[i]}.png", screenshot=self.screenshot):
                return i
        return -1

    def check_confirm(self):
        self.update_ui("开始检查奖励确认界面", 'debug')
        points_with_colors = [(524, 212, [255, 255, 253]), (441, 203, [255, 255, 253]), (413, 205, [255, 255, 251]),
                              (413, 209, [255, 253, 250]), (413, 209, [255, 253, 250]), (445, 209, [255, 255, 253]),
                              (435, 316, [50, 95, 114]), (520, 314, [54, 97, 114]), (414, 326, [33, 79, 105]),
                              (542, 325, [34, 84, 107])]
        if comparator.match_point_color(points_with_colors, screenshot=self.screenshot):
            self.update_ui("检查到奖励确认界面", 'debug')
            self.btn_confirm()
            return True
        return False

    def check_accept_confirm(self):
        self.update_ui("开始检查奖励入账确认界面", 'debug')
        points_with_colors = [(688, 55, [253, 251, 252]), (528, 59, [244, 243, 241]),
                              (533, 74, [233, 229, 226]), (513, 80, [198, 194, 191])]
        if comparator.match_point_color(points_with_colors, screenshot=self.screenshot):
            self.update_ui("检查到奖励入账确认界面", 'debug')
            self.btn_accept_confirm()
            return True
        return False

    def check_info_confirm(self):
        self.update_ui("开始检查信息确认界面", 'debug')
        flod = [(68, 483, [98, 97, 95]), (61, 472, [170, 165, 161]),
                (61, 493, [171, 170, 168]), (51, 482, [172, 171, 166])]
        unflod = [(72, 483, [183, 180, 175]), (57, 483, [149, 146, 141]),
                  (57, 483, [149, 146, 141]), (63, 493, [126, 128, 125])]
        check_list = [flod, unflod]
        for check in check_list:
            if comparator.match_point_color(check, screenshot=self.screenshot):
                self.update_ui("检查到信息确认界面", 'debug')
                self.btn_center_confirm()
                return True
        return False

    def check_final_confirm(self):
        self.update_ui("开始检查最终确认界面", 'debug')
        points_with_colors = [(533, 102, [168, 167, 165]), (533, 111, [168, 167, 165]),
                              (533, 121, [180, 179, 177]), (487, 106, [243, 242, 238]),
                              (487, 115, [236, 235, 233]), (441, 112, [236, 235, 233]),
                              (432, 119, [211, 210, 208])]
        if comparator.match_point_color(points_with_colors, screenshot=self.screenshot):
            self.update_ui("检查到最终确认界面", 'debug')
            return True
        return False

    def check_continue(self):
        self.update_ui("开始检查是否继续游戏", 'debug')
        coord = comparator.template_compare(f"./assets/monopoly/monopoly_continue.png",
                                            return_center_coord=True, screenshot=self.screenshot)
        if coord:
            self.update_ui("检查到继续游戏", 'debug')
            return True
        return False

    def check_evtent(self):
        self.update_ui("开始检查事件", 'debug')
        coord = comparator.template_compare(f"./assets/monopoly/btn_options.png",
                                            return_center_coord=True, screenshot=self.screenshot)
        if coord:
            self.update_ui("检查到事件", 'debug')
            x, y = coord
            offfset = 120
            engine.device.click(x + offfset, y)
            return True
        return False

    def check_end(self):
        self.update_ui("开始检查是否结束", 'debug')
        points_with_colors = [
            (486, 111, [233, 232, 228]),
            (486, 111, [233, 232, 228]),
            (486, 111, [233, 232, 228]),
            (486, 111, [233, 232, 228]),
            (159, 174, [102, 96, 82]),
            (164, 175, [53, 43, 31]),
            (442, 113, [236, 235, 233])]
        if comparator.match_point_color(points_with_colors, screenshot=self.screenshot):
            self.update_ui("检查到结算")
            return True
        return False

    def check_distance(self, screenshot):
        try:
            x, y, width, height = 708, 480, 28, 20
            currentshot = screenshot
            current_image = currentshot[y:y+height, x:x+width]
            number = self.ocr_number(current_image)
            retry = 1
            max_retry = self.cfg_check_roll_rule_time
            while not number and retry < max_retry+1:
                self.update_ui(f"检查距离失败，重试次数{retry}，最大重试次数{max_retry}")
                time.sleep(self.cfg_check_roll_rule_wait)
                currentshot = engine.device.screenshot(format='opencv')
                current_image = currentshot[y:y+height, x:x+width]
                number = self.ocr_number(current_image, retry)
                retry += 1
            return number
        except Exception as e:
            self.update_ui(f"检查距离出现异常{e}")
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
        bp3 = [865, 456]
        bp2 = [848, 456]
        bp1 = [832, 456]
        r_bp1 = screenshot[bp1[1], bp1[0]][2]  # 获取 R 通道
        r_bp2 = screenshot[bp2[1], bp2[0]][2]  # 获取 R 通道
        r_bp3 = screenshot[bp3[1], bp3[0]][2]  # 获取 R 通道
        limit = 80
        if r_bp3 > limit:
            return 3
        if r_bp2 > limit:
            return 2
        if r_bp1 > limit:
            return 1
        print(f"r_bp1:{r_bp1},r_bp2:{r_bp2},r_bp3:{r_bp3}")
        return 0

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
                        normalized_path, [(15, 86), (506, 448)], return_center_coord=True, match_threshold=self.cfg_enemy_match_threshold, screenshot=self.screenshot, pack=False)
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

    def btn_confirm(self):
        engine.device.click(480, 324)

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
