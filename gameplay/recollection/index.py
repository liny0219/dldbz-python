from __future__ import annotations
import gc
import time
from app_data import app_data
from engine.u2_device import u2_device
from engine.battle import battle
from utils.config_loader import cfg_recollection
from engine.comparator import comparator
from utils.stoppable_thread import StoppableThread


class Recollection:
    def __init__(self):
        self.loop = int(cfg_recollection.get("common.loop"))
        self.Timestartup = time.time()  # 程序启动时间
        self.TimeroundStart = time.time()  # 每轮开始时间
        self.screenshot = None

    def thread_stoped(self) -> bool:
        return app_data and app_data.thread_stoped()

    def on_read(self):
        try:
            if self.screenshot is None or len(self.screenshot) == 0:
                return False
            coord = comparator.template_compare(
                "./assets/recollection/read_ui.png", return_center_coord=True, screenshot=self.screenshot)
            if coord is not None:
                x, y = coord
                u2_device.device.click(x, y)
                return True
            return False
        except Exception as e:
            app_data.update_ui(f"on_read异常{e}")
            return False

    def on_confirm_read(self):
        try:
            if self.screenshot is None or len(self.screenshot) == 0:
                return False
            coord = comparator.template_compare(
                "./assets/recollection/confirm_read_ui.png", return_center_coord=True, screenshot=self.screenshot)
            if coord is not None:
                x, y = coord
                u2_device.device.click(x, y)
                return True
            return False
        except Exception as e:
            app_data.update_ui(f"on_confirm_read异常{e}")
            return False

    def on_confirm_award(self):
        try:
            if self.screenshot is None or len(self.screenshot) == 0:
                return False
            coord = comparator.template_compare(
                "./assets/recollection/confirm_award_ui.png", return_center_coord=True, screenshot=self.screenshot)
            if coord is not None:
                x, y = coord
                u2_device.device.click(x, y)
                return True
            return False
        except Exception as e:
            app_data.update_ui(f"on_confirm_award异常{e}")
            return False

    def on_status_close(self):
        try:
            if self.screenshot is None or len(self.screenshot) == 0:
                return False
            coord = comparator.template_compare(
                "./assets/recollection/status_close_ui.png", return_center_coord=True, screenshot=self.screenshot)
            if coord is not None:
                x, y = coord
                u2_device.device.click(x, y)
                return True
            return False
        except Exception as e:
            app_data.update_ui(f"on_status_close异常{e}")

    def on_skip(self):
        try:
            app_data.update_ui("跳过开场动画")
            btnSkipTimeout = int(cfg_recollection.get("common.btn_skip_timeout"))
            u2_device.device.long_click(700, 515, btnSkipTimeout)
        except Exception as e:
            app_data.update_ui(f"on_skip异常{e}")

    def shot(self):
        try:
            app_data.update_ui("-----------开始截图", 'debug')
            if self.screenshot is not None:
                del self.screenshot
                self.screenshot = None
                gc.collect()
            self.screenshot = u2_device.device.screenshot(format='opencv')
            app_data.update_ui("-----------截图完成", 'debug')
            return self.screenshot
        except Exception as e:
            app_data.update_ui(f"截图异常{e}")
            return None

    def start(self):
        app_data.update_ui("追忆之书,启动", 'stats')
        self.loop = int(cfg_recollection.get("common.loop"))
        self.finish_count = 0
        self.fail_count = 0
        self.flag_in_battle = False
        self.flag_finish = False
        app_data.recollection_deamon_thread = StoppableThread(target=lambda: self.daemon())
        app_data.recollection_deamon_thread.start()
        app_data.update_ui(f"守护线程启动", 'debug')
        battle.reset()
        battle.check_finish()
        self.run()

    def daemon(self):
        try:
            max_duration = 180
            dt_start = time.time()
            while not app_data.thread_recollection_deamon_stoped():
                try:
                    if not self.flag_in_battle:
                        duration = time.time() - dt_start
                        if duration > max_duration:
                            battle.check_finish()
                            dt_start = time.time()
                        app_data.update_ui('守护线程检查', 'debug')
                        self.shot()
                        self.on_read()
                        if self.on_confirm_read():
                            battle.cmd_skip(8000)
                            self.flag_in_battle = True
                        self.on_confirm_award()
                        self.on_status_close()
                    else:
                        dt_start = time.time()
                except Exception as e:
                    app_data.update_ui(f"守护线程循环异常{e}")
                time.sleep(0.5)
        except Exception as e:
            app_data.update_ui(f"守护线程异常停止{e}")

    def run(self):
        try:
            while app_data.thread and not app_data.thread_stoped():
                if self.flag_in_battle:
                    app_data.update_ui("开始战斗")
                    battle.run('./battle_script/recollection.txt')
                    is_finish = battle.check_finish()
                    self.turn_end(is_finish)
                    if not is_finish:
                        self.flag_finish = False
                    else:
                        battle.cmd_skip(8000)
                        self.flag_finish = True
                    self.flag_in_battle = False
                else:
                    time.sleep(0.2)

        except Exception as e:
            app_data.update_ui(f"发生错误: {e}")

    def turn_end(self, is_finish=False):
        if is_finish:
            self.finish_count += 1
        else:
            self.fail_count += 1
        # 计算每轮时间
        current_time = time.time()
        round_time = current_time - self.TimeroundStart
        self.TimeroundStart = current_time  # 更新下一轮的开始时间

        # 计算总时间
        total_time = current_time - self.Timestartup

        msg1 = f"完成 {self.finish_count} 次, 异常: {self.fail_count} 次"
        msg2 = f"本次耗时: {round_time/60:.1f} 分钟,总耗时: {total_time/60:.1f} 分钟"
        app_data.update_ui(f"{msg1} {msg2}", "stats")

        if self.loop != 0 and self.finish_count >= self.loop:
            app_data.update_ui(
                f"追忆之书已达到设定次数: {self.loop}\n"
                f"总运行时间: {total_time/60:.1f} 分钟")
