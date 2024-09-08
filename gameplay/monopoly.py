import time
from engine.comparator import comparator_vee
from engine.world import world_vee
from engine.engine import engine_vee
from utils.config_loader import cfg_monopoly_vee, reload_config
from app_data import AppData


class Monopoly():
    def __init__(self, global_data: AppData):
        self.global_data = global_data
        self.crood_range = [(474, 116), (937, 397)]
        self.ticket = 0
        self.lv = 5

    def set(self):
        reload_config()
        self.ticket = int(cfg_monopoly_vee.get("ticket"))
        self.lv = int(cfg_monopoly_vee.get("lv"))

    def thread_stoped(self) -> bool:
        return self.global_data and self.global_data.thread_stoped()

    def update_ui(self, msg: str):
        self.global_data and self.global_data.update_ui(msg)

    def start(self):
        self.set()
        looptime = 0
        engine_vee.check_in_app()  # 检查是否在游戏中，不在则启动游戏
        # 检查是否进入了游戏的世界，可以定义 in_world 函数来检查特定的界面元素是否存在
        is_in_world = world_vee.in_world()
        is_play_monopoly = self.is_play_monopoly()
        while not is_in_world and not is_play_monopoly and looptime < 100:
            if (self.thread_stoped()):
                return
            world_vee.click_btn_close()
            # 可能的界面操作，确保界面响应
            engine_vee.device.click(362, 362)  # 大富翁选择不继续游戏
            looptime += 1
            time.sleep(1)  # 等待一秒钟
            is_in_world = world_vee.in_world()
            is_play_monopoly = self.is_play_monopoly()

        if looptime == 100:
            engine_vee.restart_game()  # 重新启动游戏的函数需要定义
        self.update_ui("进入游戏")

        if is_in_world:
            engine_vee.device.click(455, 459)
        if not is_play_monopoly:
            self.log("未进入大富翁游戏")
            return
        self.select_monopoly()

    def is_play_monopoly(self):
        if (self.thread_stoped()):
            return False
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
            self.log("检测到不在大富翁选择界面中")

    def is_set_game_mode(self):
        if (self.thread_stoped()):
            return False
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
            self.log("检测到不在大富翁选择模式界面中")

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
                self.log("选择大富翁")
                break
            if (self.thread_stoped()):
                return
            if current_y >= end_y:
                break
            next_y = current_y + 50
            engine_vee.device.swipe(x, current_y, x, next_y, 0.5)
            current_y = next_y
        time.sleep(1)
        engine_vee.device.click(843, 448)
        time.sleep(1)
        if not self.is_set_game_mode():
            self.error("未进入大富翁游戏模式")
        self.select_game_mode()

    def find_monopoly(self):
        return self.find_previlege()

    def find_reputation(self):
        template_path = "./assets/monopoly/find_reputation.png"
        return comparator_vee.template_in_picture(template_path, self.crood_range[0], self.crood_range[1], True)

    def find_treasure(self):
        template_path = "./assets/monopoly/find_treasure.png"
        return comparator_vee.template_in_picture(template_path, self.crood_range[0], self.crood_range[1], True)

    def find_previlege(self):
        template_path = "./assets/monopoly/find_previlege.png"
        return comparator_vee.template_in_picture(template_path, self.crood_range[0], self.crood_range[1], True)

    def select_game_mode(self):
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

    def log(self, msg):
        print(msg)
        self.update_ui(msg)

    def error(self, msg):
        print(msg)
        self.update_ui(msg)
