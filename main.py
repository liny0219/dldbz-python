import tkinter as tk
from tkinter import ttk
from engine.recollection import recollection
from utils.stoppable_thread import StoppableThread

def on_close():
    print("Closing the application...")
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
        return
    current_thread = StoppableThread(target=lambda: evt_recollection(current_thread))
    current_thread.start()

def on_stop():
    if current_thread is not None:
        current_thread.stop()

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
    message_text.config(state=tk.NORMAL)  # 使 Text 可编辑以便插入
    message_text.insert(tk.END, text + "\n")  # 在末尾插入新消息
    message_text.config(state=tk.DISABLED)  # 插入后再设置为不可编辑
    message_text.see(tk.END)  # 自动滚动到底部

def update_stats_label(stats):
    stats_label.config(text=stats)  # 更新统计信息

# 使用 grid 布局管理器
app.grid_rowconfigure(2, weight=1)  # 设置行的权重使其拉伸
app.grid_columnconfigure(0, weight=1)  # 左侧按钮区域
app.grid_columnconfigure(1, weight=3)  # 右侧信息展示区域，宽度是左侧的三倍

# 顶部子标题标签居中显示
message_label = tk.Label(app, text="愉快的歧路旅途", font=("Segoe UI", 14, "bold"))
message_label.grid(row=0, column=0, columnspan=2, pady=10)

# 统计信息标签，放置在子标题下方
stats_label = tk.Label(app, text="即将开始旅途", font=("Segoe UI", 12))
stats_label.grid(row=1, column=0, columnspan=2, pady=5)

# 左侧按钮区域框架，进一步缩小按钮区域宽度
button_frame = tk.Frame(app)
button_frame.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)

# 右侧信息展示框架，扩大信息展示区域
info_frame = tk.Frame(app)
info_frame.grid(row=2, column=1, sticky="nswe", padx=10, pady=10)

# 左侧操作按钮，按钮区域宽度和高度缩小一半
start_button = tk.Button(button_frame, text="追忆之旅", command=on_click, font=("Segoe UI", 10), width=10, height=1)
start_button.pack(pady=5)

stop_button = tk.Button(button_frame, text="休息一下", command=on_stop, font=("Segoe UI", 10), width=10, height=1)
stop_button.pack(pady=5)

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
