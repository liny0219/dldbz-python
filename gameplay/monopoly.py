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

    def set(self):
        reload_config()
        self.ticket = int(cfg_monopoly_vee.get("ticket"))
        self.lv = int(cfg_monopoly_vee.get("lv"))
        self.type = cfg_monopoly_vee.get("type")
        self.crossing = cfg_monopoly_vee.get(f"crossing.{self.type}")
        self.auto_battle = int(cfg_monopoly_vee.get("auto_battle"))

    def thread_stoped(self) -> bool:
        return self.global_data and self.global_data.thread_stoped()

    def update_ui(self, msg: str, type=0):
        self.global_data and self.global_data.update_ui(msg, type)

    def start(self):
        count = 0
        looptime = 0
        self.set()
        starttime = time.time()
        while not self.thread_stoped():
            isMatch = False
            if world_vee.in_world():
                isMatch = 'in_world'
                self.btn_menu_monopoly()
            if self.check_continue():
                isMatch = 'check_continue'
                self.btn_not_continue()
            if self.check_page_monopoly():
                isMatch = 'check_play_monopoly'
                self.select_monopoly()
                self.btn_setting_monopoly()
            if self.check_set_game_mode():
                self.set_game_mode()
                self.btn_play_monopoly()
                turn_start = time.time()
            in_battle = battle_vee.is_in_battle()
            if in_battle:
                isMatch = 'is_in_battle'
            if battle_vee.is_in_battle_ready():
                isMatch = 'is_in_battle_ready'
                if self.auto_battle == 1:
                    battle_vee.btn_auto_battle()
                else:
                    battle_vee.btn_attack()
            if not in_battle:
                if world_vee.check_stage():
                    isMatch = 'check_stage'
                    battle_vee.cmd_skip()
                if self.can_roll_dice():
                    isMatch = 'can_roll_dice'
                    self.roll_dice()
                if self.check_crossing():
                    isMatch = 'check_crossing'
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
                    looptime += 1
                    endtime = time.time()

                    # 计算耗时并将其转换为分钟，保留两位小数
                    elapsed_time_in_minutes = (endtime - starttime) / 60
                    turn_duration = (endtime - turn_start) / 60
                    self.log(f"完成第{looptime}次，本轮耗时{turn_duration:.2f}分钟, 总挂机{elapsed_time_in_minutes:.2f}", 1)

                if self.check_page_monopoly():
                    isMatch = 'check_play_monopoly'
                if self.check_set_game_mode():
                    isMatch = 'check_set_game_mode'

            if not isMatch:
                self.log("未匹配到任何函数")
                check_in_app = engine_vee.check_in_app()
                if not check_in_app:
                    self.log("未检测到游戏", 0)
                    engine_vee.start_app()
                else:
                    count += 1
                    self.btn_trim_confirm()
            if count > 50:
                self.error("未能进入游戏", 0)
                engine_vee.restart_game()
                return
            else:
                self.log(f"匹配到的函数：{isMatch}")
                count = 0
            time.sleep(0.1)

    def roll_dice(self, bp=0):
        start_point = (846, 440)
        x, y = start_point
        if bp > 0:
            offset = 58 * bp
            end_point = (x, y - offset)
            engine_vee.long_press_and_drag(start_point, end_point, 0)
        if bp == 0:
            engine_vee.device.click(x, y)
        self.log("开始掷骰子", 0)
        time.sleep(0.5)
        self.btn_trim_confirm()

    def can_roll_dice(self):
        self.log("开始检查是否可以掷骰子")
        if (self.thread_stoped()):
            return False
        crood_range = [(809, 428), (889, 442)]
        if comparator_vee.template_in_picture("./assets/monopoly/roll_dice.png", crood_range, True):
            self.log("检测到可以掷骰子")
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
                self.log("选择大富翁", 0)
                break
            if (self.thread_stoped()):
                return
            if current_y >= end_y:
                break
            next_y = current_y + 50
            engine_vee.device.swipe(x, current_y, x, next_y, 0.1)
            current_y = next_y
        time.sleep(1)

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
        self.log("开始检查是否在大富翁选择界面中")
        ponits_with_colors = [
            (815, 451, [49, 100, 121]),
            (838, 455, [174, 199, 219]),
            (835, 456, [62, 91, 109]),
            (851, 444, [134, 156, 167]),
            (842, 439, [102, 135, 150])
        ]
        if comparator_vee.match_point_color(ponits_with_colors):
            self.log("检测到在大富翁选择界面中")
            return True
        else:
            return False

    def check_set_game_mode(self):
        if (self.thread_stoped()):
            return False
        self.log("开始检查是否在大富翁选择模式界面中")
        ponits_with_colors = [
            (393, 426, [84, 84, 84]),
            (357, 293, [130, 113, 83]),
            (351, 295, [188, 177, 157]),
            (360, 298, [23, 6, 0])
        ]
        if comparator_vee.match_point_color(ponits_with_colors):
            self.log("检测到在大富翁选择模式界面中")
            return True
        else:
            return False

    def check_crossing(self):
        self.log("开始检查大富翁路口")
        if (self.thread_stoped()):
            return False
        current_crossing = self.check_crossing_80()
        if current_crossing != None and self.crossing and self.crossing[current_crossing]:
            direction = self.crossing[current_crossing]
            self.turn_crossing(direction)
            return True
        return False

    def check_crossing_80(self):
        self.log("开始检查大富翁权利路口")
        if (self.thread_stoped()):
            return None
        num = None
        strType = None
        crood_range = [(708, 480), (750, 500)]

        if self.type == "801":
            num = [46, 36, 30, 15]
            strType = "previlege"
        if self.type == "802":
            num = []
            strType = "treasure"
        if self.type == "803":
            num = []
            strType = "reputation"
        if not num or not strType:
            return None
        for i in range(len(num)):
            if comparator_vee.template_in_picture(f"./assets/monopoly/{strType}_crossing_{num[i]}.png", crood_range):
                self.log(f"检测到大富翁权利路口{i}", 0)
                return i
        return None

    def check_confirm(self):
        self.log("开始检查奖励确认界面")
        points_with_colors = [(524, 212, [255, 255, 253]), (441, 203, [255, 255, 253]), (413, 205, [255, 255, 251]),
                              (413, 209, [255, 253, 250]), (413, 209, [255, 253, 250]), (445, 209, [255, 255, 253])]
        if comparator_vee.match_point_color(points_with_colors):
            self.log("检查到奖励确认界面")
            self.btn_confirm()
            return True
        return False

    def check_accept_confirm(self):
        self.log("开始检查奖励入账确认界面")
        points_with_colors = [(688, 55, [253, 251, 252]), (528, 59, [244, 243, 241]),
                              (533, 74, [233, 229, 226]), (513, 80, [198, 194, 191])]
        if comparator_vee.match_point_color(points_with_colors):
            self.log("检查到奖励入账确认界面")
            self.btn_accept_confirm()
            return True
        return False

    def check_info_confirm(self):
        self.log("开始检查信息确认界面")
        flod = [(68, 483, [98, 97, 95]), (61, 472, [170, 165, 161]),
                (61, 493, [171, 170, 168]), (51, 482, [172, 171, 166])]
        unflod = [(72, 483, [183, 180, 175]), (57, 483, [149, 146, 141]),
                  (57, 483, [149, 146, 141]), (63, 493, [126, 128, 125])]
        check_list = [flod, unflod]
        for check in check_list:
            if comparator_vee.match_point_color(check):
                self.log("检查到信息确认界面")
                self.btn_trim_confirm()
                return True
        return False

    def check_final_confirm(self):
        self.log("开始检查最终确认界面")
        points_with_colors = [(533, 102, [168, 167, 165]), (533, 111, [168, 167, 165]),
                              (533, 121, [180, 179, 177]), (487, 106, [243, 242, 238]),
                              (487, 115, [236, 235, 233]), (441, 112, [236, 235, 233]),
                              (432, 119, [211, 210, 208])]
        if comparator_vee.match_point_color(points_with_colors):
            self.log("检查到最终确认界面")
            self.btn_final_confirm()
            return True
        return False

    def check_continue(self):
        self.log("开始检查是否继续游戏")
        points_with_colors = [(468, 140, [90, 94, 95]), (638, 366, [34, 90, 113]),
                              (563, 365, [41, 93, 115]), (394, 363, [81, 81, 81]),
                              (327, 363, [81, 81, 81])]
        if comparator_vee.match_point_color(points_with_colors):
            self.log("检查到是否继续游戏", 0)
            self.btn_final_confirm()
            return True
        return False

    def check_evtent(self):
        self.log("开始检查事件")
        coord = comparator_vee.template_in_picture(f"./assets/monopoly/btn_options.png", return_center_coord=True)
        if coord:
            self.log("检查到事件")
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

    def log(self, msg, type=3):
        if self.debug:
            print(msg)
        if type == 3:
            return
        self.update_ui(msg, type)

    def error(self, msg):
        print(msg)
        self.update_ui(msg)
