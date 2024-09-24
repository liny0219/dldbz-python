import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Label
from view.startup_logic import StartupLogic
from utils.config_loader import cfg_version


class App:
    def __init__(self):
        self.app = tk.Tk()
        self.app.title(f"大霸茶馆v{cfg_version.get('version')}")
        self.app.geometry("800x600")  # 增加窗口宽度
        icon_path = 'image/icon_title.ico'
        self.app.iconbitmap(icon_path)
        self.startup = StartupLogic(self.app)

        self.style = ttk.Style()
        self.default_font = ("Segoe UI", 12)
        self.bold_font = ("Segoe UI", 18, 'bold')
        self.configure_styles()

        self.create_widgets()
        self.app.protocol("WM_DELETE_WINDOW", lambda: self.startup.on_close())
        self.app.mainloop()

    def configure_styles(self):
        self.style.configure('TNotebook.Tab', font=('Segoe UI', '12', 'bold'), padding=[20, 8])

    def create_widgets(self):
        message_label = tk.Label(self.app, text="歧路旅人休息站", font=self.bold_font)
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
        Label(about_frame, text="贡献者: 夜宵, GGBond, Wlog, 章鱼哥, ◕‿◕", font=self.default_font).pack(pady=10)
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

        info_frame = tk.Frame(frame)
        info_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

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
                               font=("Segoe UI", 10), height=15, state=tk.DISABLED)
        message_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        message_scrollbar = tk.Scrollbar(info_frame, orient=tk.VERTICAL, command=message_text.yview)
        message_scrollbar.pack(side='right', fill='y')

    def create_settings_frame(self, frame):
        label_port = tk.Label(frame, text="当前端口:")
        label_port.grid(row=0, column=0, padx=2, pady=2)
        entry_port_val = tk.StringVar()
        entry = tk.Entry(frame, textvariable=entry_port_val, width=30)
        entry.grid(row=0, column=1, padx=10, pady=10)
        self.startup.set_port_ui(entry, entry_port_val)

        btn_port_setting = tk.Button(frame, text="修改端口", width=15, height=1, command=self.startup.btn_set_exe_path)
        btn_port_setting.grid(row=0, column=2, padx=10, pady=10)

        label_exe = tk.Label(frame, text="模拟器路径:")
        label_exe.grid(row=1, column=0, padx=2, pady=2)
        entry_exe_val = tk.StringVar()
        entry = tk.Entry(frame, textvariable=entry_exe_val, width=30)
        entry.grid(row=1, column=1, padx=10, pady=10)
        self.startup.set_exe_ui(entry, entry_exe_val)

        btn_exe_setting = tk.Button(frame, text="设置路径", width=15, height=1, command=self.startup.btn_set_exe_path)
        btn_exe_setting.grid(row=1, column=2, padx=10, pady=10)

        tk.Button(frame, text="设置雷电端口", command=self.startup.btn_set_ld_port,
                  font=("Segoe UI", 10), width=30, height=1).grid(row=2, column=0, padx=10, pady=10)
        tk.Button(frame, text="设置mumu端口", command=self.startup.btn_set_mumu_port,
                  font=("Segoe UI", 10), width=30, height=1).grid(row=2, column=1, padx=10, pady=10)

        tk.Button(frame, text="启动设置", command=self.startup.open_startup_config,
                  font=("Segoe UI", 10), width=30, height=1).grid(row=3, column=0, padx=10, pady=10)
        tk.Button(frame, text="游戏盘设置", command=self.startup.open_monopoly_config,
                  font=("Segoe UI", 10), width=30, height=1).grid(row=3, column=1, padx=10, pady=10)
        tk.Button(frame, text="打开日志", command=self.startup.open_log,
                  font=("Segoe UI", 10), width=30, height=1).grid(row=3, column=2, padx=10, pady=10)

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
