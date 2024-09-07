from __future__ import annotations
import datetime
import os
import tkinter as tk
import tkinter.messagebox
from engine.comparator import Comparator
from engine.device_controller import DeviceController
from gameplay.monopoly import Monopoly
from gameplay.recollection import Recollection
from get_coord import GetCoord
from global_data import GlobalData
from utils.stoppable_thread import StoppableThread
from engine_vee.engine import engine_vee
from engine_vee.world import world_vee
from utils.config_loader import cfg_startup
import psutil


class Startup:
    def __init__(self, app: tk.Tk):
        self.resolution = cfg_startup.get('resolution')
        self.controller = DeviceController(cfg_startup.get('adb_port'))
        self.comparator = Comparator(self.controller)
        self.global_data = GlobalData(self.controller, self.comparator, update_ui=self.update_ui)
        self.app = app
        self.stats_label = None
        self.message_text = None
        engine_vee.set(self.global_data)
        world_vee.set(self.global_data)

    def set_stats_label(self, stats_label):
        self.stats_label = stats_label

    def set_message_text(self, message_text):
        self.message_text = message_text

    def on_close(self):
        self.update_ui("正在关闭程序，请稍等...")
        for proc in psutil.process_iter(['pid', 'name']):
            if 'adb' in proc.info['name']:
                print(f"终止进程: {proc.info['name']} (PID: {proc.info['pid']})")
                proc.terminate()
                try:
                    proc.wait(3)
                except psutil.TimeoutExpired:
                    print(f"强制终止进程: {proc.info['name']}")
                    proc.kill()
        self.on_stop()
        self.app.quit()
        self.app.destroy()

    def on_monopoly(self):
        if self.global_data.thread is not None and self.global_data.thread.is_alive():
            self.update_ui("已启动游戏盘，不要重复点击哦！")
            return
        self.global_data.thread = StoppableThread(target=self._evt_monopoly)
        self.global_data.thread.start()

    def on_recollection(self):
        if self.global_data.thread is not None and self.global_data.thread.is_alive():
            self.update_ui("已启动追忆之书，不要重复点击哦！")
            return
        self.global_data.thread = StoppableThread(target=self._evt_recollection)
        self.global_data.thread.start()

    def on_stop(self):
        self.update_ui("休息一下，停止当前操作...")
        if self.global_data.thread is not None:
            self.global_data.thread.stop()

    def update_ui(self, msg, stats=None):
        if not self.message_text:
            return
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{current_time}] {msg}\n"
        self.message_text.config(state=tk.NORMAL)
        self.message_text.insert(tk.END, message)
        self.message_text.config(state=tk.DISABLED)
        self.message_text.see(tk.END)
        if stats:
            self.stats_label.config(text=stats)

    def _evt_monopoly(self):
        monopoly = Monopoly(self.global_data)
        monopoly.start()

    def _evt_recollection(self):
        recollection = Recollection(self.global_data)
        recollection.start()

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
        coordinate_getter = GetCoord(self.controller, self.update_ui)
        coordinate_getter.show_coordinates_window(self.resolution)

    def open_monopoly_config(self):
        # 弹出警告框
        response = tk.messagebox.askokcancel("配置修改警告",
                                             "请注意，修改配置后需要重启程序才能生效。是否继续打开配置文件？")
        if response:
            file_path = os.path.join('config', 'monopoly.json')
            if os.path.exists(file_path):
                os.startfile(file_path)
            else:
                self.update_ui("配置文件(monopoly.json)不存在，请检查！")

    def open_startup_config(self):
        # 弹出警告框
        response = tkinter.messagebox.askokcancel("配置修改警告",
                                                  "请注意，修改配置后需要重启程序才能生效。是否继续打开配置文件？")
        if response:
            file_path = os.path.join('config', 'startup.json')
            if os.path.exists(file_path):
                os.startfile(file_path)
            else:
                self.update_ui("配置文件(startup.json)不存在，请检查！")

    def update_message_label(self, text):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{current_time}] {text}\n"
        self.message_text.config(state=tk.NORMAL)
        self.message_text.insert(tk.END, message)
        self.message_text.config(state=tk.DISABLED)
        self.message_text.see(tk.END)

    def update_stats_label(self, stats):
        self.stats_label.config(text=stats)
