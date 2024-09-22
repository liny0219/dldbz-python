import psutil
import subprocess
import os
import time
import platform


class ExeManager:
    def __init__(self):
        self.exe_path = None

    # 检查应用程序是否正在运行，并返回PID
    def is_exe_running(self):
        if self.exe_path is None or len(self.exe_path) == 0:
            return None
        for process in psutil.process_iter(['pid', 'exe']):
            try:
                if process.info['exe'] == self.exe_path:
                    return process.info['pid']
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
        return None

    # 关闭已经运行的应用程序
    def stop_exe(self):
        pid = self.is_exe_running()
        if pid:
            process = psutil.Process(pid)
            print(f"正在关闭 {self.exe_path}, PID: {pid}")
            process.terminate()  # 尝试优雅地结束进程
            try:
                process.wait(timeout=5)  # 等待进程终止，最多等待5秒
            except psutil.TimeoutExpired:
                print(f"强制终止 {self.exe_path}")
                process.kill()  # 如果5秒后还未结束，强制杀死进程
        else:
            print(f"{self.exe_path} 未运行。")

    # 启动应用程序，独立于Python脚本运行
    def start_exe(self):
        if self.exe_path is None or len(self.exe_path) == 0:
            return None
        if os.path.exists(self.exe_path):
            print(f"正在启动 {self.exe_path}")
            if platform.system() == "Windows":
                # 在 Windows 上，使用 creationflags 使进程独立运行
                DETACHED_PROCESS = 0x00000008
                return subprocess.Popen(self.exe_path, shell=True, creationflags=DETACHED_PROCESS)
            else:
                # 在其他平台（如Linux、Mac），使用 start_new_session 使进程独立运行
                return subprocess.Popen(self.exe_path, shell=True, start_new_session=True)
        else:
            print(f"应用程序路径 {self.exe_path} 不存在。")
            return None

    # 重启应用程序
    def restart_exe(self):
        self.stop_exe()
        time.sleep(2)  # 等待2秒再重新启动应用程序
        self.start_exe()

    # 动态设置新的 exe 路径
    def set_exe_path(self, new_exe_path):
        if os.path.exists(new_exe_path):
            print(f"设置新的 exe 路径: {new_exe_path}")
            self.exe_path = new_exe_path
        else:
            print(f"新路径 {new_exe_path} 不存在。无法设置。")


# 示例用法
if __name__ == "__main__":
    exe_path = r"C:\path\to\your_app.exe"  # 初始exe路径
    manager = ExeManager()
    manager.set_exe_path(exe_path)

    # 调用类的方法
    manager.restart_exe()  # 重启应用程序

    # 动态设置新的 exe 路径
    new_exe_path = r"C:\new\path\to\another_app.exe"
    manager.set_exe_path(new_exe_path)

    # 使用新路径进行操作
    manager.restart_exe()  # 重启新的应用程序
