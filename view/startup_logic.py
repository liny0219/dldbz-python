from __future__ import annotations
import datetime
from datetime import datetime, timedelta
import os
import sys
import tkinter as tk
import tkinter.messagebox
from engine.battle import battle
from gameplay.ads.index import Ads
from gameplay.monopoly.index import Monopoly
from gameplay.recollection.index import Recollection
from gameplay.stationary.index import Stationary
from tool_get_coord import GetCoord
from app_data import AppData
from utils.stoppable_thread import StoppableThread
from engine.u2_device import u2_device
from engine.world import world
from engine.comparator import comparator
from utils.config_loader import cfg_startup, update_json_config
import tkinter as tk

path_cfg_statrup = 'config/startup.txt'
path_cfg_stationary = 'config/stationary.txt'
path_cfg_monopoly = 'config/monopoly.txt'


class StartupLogic:
    def __init__(self, app: tk.Tk):
        self.app_data = AppData()
        self.app_data.update_ui = self.update_ui
        self.app = app
        self.stats_label = None
        self.message_text = None
        self.debug = cfg_startup.get('debug')
        self.inited = False
        self.is_busy = False
        self.log_path = 'log'
        self.log_basename = 'log/log'
        self.log_file = None
        self.last_update_time = datetime.now()
        self.monopoly = None
        self.log_update_count_max = 10
        self.log_update_data = []
        self.log_update_data_debug = []

    def init_engine_thread(self):
        u2_device.set_config()

        if self.inited:
            return
        try:
            u2_device.set()
            battle.set()
            if not u2_device.connect():
                self.update_ui("连接设备失败，请检查设备连接！")
                return
            try:
                comparator.init_ocr()
                self.update_ui("初始化OCR成功", 0)
            except Exception as e:
                self.update_ui(f"初始化OCR失败: {e}")
                print(f"初始化OCR失败: {e}")
            self.update_ui("初始化引擎成功", 0)
            self.inited = True
        except Exception as e:
            self.update_ui(f"初始化引擎失败: {e}")
        finally:
            self.is_busy = False  # 重置忙碌状态

    def init_engine(self):
        if self.inited:
            return
        if self.is_busy:
            return
        self.is_busy = True
        self.update_ui("正在初始化...")

        # 创建线程执行初始化操作
        thread = StoppableThread(target=self.init_engine_thread)
        thread.start()
        thread.join()

    def set_stats_label(self, stats_label):
        self.stats_label = stats_label

    def set_message_text(self, message_text):
        self.message_text = message_text

    def on_close(self):
        self.update_ui("正在关闭程序，请稍等...")
        if self.app_data.thread:
            self.app_data.thread.stop()
        self.on_stop()
        self.app.quit()
        self.app.destroy()
        sys.exit(0)

    def on_stationary(self):
        if self.app_data.thread is not None and self.app_data.thread.is_alive():
            self.update_ui("已启动原地刷怪，不要重复点击哦！")
            return
        self.app_data.thread = StoppableThread(target=self._evt_run_stationary)
        self.app_data.thread.start()

    def on_monopoly(self):
        if self.app_data.thread is not None and self.app_data.thread.is_alive():
            self.update_ui("已启动游戏盘，不要重复点击哦！")
            return
        self.app_data.thread = StoppableThread(target=self._evt_monopoly)
        self.app_data.thread.start()

    def on_ads(self):
        if self.app_data.thread is not None and self.app_data.thread.is_alive():
            self.update_ui("已启动广告，不要重复点击哦！")
            return
        self.app_data.thread = StoppableThread(target=self._evt_ads)
        self.app_data.thread.start()

    def on_recollection(self):
        if self.app_data.thread is not None and self.app_data.thread.is_alive():
            self.update_ui("已启动追忆之书，不要重复点击哦！")
            return
        self.app_data.thread = StoppableThread(target=self._evt_recollection)
        self.app_data.thread.start()

    def on_stop(self):
        self.update_ui("休息一下，停止当前操作...")
        if self.app_data.thread is not None:
            self.app_data.thread.stop()
        if self.app_data.monopoly_deamon_thread is not None:
            self.app_data.monopoly_deamon_thread.stop()
        if self.app_data.recollection_deamon_thread is not None:
            self.app_data.recollection_deamon_thread.stop()
        u2_device.adb_disconnect(cfg_startup.get('adb_port'))
        self.write_to_file(self.log_file)

    def update_ui(self, msg, type='info'):
        if not self.message_text:
            return
        if self.debug == 1:
            print(msg)
        # 展示时间到毫秒
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %f")[:-3]
        message = f"[{current_time}] {msg}\n"
        print(message)
        self.log_update_data_debug.append(message)
        if len(self.log_update_data_debug) >= self.log_update_count_max*10:
            self.write_to_file(self.log_file)
        if type == 'debug' and self.debug == 0:
            return
        self.log_update_data.append(message)
        # 如果是type=1，更新统计信息
        if type == 'stats':
            self.stats_label.config(text=msg)

        if len(self.log_update_data) >= self.log_update_count_max:
            self.write_to_file()
        # 允许修改文本框内容
        self.message_text.config(state=tk.NORMAL)

        # 检查消息行数，超过200条时删除最早的消息
        num_lines = int(self.message_text.index('end-1c').split('.')[0])  # 获取当前行数
        if num_lines > 200:
            self.message_text.delete(1.0, 2.0)  # 删除第一行

        # 插入新的消息
        self.message_text.insert(tk.END, message)
        # 禁用编辑并滚动到底部
        self.message_text.config(state=tk.DISABLED)
        self.message_text.see(tk.END)

    def _generate_log_filename(self, log_file_base):
        """根据当前时间生成日志文件名"""
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
        return f"{log_file_base}_{current_time}.txt"

    def write_to_file(self, file_path=None):

        if not self.log_file:
            self.log_file = self._generate_log_filename(self.log_basename)
            self.last_update_time = datetime.now()

        if datetime.now() - self.last_update_time >= timedelta(minutes=5):
            self.log_file = self._generate_log_filename(self.log_basename)
            self.last_update_time = datetime.now()

        if not file_path:
            file_path = self.log_file

        u2_device.ensure_directory_exists(self.log_path)

        for debug in self.log_update_data_debug:
            u2_device.write_to_file(debug, file_path)
            self.log_update_data_debug = []

    def _evt_run_stationary(self):
        self.init_engine()
        if not self.inited:
            self.update_ui("初始化引擎失败，请检查设备连接！")
            return
        self.update_ui("开始原地刷怪...")
        stationary = Stationary(self.app_data)
        stationary.start()

    def _evt_monopoly(self):
        self.init_engine()
        if not self.inited:
            self.update_ui("初始化引擎失败，请检查设备连接！")
            return
        u2_device.check_and_delete(self.log_path, 1)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{current_time}] 游戏盘开始\n"
        u2_device.write_to_file(message, self.log_file)

        self.monopoly = Monopoly()
        self.monopoly.start()

    def _evt_ads(self):
        self.init_engine()
        if not self.inited:
            self.update_ui("初始化引擎失败，请检查设备连接！")
            return
        ads = Ads()
        ads.start()

    def _evt_recollection(self):
        self.init_engine()
        if not self.inited:
            self.update_ui("初始化引擎失败，请检查设备连接！")
            return
        recollection = Recollection()
        recollection.start()

    def open_monopoly_log(self):
        if not self.monopoly:
            tkinter.messagebox.askokcancel("提示", f"游戏盘未启动，请先启动！")
            return
        file_path = self.monopoly.log_award_file
        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            tkinter.messagebox.askokcancel("提示", f"日志文件{self.monopoly.log_award_file}不存在，请检查！")

    def open_readme(self):
        file_path = 'readme.txt'
        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            self.update_ui("帮助文档(readme.txt)不存在，请检查！")

    def edit_battle_script(self):
        file_path = os.path.join('battle_script', 'recollection.txt')
        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            self.update_ui("战斗脚本(recollection.txt)不存在，请检查！")

    def get_coord(self):
        coordinate_getter = GetCoord(self.app_data)
        coordinate_getter.show_coordinates_window()

    def open_monopoly_config(self):
        file_path = os.path.join('config', 'monopoly.txt')
        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            self.update_ui("配置文件(monopoly.txt)不存在，请检查！")

    def open_log(self):
        if os.path.exists(self.log_path):
            os.startfile(self.log_path)
        else:
            self.update_ui("目前没有日志文件，请先运行程序！")

    def open_startup_config(self):
        # 弹出警告框
        response = tkinter.messagebox.askokcancel("配置修改警告",
                                                  "请注意，修改配置后需要重启程序才能生效。是否继续打开配置文件？")
        if response:
            file_path = os.path.join('config', 'startup.txt')
            if os.path.exists(file_path):
                os.startfile(file_path)
            else:
                self.update_ui("配置文件(startup.txt)不存在，请检查！")

    def update_message_label(self, text):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{current_time}] {text}\n"
        self.message_text.config(state=tk.NORMAL)
        self.message_text.insert(tk.END, message)
        self.message_text.config(state=tk.DISABLED)
        self.message_text.see(tk.END)

    def update_stats_label(self, stats):
        self.stats_label.config(text=stats)

    def set_startup_config(self, text, key):
        response = tkinter.messagebox.askokcancel("配置修改警告",
                                                  "请注意，修改配置后需要重启程序才能生效。是否继续打开配置文件？")
        if response:
            update_json_config(path_cfg_statrup, key, text)

    def set_stationary_config(self, text, key):
        update_json_config(path_cfg_stationary, key, text)

    def set_monopoly_config(self, text, key):
        update_json_config(path_cfg_monopoly, key, text)
