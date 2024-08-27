import os
import tkinter as tk
from tkinter import ttk
from engine.recollection import recollection
from utils.stoppable_thread import StoppableThread
import psutil


def on_close():
    print("Closing the application...")
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


def evt_recollection(thread: StoppableThread):
    recollection_instance = recollection(updateUI)
    recollection_instance.setThread(thread)
    recollection_instance.start()


def on_click():
    global current_thread
    if current_thread is not None and current_thread.is_alive():
        print(f"{current_thread.name} is already running.")
        updateUI("已经在追忆之旅中了，不要重复点击哦！")
        return
    current_thread = StoppableThread(target=lambda: evt_recollection(current_thread))
    current_thread.start()


def on_stop():
    if current_thread is not None:
        current_thread.stop()


def open_readme():
    file_path = 'readme.txt'
    if os.path.exists(file_path):
        os.startfile(file_path)
        updateUI("已尝试打开帮助文档(readme.txt)。")
    else:
        updateUI("帮助文档(readme.txt)不存在，请检查！")


def edit_battle_script():
    file_path = os.path.join('battle_script', 'recollection.txt')
    if os.path.exists(file_path):
        os.startfile(file_path)
        updateUI("已尝试打开战斗脚本(recollection.txt)。")
    else:
        updateUI("战斗脚本(recollection.txt)不存在，请检查！")


# 创建主窗口
app = tk.Tk()
app.title("旅人休息站")
app.geometry("800x400")  # 增加窗口宽度

# 设置关闭事件处理
app.protocol("WM_DELETE_WINDOW", on_close)


def updateUI(msg, stats=None):
    app.after(0, update_message_label, msg)
    if stats:
        app.after(0, update_stats_label, stats)


def update_message_label(text):
    message_text.config(state=tk.NORMAL)
    message_text.insert(tk.END, text + "\n")
    message_text.config(state=tk.DISABLED)
    message_text.see(tk.END)


def update_stats_label(stats):
    stats_label.config(text=stats)


# 使用 grid 布局管理器
app.grid_rowconfigure(2, weight=1)
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=3)

# 顶部子标题标签居中显示
message_label = tk.Label(app, text="愉快的歧路旅途", font=("Segoe UI", 14, "bold"))
message_label.grid(row=0, column=0, columnspan=2, pady=10)

# 统计信息标签，放置在子标题下方
stats_label = tk.Label(app, text="即将开始旅途", font=("Segoe UI", 12))
stats_label.grid(row=1, column=0, columnspan=2, pady=5)

# 左侧按钮区域框架
button_frame = tk.Frame(app)
button_frame.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)

# 右侧信息展示框架
info_frame = tk.Frame(app)
info_frame.grid(row=2, column=1, sticky="nswe", padx=10, pady=10)

# 左侧操作按钮
start_button = tk.Button(button_frame, text="追忆之旅", command=on_click, font=("Segoe UI", 10), width=10, height=1)
start_button.pack(pady=5)

stop_button = tk.Button(button_frame, text="休息一下", command=on_stop, font=("Segoe UI", 10), width=10, height=1)
stop_button.pack(pady=5)

readme_button = tk.Button(button_frame, text="查看帮助", command=open_readme, font=("Segoe UI", 10), width=10, height=1)
readme_button.pack(pady=5)

edit_script_button = tk.Button(button_frame, text="战斗编辑", command=edit_battle_script,
                               font=("Segoe UI", 10), width=10, height=1)
edit_script_button.pack(pady=5)  # 新添加的按钮

# 右侧信息展示区
message_text = tk.Text(info_frame, wrap=tk.WORD, font=("Segoe UI", 12), height=15, state=tk.DISABLED)
message_text.pack(expand=True, fill=tk.BOTH)

# 为右侧信息区添加滚动条
message_scrollbar = tk.Scrollbar(info_frame, orient=tk.VERTICAL, command=message_text.yview)
message_text.config(yscrollcommand=message_scrollbar.set)
message_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

current_thread = None  # 全局变量来存储当前的线程引用

# 运行主循环
app.mainloop()
