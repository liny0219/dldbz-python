import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Label
from view.startup_logic import StartupLogic
from utils.config_loader import cfg_version, cfg_stationary, cfg_monopoly, cfg_startup
from PIL import Image, ImageTk


class App:
    def __init__(self):
        self.app = tk.Tk()
        self.app.title(f"大霸茶馆v{cfg_version.get('version')}")
        width = 900
        height = 600
        self.app.geometry(f"{width}x{height}")  # 增加窗口宽度
        icon_path = 'image/icon_title.ico'
        self.app.iconbitmap(icon_path)
        self.startup = StartupLogic(self.app)

        self.style = ttk.Style()
        self.default_font = ("Segoe UI", 12)
        self.bold_font = ("Segoe UI", 18, 'bold')
        self.configure_styles()

        left_label, left_image = self.load_and_display_image('image/2b.png')
        left_label.place(x=width-110, y=10)
        self.left_image = left_image

        right_label, right_image = self.load_and_display_image('image/2a.png')
        right_label.place(x=10, y=10)
        self.right_image = right_image

        self.create_widgets()
        self.app.protocol("WM_DELETE_WINDOW", lambda: self.startup.on_close())

    def load_and_display_image(self, image_path):
        # 使用Pillow加载图片
        original_image = Image.open(image_path)

        # 设置目标宽度
        target_width = 100
        aspect_ratio = original_image.height / original_image.width
        target_height = int(target_width * aspect_ratio)

        # 调整图片大小
        resized_image = original_image.resize((target_width, target_height), Image.LANCZOS)
        image = ImageTk.PhotoImage(resized_image)

        # 创建标签并显示图片
        label = tk.Label(self.app, image=image)
        return label, image

    def configure_styles(self):
        self.style.configure('TNotebook.Tab', font=('Segoe UI', '12', 'bold'), padding=[20, 8])

    def create_widgets(self):
        message_label = tk.Label(self.app, text="完全免费脚本,歧路旅人休息站,群号213459239", font=self.bold_font)
        message_label.grid(row=0, column=0, columnspan=2, pady=10)

        stats_label = tk.Label(self.app, text="大霸启动!", font=self.default_font)
        stats_label.grid(row=1, column=0, columnspan=2, pady=5)

        notebook = ttk.Notebook(self.app)
        notebook.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)

        self.create_frames(notebook)
        self.create_info_buttons(notebook)

        notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.startup.set_stats_label(stats_label)

        self.app.grid_rowconfigure(2, weight=1)
        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_columnconfigure(1, weight=1)
        self.app.grid_columnconfigure(2, weight=3)

    def create_frames(self, notebook):
        self.monopoly_frame = tk.Frame(notebook, name="monopoly_frame")
        self.recollection_frame = tk.Frame(notebook, name="recollection_frame")
        self.map_frame = tk.Frame(notebook, name="map_frame")
        self.settings_frame = tk.Frame(notebook, name="settings_frame")  # 移动到这里
        about_frame = tk.Frame(notebook, name="about_frame")

        Label(about_frame, text=f"大霸茶馆 v{cfg_version.get('version')}", font=self.bold_font).pack(pady=10)
        Label(about_frame, text="仅供交流学习用，请勿用于任何商业盈利", font=self.default_font).pack(pady=10)
        Label(about_frame, text="©2024", font=self.default_font).pack(pady=10)

        notebook.add(self.monopoly_frame, text='游戏盘')
        notebook.add(self.recollection_frame, text='追忆之书(未完善)')
        notebook.add(self.map_frame, text='大地图')
        notebook.add(self.settings_frame, text='设置')  # 添加到这里
        notebook.add(about_frame, text='关于')

    def create_info_buttons(self, notebook):
        self.create_info_button(self.monopoly_frame)
        self.create_info_button(self.recollection_frame)
        self.create_info_button(self.map_frame)
        self.create_settings_frame(self.settings_frame)  # 直接使用已创建的设置框架

    def create_info_button(self, frame):
        button_frame = tk.Frame(frame)
        button_frame.pack(side='left', fill='y', padx=10, pady=10)

        info_frame = tk.Frame(frame, width=500)
        info_frame.pack_propagate(0)
        info_frame.pack(side='left', fill='y', padx=10, pady=10)

        main_button = {"text": "大霸启动", "command": self.startup.on_monopoly}
        if frame == self.recollection_frame:
            main_button["text"] = "追忆启动"
            main_button["command"] = self.startup.on_recollection
        elif frame == self.map_frame:
            main_button["text"] = "刷野启动"
            main_button["command"] = self.startup.on_stationary

        buttons = [
            main_button,
            {"text": "休息一下", "command": self.startup.on_stop},
            {"text": "查看帮助", "command": self.startup.open_readme},
            {"text": "战斗编辑", "command": self.startup.edit_battle_script},
            {"text": "标记坐标", "command": self.startup.get_coord}
        ]

        for button_config in buttons:
            tk.Button(button_frame, text=button_config["text"], command=button_config["command"],
                      font=("Segoe UI", 10), width=10, height=1).pack(pady=5)

        message_text = tk.Text(info_frame, name="info_label", wrap=tk.WORD,
                               font=("Segoe UI", 10), width=500, height=15, state=tk.DISABLED)
        message_text.pack(side='left', fill='y', expand=True, padx=10, pady=10)

        message_scrollbar = tk.Scrollbar(info_frame, orient=tk.VERTICAL, command=message_text.yview)
        message_scrollbar.pack(side='right', fill='y')
        if frame == self.monopoly_frame:
            cfg_monopoly_type = cfg_monopoly.get("type")
            cfg_monopoly_ticket = cfg_monopoly.get("ticket")
            cfg_monopoly_lv = cfg_monopoly.get("lv")
            cfg_monopoly_enemy_check = cfg_monopoly.get("enemy_check")
            self.cmb_monopoly_type = ComboBoxComponent(
                frame, "游戏盘:", {
                    "80权利": "801",
                    "80财富": "802",
                    "80名声": "803",
                }, lambda text: self.startup.set_monopoly_config(text, 'type'), default_value=cfg_monopoly_type)
            self.cmb_monopoly_type.pack(padx=10, pady=5, anchor=tk.W)  # 组件左对齐

            self.cmb_ticket_type = ComboBoxComponent(
                frame, "票数:", {
                    "0": "0",
                    "1": "1",
                    "2": "2",
                    "3": "3",
                    "4": "4",
                    "5": "5",
                    "6": "6",
                    "7": "7",
                    "8": "8",
                }, lambda text: self.startup.set_monopoly_config(text, 'ticket'), default_value=cfg_monopoly_ticket)
            self.cmb_ticket_type.pack(padx=10, pady=5, anchor=tk.W)  # 组件左对齐

            self.cmb_ticket_type = ComboBoxComponent(
                frame, "难度:", {
                    "0": "0",
                    "1": "1",
                    "2": "2",
                    "3": "3",
                    "4": "4",
                    "5": "5",
                }, lambda text: self.startup.set_monopoly_config(text, 'lv'), default_value=cfg_monopoly_lv)
            self.cmb_ticket_type.pack(padx=10, pady=5, anchor=tk.W)  # 组件左对齐

            self.cmb_enemy_check = ComboBoxComponent(
                frame, "检测敌人:", {
                    "关闭": "0",
                    "开启": "1"
                }, lambda text: self.startup.set_monopoly_config(text, 'enemy_check'), default_value=cfg_monopoly_enemy_check)
            self.cmb_enemy_check.pack(padx=10, pady=5, anchor=tk.W)  # 组件左对齐

        if frame == self.map_frame:
            run_enabled = cfg_stationary.get("run_enabled")
            max_battle_count = cfg_stationary.get("max_battle_count")
            max_run_count = cfg_stationary.get("max_run_count")
            cmb_run_enabled_text = int(run_enabled)
            self.cmb_run_enabled = ComboBoxComponent(
                frame, "打N跑N:", {
                    "关闭": False,
                    "开启": True
                }, lambda text: self.startup.set_stationary_config(text, 'run_enabled'), default_value=cmb_run_enabled_text)
            self.cmb_run_enabled.pack(padx=10, pady=5, anchor=tk.W)  # 组件左对齐

            self.input_max_battle_count = InputComponent(
                frame, "战斗N次:", lambda text: self.startup.set_stationary_config(text, 'max_battle_count'), default_value=max_battle_count)
            self.input_max_battle_count.pack(padx=10, pady=5, anchor=tk.W)  # 组件左对齐

            self.input_max_run_count = InputComponent(
                frame, "逃跑N次:", lambda text: self.startup.set_stationary_config(text, 'max_run_count'), default_value=max_run_count)
            self.input_max_run_count.pack(padx=10, pady=5, anchor=tk.W)  # 组件

    def on_option_selected(self, option, key):

        print(f"选中的选项: {option}")

    def create_settings_frame(self, frame):
        adb_port = cfg_startup.get("adb_port")
        self.input_port = InputComponent(
            frame, "当前端口:", lambda text: self.startup.set_startup_config(text, 'adb_port'), default_value=adb_port, entry_width=30)
        self.input_port.grid(row=0, column=0, columnspan=3, pady=10)

        tk.Button(frame, text="启动设置", command=self.startup.open_startup_config,
                  font=("Segoe UI", 10), width=30, height=1).grid(row=2, column=0, padx=10, pady=10)
        tk.Button(frame, text="游戏盘设置", command=self.startup.open_monopoly_config,
                  font=("Segoe UI", 10), width=30, height=1).grid(row=2, column=1, padx=10, pady=10)
        tk.Button(frame, text="打开日志", command=self.startup.open_log,
                  font=("Segoe UI", 10), width=30, height=1).grid(row=2, column=2, padx=10, pady=10)

    def find_widget_by_name(self, parent, widget_name):
        """递归查找具有指定name的组件"""
        if str(parent.winfo_name()) == widget_name:
            return parent
        for child in parent.winfo_children():
            result = self.find_widget_by_name(child, widget_name)
            if result is not None:
                return result
        return None

    def on_tab_changed(self, event: tk.Event):
        notebook: ttk.Notebook = event.widget
        selected_tab_name = notebook.select()
        selected_tab = notebook.nametowidget(selected_tab_name)
        info_label = self.find_widget_by_name(selected_tab, "info_label")
        if info_label is not None:
            print(f"当前选中的Tab: {info_label}")
            self.startup.set_message_text(info_label)
        else:
            print("未找到info_label")

    def run(self):
        self.app.mainloop()


