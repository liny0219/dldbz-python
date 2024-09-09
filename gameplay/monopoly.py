import time
from typing import List
from engine.comparator import comparator_vee
from engine.world import world_vee
from engine.engine import engine_vee
from engine.battle import battle_vee
from utils.config_loader import cfg_monopoly_vee, reload_config
from app_data import AppData


class Monopoly():
    def __init__(self, global_data: AppData):
        self.global_data = global_data
        self.debug = True
        self.crood_range = [(474, 116), (937, 397)]
        self.type = "801"
        self.crossing = None
        self.ticket = 0
        self.lv = 5
        self.auto_battle = 1
        self.isContinue = 1
        self.check_interval = 0.2
        self.check_roll_dice_interval = 0.2
        self.check_roll_dice_time = 2
        self.screenshot = None

    def set(self):
        reload_config()
        self.ticket = int(cfg_monopoly_vee.get("ticket"))
        self.lv = int(cfg_monopoly_vee.get("lv"))
        self.type = cfg_monopoly_vee.get("type")
        self.crossing = cfg_monopoly_vee.get(f"crossing.{self.type}")
        self.auto_battle = int(cfg_monopoly_vee.get("auto_battle"))
        self.isContinue = int(cfg_monopoly_vee.get("isContinue"))
        self.check_interval = float(cfg_monopoly_vee.get("check_interval"))
        self.check_roll_dice_interval = float(cfg_monopoly_vee.get("check_roll_dice_interval"))
        self.check_roll_dice_time = int(cfg_monopoly_vee.get("check_roll_dice_time"))

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
                    if self.isContinue == 0:
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
                        msg1 = f"完成{looptime}次，翻车{failed}次，本轮耗时{turn_duration:.2f}分钟"
                        msg2 = f"总耗时{total_duration:.2f}分钟"
                        self.update_ui(f"{msg1},{msg2} ", 1)
                        reported = True
                    self.select_monopoly()
                    self.btn_setting_monopoly()

                in_battle = battle_vee.is_in_battle(self.screenshot)
                if in_battle:
                    isMatch = 'is_in_battle'
                if battle_vee.is_in_battle_ready():
                    isMatch = 'is_in_battle_ready'
                    if self.auto_battle == 1:
                        battle_vee.btn_auto_battle()
                    else:
                        battle_vee.btn_attack()
                if not in_battle:
                    if self.can_roll_dice():
                        isMatch = 'can_roll_dice'
                        self.roll_dice()
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
                    self.update_ui(f"匹配到的函数：{isMatch} ", 3)
                    count = 0
                else:
                    if count > 100:
                        self.error(f"检查{count}次0.1秒未匹配到任何执行函数，重启游戏")
                        count = 0
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
                time.sleep(self.check_interval)
            except Exception as e:
                self.update_ui(f"出现异常！{e}")
                return

    def roll_dice(self, bp=0):
        start_point = (846, 440)
        x, y = start_point
        if bp > 0:
            offset = 58 * bp
            end_point = (x, y - offset)
            engine_vee.long_press_and_drag(start_point, end_point, 0)
        if bp == 0:
            engine_vee.device.click(x, y)
        self.update_ui("开始掷骰子")
        for i in range(self.check_roll_dice_time):
            time.sleep(self.check_roll_dice_interval)
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
        if self.type == "801":
            return self.find_previlege()
        if self.type == "802":
            return self.find_treasure()
        if self.type == "803":
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
        while self.ticket < init_ticket and not self.thread_stoped():
            self.reduce_ticket()
            init_ticket -= 1
        while self.ticket > init_ticket and not self.thread_stoped():
            self.add_ticket()
            init_ticket += 1
        while self.lv > init_lv and not self.thread_stoped():
            self.add_lv()
            init_lv += 1
        while self.lv < init_lv and not self.thread_stoped():
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
            engine_vee.device.click(400, 250)
        if direction == "right":
            engine_vee.device.click(560, 250)
        if direction == "up":
            engine_vee.device.click(480, 150)
        if direction == "down":
            engine_vee.device.click(480, 330)

    def check_page_monopoly(self):
        if (self.thread_stoped()):
            return False
        self.update_ui("开始检查是否在大富翁选择界面中", 3)
        p1 = [
            (815, 451, [49, 100, 121]),
            (838, 455, [174, 199, 219]),
            (835, 456, [62, 91, 109]),
            (851, 444, [134, 156, 167]),
            (842, 439, [102, 135, 150])
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
        if current_crossing != None and self.crossing and self.crossing[current_crossing]:
            direction = self.crossing[current_crossing]
            self.turn_crossing(direction)
            return True
        return False

    def check_crossing_index(self):
        if (self.thread_stoped()):
            return None
        num = None
        strType = None
        crood_range = [(708, 480), (750, 500)]

        if self.type == "801":
            num = [46, 36, 30, 15]
            strType = "previlege"
        if self.type == "802":
            num = [45, 34, 10]
            strType = "treasure"
        if self.type == "803":
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
