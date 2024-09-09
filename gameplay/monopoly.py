import time
import cv2
from typing import List
from engine.comparator import comparator_vee
from engine.world import world_vee
from engine.engine import engine_vee
from engine.battle import battle_vee
from utils.config_loader import cfg_monopoly_vee, reload_config
from app_data import AppData
import json


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
        self.cfg_check_roll_rule_time = 5
        self.cfg_check_roll_rule_wait = 0.2
        self.screenshot = None
        self.cfg_r801 = []
        self.cfg_r802 = []
        self.cfg_r803 = []

    def set(self):
        reload_config()
        self.cfg_ticket = int(cfg_monopoly_vee.get("ticket"))
        self.cfg_lv = int(cfg_monopoly_vee.get("lv"))
        self.cfg_type = cfg_monopoly_vee.get("type")
        self.cfg_crossing = cfg_monopoly_vee.get(f"crossing.{self.cfg_type}")
        self.cfg_auto_battle = int(cfg_monopoly_vee.get("auto_battle"))
        self.cfg_isContinue = int(cfg_monopoly_vee.get("isContinue"))
        self.cfg_check_interval = float(cfg_monopoly_vee.get("check_interval"))
        self.cfg_check_roll_dice_interval = float(cfg_monopoly_vee.get("check_roll_dice_interval"))
        self.cfg_check_roll_dice_time = int(cfg_monopoly_vee.get("check_roll_dice_time"))
        self.cfg_check_roll_rule = int(cfg_monopoly_vee.get("check_roll_rule"))
        self.cfg_check_roll_rule_time = int(cfg_monopoly_vee.get("check_roll_rule_time"))
        self.cfg_check_roll_rule_wait = float(cfg_monopoly_vee.get("check_roll_rule_wait"))
        self.cfg_r801 = cfg_monopoly_vee.get("bp.801")
        self.cfg_r802 = cfg_monopoly_vee.get("bp.802")
        self.cfg_r803 = cfg_monopoly_vee.get("bp.803")

    def thread_stoped(self) -> bool:
        return self.global_data and self.global_data.thread_stoped()

    def update_ui(self, msg: str, type=0):
        self.global_data and self.global_data.update_ui(msg, type)

    def start(self):
        count = 0
        looptime = 0
        failed = 0
        self.set()
        begin_time = time.time()
        begin_turn = begin_time
        total_duration = 0
        turn_duration = 0
        restart = 0
        reported = False
        finished = True
        isMatch = "None"
        self.update_ui(f"大霸启动!", 1)
        while not self.thread_stoped():
            try:
                self.screenshot = engine_vee.device.screenshot(format='opencv')

                isMatch = "None"
                if world_vee.in_world(self.screenshot):
                    isMatch = 'in_world'
                    self.btn_menu_monopoly()
                if self.check_continue():
                    isMatch = 'check_continue'
                    if self.cfg_isContinue == 0:
                        self.btn_not_continue()
                    else:
                        self.btn_continue()
                is_set_game_mode = self.check_set_game_mode()
                is_page_monopoly = self.check_page_monopoly()
                if is_set_game_mode:
                    self.set_game_mode()
                    self.btn_play_monopoly()
                    begin_turn = time.time()
                    finished = False
                    reported = False
                    looptime += 1

                if is_page_monopoly:
                    isMatch = 'check_play_monopoly'
                    if looptime != 0 and not reported:
                        now = time.time()
                        total_duration = (now - begin_time) / 60
                        turn_duration = (now - begin_turn) / 60
                        if not finished:
                            failed += 1
                        msg1 = f"完成{looptime}次,翻车{failed}次,重启{restart}次"
                        msg2 = f"本轮耗时{turn_duration:.2f}分钟,总耗时{total_duration:.2f}分钟"
                        self.update_ui(f"{msg1},{msg2}", 1)
                        reported = True
                    self.select_monopoly()
                    self.btn_setting_monopoly()

                in_battle = battle_vee.is_in_battle(self.screenshot)
                if in_battle:
                    isMatch = 'is_in_battle'
                if battle_vee.is_in_battle_ready():
                    isMatch = 'is_in_battle_ready'
                    if self.cfg_auto_battle == 1:
                        battle_vee.btn_auto_battle()
                    else:
                        battle_vee.btn_attack()
                if not in_battle:
                    if self.can_roll_dice():
                        isMatch = 'can_roll_dice'
                        input_bp = 0
                        if self.cfg_check_roll_rule == 1:
                            number = self.check_distance(self.screenshot)
                            input_bp = self.check_roll_rule(number)
                            max_bp = self.check_bp_number(self.screenshot)
                            self.update_ui(f"距离终点 {number}，当前BP: {max_bp}")
                            if input_bp > max_bp:
                                input_bp = max_bp
                        self.roll_dice(input_bp)
                    if world_vee.check_stage(self.screenshot):
                        isMatch = 'check_stage'
                        battle_vee.cmd_skip()
                    if self.check_evtent():
                        isMatch = 'check_evt'
                    if self.check_confirm():
                        isMatch = 'check_confirm'
                    if self.check_accept_confirm():
                        isMatch = 'check_accept_confirm'
                    if self.check_info_confirm():
                        isMatch = 'check_info_confirm'
                    if self.check_final_confirm():
                        isMatch = 'check_final_confirm'
                        self.btn_final_confirm()
                        finished = True
                    if self.check_crossing():
                        isMatch = 'check_crossing'
                if isMatch != 'None':
                    self.update_ui(f"匹配到的函数 {isMatch} ", 3)
                    count = 0
                else:
                    if count > 100:
                        self.error(f"检查{count}次0.1秒未匹配到任何执行函数，重启游戏")
                        count = 0
                        restart += 1
                        engine_vee.restart_game()
                        continue
                    self.update_ui("未匹配到任何函数", 3)
                    check_in_app = engine_vee.check_in_app()
                    if not check_in_app:
                        self.update_ui("未检测到游戏")
                        count = 0
                        engine_vee.start_app()
                    else:
                        self.btn_trim_confirm()
                        count += 1
                        self.update_ui(f"未匹配到任何函数，第{count}次", 3)
                time.sleep(self.cfg_check_interval)
            except Exception as e:
                self.update_ui(f"出现异常！{e}")

    def roll_dice(self, bp=0):
        start_point = (846, 440)
        x, y = start_point
        if bp > 0:
            offset = 58 * bp
            end_point = (x, y - offset)
            engine_vee.long_press_and_drag(start_point, end_point)
        if bp == 0:
            engine_vee.device.click(x, y)
        self.update_ui(f"投骰子, BP: {bp}")
        for i in range(self.cfg_check_roll_dice_time):
            time.sleep(self.cfg_check_roll_dice_interval)
            self.btn_trim_confirm()

    def can_roll_dice(self):
        self.update_ui("开始检查是否可以掷骰子", 3)
        if (self.thread_stoped()):
            return False
        crood_range = [(809, 428), (889, 442)]
        if comparator_vee.template_in_picture("./assets/monopoly/roll_dice.png", crood_range, True):
            self.update_ui("检测到可以掷骰子", 3)
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
            select = self.find_monopoly()
            if select:
                x, y = select
                engine_vee.device.click(x, y)
                self.update_ui("选择大富翁")
                break
            if (self.thread_stoped()):
                return
            if current_y >= end_y:
                break
            next_y = current_y + 50
            engine_vee.device.swipe(x, current_y, x, next_y, 0.1)
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
        return comparator_vee.template_in_picture(template_path, self.crood_range, True)

    def find_treasure(self):
        template_path = "./assets/monopoly/find_treasure.png"
        return comparator_vee.template_in_picture(template_path, self.crood_range, True)

    def find_previlege(self):
        template_path = "./assets/monopoly/find_previlege.png"
        return comparator_vee.template_in_picture(template_path, self.crood_range, True)

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
        engine_vee.device.click(373, 220)

    def reduce_ticket(self):
        engine_vee.device.click(243, 220)

    def add_lv(self):
        engine_vee.device.click(715, 220)

    def reduce_lv(self):
        engine_vee.device.click(588, 220)

    def turn_crossing(self, direction):
        if (self.thread_stoped()):
            return
        if direction == "left":
            engine_vee.device.click(402, 243)
        if direction == "right":
            engine_vee.device.click(558, 243)
        if direction == "up":
            engine_vee.device.click(480, 150)
        if direction == "down":
            engine_vee.device.click(480, 330)

    def check_page_monopoly(self):
        if (self.thread_stoped()):
            return False
        self.update_ui("开始检查是否在大富翁选择界面中", 3)
        p1 = [
            (150, 102, [235, 215, 188]),
            (586, 21, [139, 114, 83]),
            (471, 198, [134, 126, 107]),
            (473, 252, [139, 130, 113]),
            (473, 315, [145, 137, 118]),
            (24, 16, [231, 231, 231]),
            (472, 145, [133, 124, 107])
        ]
        ponits_with_colors = [p1]
        for i in ponits_with_colors:
            if comparator_vee.match_point_color(i, screenshot=self.screenshot):
                self.update_ui("检测到在大富翁选择界面中", 3)
                return True
        return False

    def check_set_game_mode(self):
        if (self.thread_stoped()):
            return False
        self.update_ui("开始检查是否在大富翁选择模式界面中", 3)
        p1 = [
            (393, 426, [84, 84, 84]),
            (357, 293, [130, 113, 83]),
            (351, 295, [188, 177, 157]),
            (360, 298, [23, 6, 0])
        ]
        p2 = [
            (437, 116, [235, 231, 228]),
            (466, 112, [134, 133, 131]),
            (496, 117, [224, 223, 221]),
            (518, 119, [214, 213, 211])
        ]
        ponits_with_colors = [p1, p2]

        for i in ponits_with_colors:
            if comparator_vee.match_point_color(i, screenshot=self.screenshot):
                self.update_ui("检测到在大富翁选择模式界面中", 3)
                return True
        return False

    def check_crossing(self):
        self.update_ui("开始检查大富翁路口", 3)
        if (self.thread_stoped()):
            return False
        current_crossing = self.check_crossing_index()
        if current_crossing != None and self.cfg_crossing and self.cfg_crossing[current_crossing]:
            direction = self.cfg_crossing[current_crossing]
            self.turn_crossing(direction)
            return True
        return False

    def check_crossing_index(self):
        if (self.thread_stoped()):
            return None
        num = None
        strType = None
        crood_range = [(708, 480), (750, 500)]

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
            return None
        for i in range(len(num)):
            if comparator_vee.template_in_picture(f"./assets/monopoly/{strType}_crossing_{num[i]}.png", crood_range):
                self.update_ui(f"检测到大富翁路口{i}", 0)
                return i
        return None

    def check_confirm(self):
        self.update_ui("开始检查奖励确认界面", 3)
        points_with_colors = [(524, 212, [255, 255, 253]), (441, 203, [255, 255, 253]), (413, 205, [255, 255, 251]),
                              (413, 209, [255, 253, 250]), (413, 209, [255, 253, 250]), (445, 209, [255, 255, 253])]
        if comparator_vee.match_point_color(points_with_colors, screenshot=self.screenshot):
            self.update_ui("检查到奖励确认界面", 3)
            self.btn_confirm()
            return True
        return False

    def check_accept_confirm(self):
        self.update_ui("开始检查奖励入账确认界面", 3)
        points_with_colors = [(688, 55, [253, 251, 252]), (528, 59, [244, 243, 241]),
                              (533, 74, [233, 229, 226]), (513, 80, [198, 194, 191])]
        if comparator_vee.match_point_color(points_with_colors, screenshot=self.screenshot):
            self.update_ui("检查到奖励入账确认界面", 3)
            self.btn_accept_confirm()
            return True
        return False

    def check_info_confirm(self):
        self.update_ui("开始检查信息确认界面", 3)
        flod = [(68, 483, [98, 97, 95]), (61, 472, [170, 165, 161]),
                (61, 493, [171, 170, 168]), (51, 482, [172, 171, 166])]
        unflod = [(72, 483, [183, 180, 175]), (57, 483, [149, 146, 141]),
                  (57, 483, [149, 146, 141]), (63, 493, [126, 128, 125])]
        check_list = [flod, unflod]
        for check in check_list:
            if comparator_vee.match_point_color(check, screenshot=self.screenshot):
                self.update_ui("检查到信息确认界面", 3)
                self.btn_trim_confirm()
                return True
        return False

    def check_final_confirm(self):
        self.update_ui("开始检查最终确认界面", 3)
        points_with_colors = [(533, 102, [168, 167, 165]), (533, 111, [168, 167, 165]),
                              (533, 121, [180, 179, 177]), (487, 106, [243, 242, 238]),
                              (487, 115, [236, 235, 233]), (441, 112, [236, 235, 233]),
                              (432, 119, [211, 210, 208])]
        if comparator_vee.match_point_color(points_with_colors, screenshot=self.screenshot):
            self.update_ui("检查到最终确认界面", 3)
            return True
        return False

    def check_continue(self):
        self.update_ui("开始检查是否继续游戏", 3)
        points_with_colors = [(468, 140, [90, 94, 95]), (638, 366, [34, 90, 113]),
                              (563, 365, [41, 93, 115]), (394, 363, [81, 81, 81]),
                              (327, 363, [81, 81, 81])]
        if comparator_vee.match_point_color(points_with_colors, screenshot=self.screenshot):
            self.update_ui("检查到是否继续游戏")
            return True
        return False

    def check_evtent(self):
        self.update_ui("开始检查事件", 3)
        coord = comparator_vee.template_in_picture(f"./assets/monopoly/btn_options.png", return_center_coord=True)
        if coord:
            self.update_ui("检查到事件", 3)
            x, y = coord
            offfset = 120
            engine_vee.device.click(x + offfset, y)
            return True
        return False

    def check_distance(self, screenshot):
        try:
            time.sleep(self.cfg_check_roll_rule_wait)
            number = self.ocr_number(screenshot)
            retry = 0
            max_retry = self.cfg_check_roll_rule_time
            while not number and retry < max_retry:
                self.update_ui(f"检查距离失败，重试次数{retry}，最大重试次数{max_retry}")
                time.sleep(self.cfg_check_roll_rule_wait)
                number = self.ocr_number(screenshot)
                retry += 1
            return number
        except Exception as e:
            self.update_ui(f"检查距离出现异常{e}")
            return None

    def check_roll_rule(self, number):
        if not number:
            self.update_ui("检查距离失败", 3)
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

    def ocr_number(self, screenshot):
        x, y, width, height = 708, 480, 28, 20
        cropped_image = screenshot[y:y+height, x:x+width]
        cv2.imwrite('cropped_image.png', cropped_image)
        return comparator_vee.get_num_in_image('cropped_image.png')

    def btn_confirm(self):
        engine_vee.device.click(480, 324)

    def btn_accept_confirm(self):
        engine_vee.device.click(484, 470)

    def btn_trim_confirm(self):
        engine_vee.device.click(480, 254)

    def btn_final_confirm(self):
        engine_vee.device.click(480, 410)

    def btn_menu_monopoly(self):
        engine_vee.device.click(455, 459)

    def btn_setting_monopoly(self):
        engine_vee.device.click(843, 448)

    def btn_play_monopoly(self):
        engine_vee.device.click(600, 430)
        pass

    def btn_not_continue(self):
        engine_vee.device.click(362, 362)

    def btn_continue(self):
        engine_vee.device.click(536, 362)

    def error(self, msg):
        print(msg)
        self.update_ui(msg)