class ComboBoxComponent:
    def __init__(self, master, label_text,  value_map, on_select, default_value=0, label_width=8):
        self.frame = tk.Frame(master)

        # 创建标签
        self.label = tk.Label(self.frame, text=label_text, anchor=tk.W, width=label_width)
        self.label.pack(side=tk.LEFT)

        # 保存值映射字典
        self.value_map = value_map
        self.inverse_value_map = {v: k for k, v in value_map.items()}  # 反向映射用于设置选中的文本

        # 创建下拉框并显示可读选项
        self.combobox = ttk.Combobox(self.frame, values=list(self.value_map.keys()), width=8)
        self.combobox.pack(side=tk.LEFT, fill=tk.X)

        # 设置默认选项（根据映射值找到对应的key，然后获取其索引）
        if default_value is not None and default_value in self.inverse_value_map:
            default_key = self.inverse_value_map[default_value]  # 根据value找到key
            default_index = list(self.value_map.keys()).index(default_key)  # 根据key找到对应的索引
            self.combobox.current(default_index)  # 设

        # 创建确定按钮，点击时传递映射后的值
        self.button = tk.Button(self.frame, text="确定", command=self.select_value)
        self.button.pack(side=tk.RIGHT, padx=10)

        # 保存回调函数
        self.on_select = on_select

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def select_value(self):
        selected_text = self.combobox.get()  # 获取用户可见的选项
        mapped_value = self.value_map.get(selected_text)  # 将选项映射为实际值
        if mapped_value is not None:
            self.on_select(mapped_value)

    def set_selected_value(self, value):
        # 将内部值映射回可见的选项并更新 Combobox
        if value in self.inverse_value_map:
            selected_text = self.inverse_value_map[value]
            self.combobox.set(selected_text)


class InputComponent:
    def __init__(self, master, label_text, on_submit, default_value=0, label_width=8, entry_width=10):
        self.frame = tk.Frame(master)

        # 创建标签
        self.label = tk.Label(self.frame, text=label_text, anchor=tk.W, width=label_width)
        self.label.pack(side=tk.LEFT)

        # 创建输入框
        self.entry = tk.Entry(self.frame, width=entry_width)
        self.entry.pack(side=tk.LEFT, fill=tk.X)
        self.entry.insert(0, str(default_value))  # 设置默认值
        # 创建确定按钮
        self.button = tk.Button(self.frame, text="确定", command=lambda: on_submit(self.entry.get()))
        self.button.pack(side=tk.RIGHT, padx=10)  # 增加横向间距

    def pack(self, **kwargs):
        # 使用显式传递来避免重复传递参数问题
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        # 使用显式传递来避免重复传递参数问题
        self.frame.grid(**kwargs)

    def set_value(self, value):
        self.entry.delete(0, tk.END)  # 清除输入框现有内容
        self.entry.insert(0, str(value))  # 插入新的值
