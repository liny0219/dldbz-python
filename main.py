import os
import datetime
import tkinter as tk
import tkinter.messagebox
from engine.comparator import Comparator
from engine.device_controller import DeviceController
from gameplay.recollection import Recollection
from get_coord import GetCoord
from global_data import GlobalData
from utils.stoppable_thread import StoppableThread
from utils.config_loader import cfg_startup
import psutil


# 创建主窗口
app = tk.Tk()
app.title("旅人休息站")
app.geometry("800x400")  # 增加窗口宽度

# 设置关闭事件处理
app.protocol("WM_DELETE_WINDOW", lambda: on_close())


def fn_UpdateUI(msg, stats=None): return updateUI(msg, stats)


resolution = cfg_startup.get('resolution')
controller = DeviceController(cfg_startup.get('adb_port'))
comparator = Comparator(controller)

global_data = GlobalData(controller, comparator, updateUI=fn_UpdateUI)


def on_close():
    updateUI("正在关闭程序，请稍等...")
    # 尝试查找并终止所有adb进程
    for proc in psutil.process_iter(['pid', 'name']):
        if 'adb' in proc.info['name']:
            print(f"终止进程: {proc.info['name']} (PID: {proc.info['pid']})")
            proc.terminate()
            try:
                proc.wait(3)  # 等待最多3秒以确保进程被终止
            except psutil.TimeoutExpired:
                print(f"强制终止进程: {proc.info['name']}")
                proc.kill()
    on_stop()  # 停止当前线程
    app.quit()  # 退出主循环
    app.destroy()  # 销毁窗口


def updateUI(msg, stats=None):
    app.after(0, update_message_label, msg)
    if stats:
        app.after(0, update_stats_label, stats)


def evt_monopoly():
    pass


def evt_recollection():
    recollection_instance = Recollection(global_data)
    recollection_instance.start()


def on_monopoly():
    if global_data.thread is not None and global_data.thread.is_alive():
        updateUI("已启动游戏盘，不要重复点击哦！")
        return
    global_data.thread = StoppableThread(target=lambda: evt_monopoly())
    global_data.thread.start()


def on_recollection():
    if global_data.thread is not None and global_data.thread.is_alive():
        updateUI("已启动追忆之书，不要重复点击哦！")
        return
    global_data.thread = StoppableThread(target=lambda: evt_recollection())
    global_data.thread.start()


def on_stop():
    if global_data.thread is not None:
        # 更新UI
        updateUI("正在停止当前操作，请稍等...")
        global_data.thread.stop()


def open_readme():
    file_path = 'readme.txt'
    if os.path.exists(file_path):
        os.startfile(file_path)
    else:
        updateUI("帮助文档(readme.txt)不存在，请检查！")


def edit_battle_script():
    file_path = os.path.join('battle_script', 'recollection.txt')
    if os.path.exists(file_path):
        os.startfile(file_path)
    else:
        updateUI("战斗脚本(recollection.txt)不存在，请检查！")


def get_coord():
    coordinate_getter = GetCoord(controller, updateUI)
    coordinate_getter.show_coordinates_window(resolution)


def open_startup_config():
    # 弹出警告框
    response = tkinter.messagebox.askokcancel("配置修改警告",
                                              "请注意，修改配置后需要重启程序才能生效。是否继续打开配置文件？")
    if response:
        file_path = os.path.join('config', 'startup.json')
        if os.path.exists(file_path):
            os.startfile(file_path)
            updateUI("已尝试打开配置文件(startup)。")
        else:
            updateUI("配置文件(startup)不存在，请检查！")


def update_message_label(text):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{current_time}] {text}\n"
    message_text.config(state=tk.NORMAL)
    message_text.insert(tk.END, message)
    message_text.config(state=tk.DISABLED)
    message_text.see(tk.END)


def update_stats_label(stats):
    stats_label.config(text=stats)


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
start_button = tk.Button(button_frame, text="游戏盘", command=on_monopoly, font=("Segoe UI", 10), width=10, height=1)
start_button.pack(pady=5)

start_button = tk.Button(button_frame, text="追忆之书", command=on_recollection, font=("Segoe UI", 10), width=10, height=1)
start_button.pack(pady=5)

stop_button = tk.Button(button_frame, text="休息一下", command=on_stop, font=("Segoe UI", 10), width=10, height=1)
stop_button.pack(pady=5)

readme_button = tk.Button(button_frame, text="查看帮助", command=open_readme, font=("Segoe UI", 10), width=10, height=1)
readme_button.pack(pady=5)

edit_script_button = tk.Button(button_frame, text="战斗编辑", command=edit_battle_script,
                               font=("Segoe UI", 10), width=10, height=1)
edit_script_button.pack(pady=5)

get_coord_button = tk.Button(button_frame, text="标记坐标", command=get_coord,
                             font=("Segoe UI", 10), width=10, height=1)
get_coord_button.pack(pady=5)

settings_button = tk.Button(button_frame, text="设置", command=open_startup_config,
                            font=("Segoe UI", 10), width=10, height=1)
settings_button.pack(pady=5)  # 新添加的按钮

# 右侧信息展示区
message_text = tk.Text(info_frame, wrap=tk.WORD, font=("Segoe UI", 12), height=15, state=tk.DISABLED)
message_text.pack(expand=True, fill=tk.BOTH)

# 为右侧信息区添加滚动条
message_scrollbar = tk.Scrollbar(info_frame, orient=tk.VERTICAL, command=message_text.yview)
message_text.config(yscrollcommand=message_scrollbar.set)
message_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# 运行主循环
app.mainloop()
