import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Label
from startup_logic import Startup
from utils.config_loader import cfg_version
# 创建主窗口
app = tk.Tk()
app.title(f"大霸茶馆v{cfg_version.get('version')}")
app.geometry("800x600")  # 增加窗口宽度
icon_path = 'image/icon_title.ico'
app.iconbitmap(icon_path)
startup = Startup(app)
# 创建样式对象
style = ttk.Style()

# font_path = "fonts/FZSTK.TTF"  # 字体路径
default_font = ("Segoe UI", 12)  # 默认字体大小为12
bold_font = ("Segoe UI", 18, 'bold')  # 粗体字，大小为18
# 配置'TNotebook.Tab'的样式
style.configure('TNotebook.Tab', font=('Segoe UI', '12', 'bold'), padding=[20, 8])

# 顶部子标题标签居中显示
message_label = tk.Label(app, text="歧路旅人休息站", font=bold_font)
message_label.grid(row=0, column=0, columnspan=2, pady=10)

# 统计信息标签，放置在子标题下方
stats_label = tk.Label(app, text="大霸启动!", font=default_font)
stats_label.grid(row=1, column=0, columnspan=2, pady=5)

notebook = ttk.Notebook(app)
notebook.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)


# 创建游戏盘、追忆之书、设置的Frame
monopoly_frame = tk.Frame(notebook, name="monopoly_frame")

recollection_frame = tk.Frame(notebook, name="recollection_frame")

map_frame = tk.Frame(notebook, name="map_frame")

settings_frame = tk.Frame(notebook, name="settings_frame")
settings_frame.grid(padx=10, pady=5)


about_frame = tk.Frame(notebook, name="about_frame")
about_frame.grid(padx=10, pady=5)

Label(about_frame, text=f"大霸茶馆 v{cfg_version.get('version')}", font=bold_font).pack(pady=10)
Label(about_frame, text="仅供交流学习用，请勿用于任何商业盈利", font=default_font).pack(pady=10)
Label(about_frame, text="贡献者: 夜宵, GGBond, Wlog, 章鱼哥, ◕‿◕", font=default_font).pack(pady=10)
Label(about_frame, text="©2024", font=default_font).pack(pady=10)

# 添加到Notebook
notebook.add(monopoly_frame, text='游戏盘')
notebook.add(recollection_frame, text='追忆之书')
notebook.add(map_frame, text='大地图')
notebook.add(settings_frame, text='设置')
notebook.add(about_frame, text='关于')

# 使用 grid 布局管理器
app.grid_rowconfigure(2, weight=1)
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)
app.grid_columnconfigure(2, weight=3)


def create_map_frame(frame):
    tk.Button(frame, text="原地刷野", command=startup.on_stationary,
              font=("Segoe UI", 10), width=10, height=1).grid(row=0, column=0, padx=10, pady=10)


def create_settings_frame(frame):

    label_port = tk.Label(frame, text="当前端口:")
    label_port.grid(row=0, column=0, padx=2, pady=2)
    entry_port_val = tk.StringVar()
    entry = tk.Entry(frame, textvariable=entry_port_val, width=30)
    entry.grid(row=0, column=1, padx=10, pady=10)
    startup.set_port_ui(entry, entry_port_val)
    btn_port_setting = tk.Button(frame, text="修改端口", width=15, height=1, command=startup.btn_set_exe_path)
    btn_port_setting.grid(row=0, column=2, padx=10, pady=10)

    label_exe = tk.Label(frame, text="模拟器路径:")
    label_exe.grid(row=1, column=0, padx=2, pady=2)
    entry_exe_val = tk.StringVar()
    entry = tk.Entry(frame, textvariable=entry_exe_val, width=30)
    entry.grid(row=1, column=1, padx=10, pady=10)
    startup.set_exe_ui(entry, entry_exe_val)
    btn_exe_setting = tk.Button(frame, text="设置路径", width=15, height=1, command=startup.btn_set_exe_path)
    btn_exe_setting.grid(row=1, column=2, padx=10, pady=10)

    tk.Button(frame, text="设置雷电端口", command=startup.btn_set_ld_port,
              font=("Segoe UI", 10), width=30, height=1).grid(row=2, column=0, padx=10, pady=10)
    tk.Button(frame, text="设置mumu端口", command=startup.btn_set_mumu_port,
              font=("Segoe UI", 10), width=30, height=1).grid(row=2, column=1, padx=10, pady=10)

    tk.Button(frame, text="启动设置", command=startup.open_startup_config,
              font=("Segoe UI", 10), width=30, height=1).grid(row=3, column=0, padx=10, pady=10)
    tk.Button(frame, text="游戏盘设置", command=startup.open_monopoly_config,
              font=("Segoe UI", 10), width=30, height=1).grid(row=3, column=1, padx=10, pady=10)


def create_info_button(frame):
    # 左侧按钮区域框架
    button_frame = tk.Frame(frame)
    button_frame.pack(side='left', fill='y', padx=10, pady=10)

    # 右侧信息展示框架
    info_frame = tk.Frame(frame)
    info_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

    main_button = {"text": "大霸启动", "command": None}
    if frame == monopoly_frame:
        main_button["text"] = "大霸启动"
        main_button["command"] = startup.on_monopoly
    elif frame == recollection_frame:
        main_button["text"] = "追忆启动"
        main_button["command"] = startup.on_recollection
    elif frame == map_frame:
        main_button["text"] = "刷野启动"
        main_button["command"] = startup.on_stationary

    # 定义按钮的配置列表
    buttons = [
        main_button,
        {"text": "休息一下", "command": startup.on_stop},
        {"text": "查看帮助", "command": startup.open_readme},
        {"text": "战斗编辑", "command": startup.edit_battle_script},
        {"text": "标记坐标", "command": startup.get_coord}
    ]

    # 创建按钮
    for button_config in buttons:
        tk.Button(button_frame, text=button_config["text"], command=button_config["command"],
                  font=("Segoe UI", 10), width=10, height=1).pack(pady=5)

    # 右侧信息展示区
    message_text = tk.Text(info_frame, name="info_label", wrap=tk.WORD,
                           font=("Segoe UI", 10), height=15, state=tk.DISABLED)
    message_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)

    # 为右侧信息区添加滚动条
    message_scrollbar = tk.Scrollbar(info_frame, orient=tk.VERTICAL, command=message_text.yview)
    message_scrollbar.pack(side='right', fill='y')


create_info_button(monopoly_frame)
create_info_button(recollection_frame)
create_info_button(map_frame)
create_settings_frame(settings_frame)


def find_widget_by_name(parent, widget_name):
    """递归查找具有指定name的组件"""
    # 检查当前父组件是否是我们正在查找的组件
    if str(parent.winfo_name()) == widget_name:
        return parent
    # 如果不是，遍历所有子组件
    for child in parent.winfo_children():
        result = find_widget_by_name(child, widget_name)
        if result is not None:
            return result
    return None


def on_tab_changed(event: tk.Event):
    notebook: ttk.Notebook = event.widget
    selected_tab_name = notebook.select()  # 获取当前选中的tab的内部名称
    selected_tab = notebook.nametowidget(selected_tab_name)  # 从名称获取 widget 对象
    info_label = find_widget_by_name(selected_tab, "info_label")
    if info_label is not None:
        print(f"当前选中的Tab: {info_label}")
        startup.set_message_text(info_label)
    else:
        print("未找到info_label")


notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
startup.set_stats_label(stats_label)


# 设置关闭事件处理
app.protocol("WM_DELETE_WINDOW", lambda: startup.on_close())
# 运行主循环
app.mainloop()
