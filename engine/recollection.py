import time
import cv2
from engine.battle_DSL import BattleDSL
from engine.battle_hook import BattleHook
from engine.device_controller import DeviceController
from engine.battle_vee import Battle
from engine.comparator import Comparator
from utils.config_loader import cfg_recollection
from engine.player import Player
from utils.wait import wait_until


class recollection:
    def __init__(self, updateUI, device_ip="127.0.0.1:5555", team='TBD'):
        self.updateUI = updateUI

        self.loop = int(cfg_recollection.get("common.loop"))
        self.controller = DeviceController(device_ip)
        self.comparator = Comparator(self.controller)
        self.player = Player(self.controller, self.comparator, team)
        self.battle_dsl = BattleDSL(updateUI)
        self.battle_hook = BattleHook()
        self.Timestartup = time.time()  # 程序启动时间
        self.TimeroundStart = time.time()  # 每轮开始时间
        self.battle = Battle(self.player, '测试', updateUI)

        # 显示程序启动时间
        startup_time_str = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(self.Timestartup))
        self.updateUI(
            f"程序启动时间: {startup_time_str}\n旅途即将开始...",
            stats="大霸启动！！"
        )

    def setThread(self, thread):
        self.thread = thread
        self.battle.setThread(thread)

    def log_time(self, start_time, action_description):
        elapsed_time = time.time() - start_time
        self.updateUI(f"{action_description} 完成，耗时：{elapsed_time:.2f} 秒")

    def on_read(self):
        ui_read = cfg_recollection.get("check.check_read_ui_refs")
        in_read = self.comparator.template_in_picture(
            ui_read, return_center_coord=True)
        if in_read:
            self.controller.press(in_read)
            return True

    def on_confirm_read(self):
        ui_confirm_read = cfg_recollection.get(
            "check.check_confirm_read_ui_refs")
        in_confirm_read = self.comparator.template_in_picture(
            ui_confirm_read, return_center_coord=True)
        if in_confirm_read:
            self.controller.press(in_confirm_read)
            return True

    def on_confirm_award(self):
        ui_confirm_award = cfg_recollection.get(
            "check.check_confirm_award_ui_refs")
        in_confirm_award = self.comparator.template_in_picture(
            ui_confirm_award, return_center_coord=True)
        if in_confirm_award:
            self.controller.press(in_confirm_award)
            print(f"on_confirm_award in_confirm_award True")
            return True
        print(f"on_confirm_award in_confirm_award False")
        return False

    def on_status_close(self):
        ui_status_close = cfg_recollection.get(
            "check.check_status_close_ui_refs")
        in_status_close = self.comparator.template_in_picture(
            ui_status_close, return_center_coord=True)
        if in_status_close:
            self.controller.press(in_status_close)
            print(f"on_status_close in_status_close True")
            return True
        print(f"on_status_close in_status_close True")
        return False

    def start(self):
        self.loopNum = 0
        self.run()

    def run(self):
        try:
            self.loop = int(cfg_recollection.get("common.loop"))

            self.updateUI("开始旅途...")
            start_time = time.time()

            # 等待读取并确认读取
            self.updateUI("正在读取旅途内容...")
            runState = wait_until(self.on_read,  operate_funcs=[self.on_read], thread=self.thread,
                                  timeout=10, check_interval=1)
            self.log_time(start_time, "读取旅途内容")
            if not runState:
                self.updateUI("读取失败，旅途中止。", stats="旅途中断，请重试。")
                return

            self.updateUI("确认读取内容...")
            start_time = time.time()
            runState = wait_until(self.on_confirm_read, operate_funcs=[self.on_confirm_read],  thread=self.thread,
                                  timeout=10, check_interval=1)
            self.log_time(start_time, "确认读取内容")
            if not runState:
                self.updateUI("确认失败，旅途中止。", stats="确认失败，请检查。")
                return

            self.updateUI("跳过开场动画...")
            start_time = time.time()
            btnSkipTimeout = cfg_recollection.get("common.btn_skip_timeout")
            btnSkip = cfg_recollection.get("coord.btn_skip")
            self.controller.press(btnSkip, btnSkipTimeout)
            self.log_time(start_time, "跳过开场动画")

            if not runState:
                self.updateUI("跳过动画失败，旅途中止。", stats="跳过动画失败，请重试。")
                return

            self.updateUI("开始战斗...")
            start_time = time.time()
            self.battle.reset()
            self.battle_dsl.run_script('./battle_script/recollection.txt')
            self.finish()
        except Exception as e:
            self.updateUI(f"发生错误：{e}", stats="发生错误，请检查。")

    def finish(self):
        self.loopNum += 1
        # 计算每轮时间
        current_time = time.time()
        round_time = current_time - self.TimeroundStart
        self.TimeroundStart = current_time  # 更新下一轮的开始时间

        # 计算总时间
        total_time = current_time - self.Timestartup

        # 获取当前时间的字符串表示
        current_time_str = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(current_time))

        # 更新 UI，时间格式为分钟
        self.updateUI(
            f"当前时间: {current_time_str}\n"
            f"追忆之书旅途完成，当前次数：{self.loopNum}\n"
            f"本次旅途时间：{round_time/60:.2f} 分钟\n"
            f"总运行时间：{total_time/60:.2f} 分钟",
            stats=f"已完成 {self.loopNum} 次旅途 | 本次耗时：{round_time/60:.2f} 分钟 | 总耗时：{total_time/60:.2f} 分钟"
        )

        # 等待确认奖励
        runStateAward = wait_until(self.on_confirm_award, time_out_operate_funcs=[self.on_confirm_award], thread=self.thread,
                                   timeout=20)
        if self.thread.stopped():
            self.updateUI(f"休息一下\n")
            return
        # 输出奖励确认结果
        if not runStateAward:
            self.updateUI(f"奖励确认失败\n")
            return
        runStateStatus = wait_until(self.on_status_close, time_out_operate_funcs=[self.on_status_close], thread=self.thread,
                                    timeout=20)
        # 输出状态关闭结果
        if not runStateStatus:
            self.updateUI(f"状态关闭失败：{self.loop}\n")
            return
        if self.loop != 0 and self.loopNum >= self.loop:
            # 旅途完成，已达到设定次数 展示loop与loopNum 更新UI
            self.updateUI(
                f"追忆之书旅途完成，已达到设定次数：{self.loop}\n"
                f"总运行时间：{total_time/60:.2f} 分钟",
                stats=f"已完成 {self.loopNum} 次旅途 | 本次耗时：{round_time/60:.2f} 分钟 | 总耗时：{total_time/60:.2f} 分钟"
            )
            return
        self.run()

    def shot(self):
        self.comparator._cropped_screenshot(
            [462, 290], [498, 312], convert_gray=False, save_path='./refs/recollection/status_close_ui.png')
