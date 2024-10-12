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
        self.end = False

    def thread_stoped(self) -> bool:
        return app_data and app_data.thread_stoped()

    def can_read(self, screenshot=None):
        try:
            screenshot = self.shot()
            coord = comparator.template_compare(
                "./assets/recollection/read_ui.png", return_center_coord=True, screenshot=screenshot)
            return coord
        except Exception as e:
            app_data.update_ui(f"can_read异常{e}")
            return None
        finally:
            del screenshot
            gc.collect()

    def on_read(self, screenshot=None):
        try:
            coord = self.can_read(screenshot)
            if coord is not None and len(coord) > 0:
                x, y = coord
                u2_device.device.click(x, y)
                return True
            return False
        except Exception as e:
            app_data.update_ui(f"on_read异常{e}")
            return False
        finally:
            del screenshot
            gc.collect()

    def on_confirm_read(self, screenshot=None):
        try:
            if screenshot is None or len(screenshot) == 0:
                screenshot = self.shot()
            coord = comparator.template_compare(
                "./assets/recollection/confirm_read_ui.png", return_center_coord=True, screenshot=screenshot)
            if coord is not None:
                x, y = coord
                u2_device.device.click(x, y)
                return True
            return False
        except Exception as e:
            app_data.update_ui(f"on_confirm_read异常{e}")
            return False
        finally:
            del screenshot
            gc.collect()

    def on_confirm_award(self, screenshot=None):
        try:
            app_data.update_ui("check-确认奖励界面", "debug")
            if screenshot is None or len(screenshot) == 0:
                screenshot = self.shot()
            coord = comparator.template_compare(
                "./assets/recollection/confirm_award_ui.png", return_center_coord=True, screenshot=screenshot)
            if coord is not None:
                app_data.update_ui("点击确认奖励界面")
                x, y = coord
                u2_device.device.click(x, y)
                return True
            return False
        except Exception as e:
            app_data.update_ui(f"on_confirm_award异常{e}")
            return False
        finally:
            del screenshot
            gc.collect()

    def on_status_close(self, screenshot=None):
        try:
            app_data.update_ui("check-关闭状态界面", "debug")
            if screenshot is None or len(screenshot) == 0:
                screenshot = self.shot()
            coord = comparator.template_compare(
                "./assets/recollection/status_close_ui.png", return_center_coord=True, screenshot=screenshot)
            if coord is not None:
                app_data.update_ui("点击关闭状态界面")
                x, y = coord
                u2_device.device.click(x, y)
                return True
            return False
        except Exception as e:
            app_data.update_ui(f"on_status_close异常{e}")
        finally:
            del screenshot
            gc.collect()

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

    def reset(self):
        cfg_recollection.reload()
        self.loop = int(cfg_recollection.get("common.loop"))

    def start(self):
        app_data.update_ui("追忆之书,启动", 'stats')
        self.reset()
        battle.reset()
        self.finish_count = 0
        self.report_count = -1
        self.start_count = 0
        self.total_time = 0
        self.flag_in_battle = False
        self.flag_finish = False
        app_data.recollection_deamon_thread = StoppableThread(target=lambda: self.daemon())
        app_data.recollection_deamon_thread.start()
        app_data.update_ui(f"守护线程启动", 'debug')
        self.run()

    def daemon(self):
        try:
            while not app_data.thread_recollection_deamon_stoped() and not self.end:
                try:
                    if not self.flag_in_battle:
                        app_data.update_ui('守护线程检查', 'debug')
                        screenshot = self.shot()
                        battle.check_finish(screenshot)
                        battle.check_confirm_quit_battle(screenshot)
                        coord = self.can_read(screenshot)
                        if coord is not None and len(coord) > 0:

                            if self.flag_finish:
                                self.end = True
                                app_data.update_ui("追忆之书已达到设定次数")
                                break
                            else:
                                u2_device.device.click(coord[0], coord[1])
                        if self.on_confirm_read(screenshot):
                            for i in range(2):
                                if app_data.thread_stoped():
                                    break
                                battle.cmd_skip(3000)
                            self.flag_in_battle = True
                            self.start_count += 1
                            self.TimeroundStart = time.time()
                        if self.on_confirm_award(screenshot):
                            self.finish_count += 1
                            self.turn_end()
                        if self.on_status_close(screenshot):
                            self.turn_end()
                        time.sleep(0.2)
                    else:
                        time.sleep(1)
                except Exception as e:
                    app_data.update_ui(f"守护线程循环异常{e}")
        except Exception as e:
            app_data.update_ui(f"守护线程异常停止{e}")

    def run(self):
        try:
            while app_data.thread and not app_data.thread_stoped() and not self.end:
                if self.flag_in_battle:
                    app_data.update_ui("开始战斗")
                    run_result = battle.run('./battle_script/recollection.txt')
                    if run_result == 1:
                        is_finish = battle.check_finish()
                        if is_finish:
                            for i in range(2):
                                if app_data.thread_stoped():
                                    break
                                battle.cmd_skip(3000)
                        self.flag_in_battle = False
                else:
                    time.sleep(0.2)

        except Exception as e:
            app_data.update_ui(f"发生错误: {e}")

    def turn_end(self):
        if self.report_count == self.start_count:
            return
        self.report_count = self.start_count
        fail_count = self.start_count - self.finish_count
        # 计算每轮时间
        current_time = time.time()
        round_time = current_time - self.TimeroundStart
        self.TimeroundStart = current_time  # 更新下一轮的开始时间
        if self.start_count == 0:
            round_time = 0

        # 计算总时间
        self.total_time = self.total_time + round_time

        msg1 = f"完成 {self.finish_count} 次, 异常: {fail_count} 次"
        msg2 = f"本次耗时: {round_time/60:.1f} 分钟,总耗时: {self.total_time/60:.1f} 分钟"
        app_data.update_ui(f"{msg1} {msg2}", "stats")

        if self.loop != 0 and self.finish_count >= self.loop:
            app_data.update_ui(
                f"追忆之书已达到设定次数: {self.loop}\n"
                f"总运行时间: {self.total_time/60:.1f} 分钟")
            return True
        return False
