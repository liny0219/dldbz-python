import tkinter as tk
import tkinter.ttk as ttk
from startup import Startup

# 创建主窗口
app = tk.Tk()
app.title("旅人休息站")
app.geometry("800x400")  # 增加窗口宽度

startup = Startup(app)

# # 创建Notebook
# notebook = ttk.Notebook(app)
# notebook.pack(expand=True, fill='both')

# # 创建游戏盘、追忆之书、设置的Frame
# monopoly_frame = tk.Frame(notebook)
# recollection_frame = tk.Frame(notebook)
# settings_frame = tk.Frame(notebook)

# # 添加到Notebook
# notebook.add(monopoly_frame, text='游戏盘')
# notebook.add(recollection_frame, text='追忆之书')
# notebook.add(settings_frame, text='设置')

# 设置关闭事件处理
app.protocol("WM_DELETE_WINDOW", lambda: startup.on_close())


# 使用 grid 布局管理器
app.grid_rowconfigure(2, weight=1)
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=3)

# 顶部子标题标签居中显示
message_label = tk.Label(app, text="大霸启动", font=("Segoe UI", 18, "bold"))
message_label.grid(row=0, column=0, columnspan=2, pady=10)

# 统计信息标签，放置在子标题下方
stats_label = tk.Label(app, text="开始旅途", font=("Segoe UI", 12))
stats_label.grid(row=1, column=0, columnspan=2, pady=5)

# 左侧按钮区域框架
button_frame = tk.Frame(app)
button_frame.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)

# 右侧信息展示框架
info_frame = tk.Frame(app)
info_frame.grid(row=2, column=1, sticky="nswe", padx=10, pady=10)

# 左侧操作按钮
start_button = tk.Button(button_frame, text="游戏盘", command=startup.on_monopoly,
                         font=("Segoe UI", 10), width=10, height=1)
start_button.pack(pady=5)

start_button = tk.Button(button_frame, text="追忆之书", command=startup.on_recollection,
                         font=("Segoe UI", 10), width=10, height=1)
start_button.pack(pady=5)

stop_button = tk.Button(button_frame, text="休息一下", command=startup.on_stop, font=("Segoe UI", 10), width=10, height=1)
stop_button.pack(pady=5)

readme_button = tk.Button(button_frame, text="查看帮助", command=startup.open_readme,
                          font=("Segoe UI", 10), width=10, height=1)
readme_button.pack(pady=5)

edit_script_button = tk.Button(button_frame, text="战斗编辑", command=startup.edit_battle_script,
                               font=("Segoe UI", 10), width=10, height=1)
edit_script_button.pack(pady=5)

get_coord_button = tk.Button(button_frame, text="标记坐标", command=startup.get_coord,
                             font=("Segoe UI", 10), width=10, height=1)
get_coord_button.pack(pady=5)

settings_button = tk.Button(button_frame, text="设置", command=startup.open_startup_config,
                            font=("Segoe UI", 10), width=10, height=1)
settings_button.pack(pady=5)  # 新添加的按钮

# 右侧信息展示区
message_text = tk.Text(info_frame, wrap=tk.WORD, font=("Segoe UI", 12), height=15, state=tk.DISABLED)
message_text.pack(expand=True, fill=tk.BOTH)

# 为右侧信息区添加滚动条
message_scrollbar = tk.Scrollbar(info_frame, orient=tk.VERTICAL, command=message_text.yview)
message_text.config(yscrollcommand=message_scrollbar.set)
message_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

startup.set_ui(message_text, stats_label)

# 运行主循环
app.mainloop()
