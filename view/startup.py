import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Label
from utils.config_loader import cfg_version
from view.startup_logic import StartupLogic


class AppModule:
    def __init__(self):
        self.app = tk.Tk()
        self.startup = None
        self.notebook = None
        self.stats_label = None

    def initialize(self):
        # 创建主窗口
        self.app.title(f"大霸茶馆v{cfg_version.get('version')}")
        self.app.geometry("800x600")  # 增加窗口宽度
        icon_path = 'image/icon_title.ico'
        self.app.iconbitmap(icon_path)

        # 初始化 Startup 类
        self.startup = StartupLogic(self.app)

        # 创建样式对象
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Segoe UI', '12', 'bold'), padding=[20, 8])

        # 顶部子标题标签居中显示
        bold_font = ("Segoe UI", 18, 'bold')
        message_label = tk.Label(self.app, text="歧路旅人休息站", font=bold_font)
        message_label.grid(row=0, column=0, columnspan=2, pady=10)

        # 统计信息标签，放置在子标题下方
        default_font = ("Segoe UI", 12)
        self.stats_label = tk.Label(self.app, text="大霸启动!", font=default_font)
        self.stats_label.grid(row=1, column=0, columnspan=2, pady=5)

        # 创建 Notebook
        self.notebook = ttk.Notebook(self.app)
        self.notebook.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)

        self._create_frames()

        self.app.grid_rowconfigure(2, weight=1)
        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_columnconfigure(1, weight=1)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # 设置关闭事件处理
        self.app.protocol("WM_DELETE_WINDOW", lambda: self.startup.on_close())
        self.startup.set_stats_label(self.stats_label)

    def _create_frames(self):
        # 创建各个标签页的 Frame
        monopoly_frame = tk.Frame(self.notebook, name="monopoly_frame")
        recollection_frame = tk.Frame(self.notebook, name="recollection_frame")
        map_frame = tk.Frame(self.notebook, name="map_frame")
        settings_frame = tk.Frame(self.notebook, name="settings_frame")
        about_frame = tk.Frame(self.notebook, name="about_frame")

        # 添加到 Notebook 中
        self.notebook.add(monopoly_frame, text='游戏盘')
        self.notebook.add(recollection_frame, text='追忆之书(未完善)')
        self.notebook.add(map_frame, text='大地图')
        self.notebook.add(settings_frame, text='设置')
        self.notebook.add(about_frame, text='关于')

        self._create_info_button(monopoly_frame)
        self._create_info_button(recollection_frame)
        self._create_info_button(map_frame)
        self._create_settings_frame(settings_frame)

        # 关于页面内容
        Label(about_frame, text=f"大霸茶馆 v{cfg_version.get('version')}", font=("Segoe UI", 18, 'bold')).pack(pady=10)
        Label(about_frame, text="仅供交流学习用，请勿用于任何商业盈利", font=("Segoe UI", 12)).pack(pady=10)
        Label(about_frame, text="贡献者: 大霸茶馆", font=("Segoe UI", 12)).pack(pady=10)
        Label(about_frame, text="©2024", font=("Segoe UI", 12)).pack(pady=10)

    def _create_settings_frame(self, frame):
        # 设置框架的控件配置
        label_port = tk.Label(frame, text="当前端口:")
        label_port.grid(row=0, column=0, padx=2, pady=2)
        entry_port_val = tk.StringVar()
        entry = tk.Entry(frame, textvariable=entry_port_val, width=30)
        entry.grid(row=0, column=1, padx=10, pady=10)
        self.startup.set_port_ui(entry, entry_port_val)

        btn_port_setting = tk.Button(frame, text="修改端口", width=15, height=1, command=self.startup.btn_set_exe_path)
        btn_port_setting.grid(row=0, column=2, padx=10, pady=10)

        # 同样添加其他按钮与配置

    def _create_info_button(self, frame):
        # 创建按钮和信息框
        button_frame = tk.Frame(frame)
        button_frame.pack(side='left', fill='y', padx=10, pady=10)

        info_frame = tk.Frame(frame)
        info_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # 定义和创建按钮
        buttons = [
            {"text": "大霸启动", "command": self.startup.on_monopoly},
            {"text": "休息一下", "command": self.startup.on_stop},
            {"text": "查看帮助", "command": self.startup.open_readme}
        ]
        for button_config in buttons:
            tk.Button(button_frame, text=button_config["text"], command=button_config["command"],
                      font=("Segoe UI", 10), width=10, height=1).pack(pady=5)

        # 信息展示区
        message_text = tk.Text(info_frame, name="info_label", wrap=tk.WORD,
                               font=("Segoe UI", 10), height=15, state=tk.DISABLED)
        message_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        message_scrollbar = tk.Scrollbar(info_frame, orient=tk.VERTICAL, command=message_text.yview)
        message_scrollbar.pack(side='right', fill='y')

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
        notebook = event.widget
        selected_tab_name = notebook.select()
        selected_tab = notebook.nametowidget(selected_tab_name)
        info_label = self.find_widget_by_name(selected_tab, "info_label")
        if info_label is not None:
            self.startup.set_message_text(info_label)

    def run(self):
        self.initialize()
        self.app.mainloop()
