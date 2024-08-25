import tkinter as tk
from engine.recollection import recollection
from utils.stoppable_thread import StoppableThread

# 示例任务

def on_close():
    print("Closing the application...")
    on_stop()  # 停止当前线程
    app.quit()  # 退出主循环
    app.destroy()  # 销毁窗口

def evt_recollection(thread: StoppableThread):
    # 避免变量与函数或模块名称冲突
    recollection_instance = recollection(thread)
    recollection_instance.start()

def on_click():
    global current_thread
    if current_thread is not None and current_thread.is_alive():
        print(f"{current_thread.name} is already running.")
        return
    # 创建并启动一个可关闭的线程来运行耗时任务
    current_thread = StoppableThread(target=lambda: evt_recollection(current_thread))
    current_thread.start()

def on_stop():
    if current_thread is not None:
        current_thread.stop()

# 创建主窗口
app = tk.Tk()
app.title("Simple GUI")
app.geometry("300x200")
# 设置关闭事件处理
app.protocol("WM_DELETE_WINDOW", on_close)

# 标签
label = tk.Label(app, text="Click the button to start a long task")
label.pack(pady=20)

# 停止按钮
stop_button = tk.Button(app, text="停止", command=on_stop)  # 设置按钮宽度
stop_button.place(x=100, y=50, width=100, height=30)  #

# 启动按钮
start_button = tk.Button(app, text="追忆之书挂机", command=on_click)
start_button.place(x=100, y=90, width=100, height=30)  #


current_thread = None  # 全局变量来存储当前的线程引用

# 运行主循环
app.mainloop()
