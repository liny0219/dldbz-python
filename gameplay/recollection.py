from __future__ import annotations
import time
from app_data import AppData
from engine.engine import engine
from engine.battle import battle
from utils.config_loader import cfg_recollection
from engine.comparator import comparator
from utils.wait import wait_until


class Recollection:
    def __init__(self, app_data: AppData):
        self.loop = int(cfg_recollection.get("common.loop"))
        self.app_data = app_data
        self.Timestartup = time.time()  # 程序启动时间
        self.TimeroundStart = time.time()  # 每轮开始时间

    def thread_stoped(self) -> bool:
        return self.app_data and self.app_data.thread_stoped()

    def update_ui(self, msg: str, type='info'):
        self.app_data and self.app_data.update_ui(msg, type)

    def on_read(self):
        ui_read = cfg_recollection.get("check.check_read_ui_refs")
        in_read = comparator.template_in_picture(
            ui_read, return_center_coord=True)
        if in_read:
            engine.press(in_read)
            return True

    def on_confirm_read(self):
        ui_confirm_read = cfg_recollection.get(
            "check.check_confirm_read_ui_refs")
        in_confirm_read = comparator.template_in_picture(
            ui_confirm_read, return_center_coord=True)
        if in_confirm_read:
            engine.press(in_confirm_read)
            return True

    def on_confirm_award(self):
        ui_confirm_award = cfg_recollection.get(
            "check.check_confirm_award_ui_refs")
        in_confirm_award = comparator.template_in_picture(
            ui_confirm_award, return_center_coord=True)
        if in_confirm_award:
            engine.press(in_confirm_award)
            return True
        return False

    def on_status_close(self):
        ui_status_close = cfg_recollection.get(
            "check.check_status_close_ui_refs")
        in_status_close = comparator.template_in_picture(
            ui_status_close, return_center_coord=True)
        if in_status_close:
            engine.press(in_status_close)
            return True
        return False

    def start(self):
        self.loopNum = 0
        self.run()

    def run(self):
        debug = False
        # debug = True
        try:
            if not debug:
                self.loop = int(cfg_recollection.get("common.loop"))

                self.update_ui("开始追忆之旅...")

                # 等待读取并确认读取
                self.update_ui(f"开始阅读")
                runState = wait_until(self.on_read,  operate_funcs=[self.on_read], thread=self.app_data.thread,
                                      timeout=10, check_interval=1)
                if self.thread_stoped():
                    self.update_ui(f"线程已停止")
                    return
                if not runState:
                    self.update_ui("开始阅读，中止", )
                    return

                self.update_ui(f"确认阅读内容")
                runState = wait_until(self.on_confirm_read, operate_funcs=[self.on_confirm_read],  thread=self.app_data.thread,
                                      timeout=10, check_interval=1)
                if self.thread_stoped():
                    self.update_ui(f"线程已停止")
                    return
                if not runState:
                    self.update_ui("确认失败，中止")
                    return

                self.update_ui("跳过开场动画")
                btnSkipTimeout = cfg_recollection.get("common.btn_skip_timeout")
                btnSkip = cfg_recollection.get("coord.btn_skip")
                engine.press(btnSkip, btnSkipTimeout)

                if not runState:
                    self.update_ui("跳过动画失败，中止")
                    return

            self.update_ui("开始战斗")
            battle.run('./battle_script/recollection.txt')
            self.finish()
        except Exception as e:
            self.update_ui(f"发生错误: {e}")

    def finish(self):
        self.loopNum += 1
        # 计算每轮时间
        current_time = time.time()
        round_time = current_time - self.TimeroundStart
        self.TimeroundStart = current_time  # 更新下一轮的开始时间

        # 计算总时间
        total_time = current_time - self.Timestartup

        # 更新 UI，时间格式为分钟
        self.update_ui(
            f"追忆之书完成次数: {self.loopNum}\n"
            f"本次时间: {round_time/60:.2f} 分钟\n"
            f"总运行时间: {total_time/60:.2f} 分钟",
        )
        self.update_ui(
            f"追忆之书完成次数: {self.loopNum} 次 | 本次耗时: {round_time/60:.2f} 分钟 | 总耗时: {total_time/60:.2f} 分钟", "stats"
        )

        # 等待确认奖励
        runStateAward = wait_until(self.on_confirm_award, time_out_operate_funcs=[self.on_confirm_award], thread=self.app_data.thread,
                                   timeout=20)
        if self.thread_stoped():
            self.update_ui(f"线程已停止")
            return
        # 输出奖励确认结果
        if not runStateAward:
            self.update_ui(f"奖励确认失败")
            return
        runStateStatus = wait_until(self.on_status_close, time_out_operate_funcs=[self.on_status_close], thread=self.app_data.thread,
                                    timeout=20)
        # 输出状态关闭结果
        if not runStateStatus:
            self.update_ui(f"状态关闭失败: {self.loop}")
            return
        if self.loop != 0 and self.loopNum >= self.loop:
            self.update_ui(
                f"追忆之书已达到设定次数: {self.loop}\n"
                f"总运行时间: {total_time/60:.2f} 分钟")
            self.update_ui(f"已完成 {self.loopNum} 次 | 本次耗时: {round_time/60:.2f} 分钟 | 总耗时: {total_time/60:.2f} 分钟", "stats"
                           )
            return
        self.run()
