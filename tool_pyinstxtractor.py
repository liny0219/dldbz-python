import os
import subprocess
from utils.config_loader import cfg_version


def run_extraction(version, relative_path):
    # 构建相对路径
    exe_file = os.path.join(relative_path, "publish", "package", f"大霸茶馆v{version}.exe")

    # 检查文件是否存在
    if not os.path.exists(exe_file):
        print(f"Error: 文件 {exe_file} 不存在.")
        return

    # 构建命令
    command = ["python", "pyinstxtractor.py", exe_file]

    # 执行命令
    try:
        print(f"正在提取 {exe_file} ...")
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 打印执行结果，尝试使用 gbk 编码或者忽略错误
        try:
            print(result.stdout.decode('utf-8'))
        except UnicodeDecodeError:
            print("UTF-8 解码失败，尝试使用 gbk 解码...")
            print(result.stdout.decode('gbk', errors='ignore'))

        print("提取完成.")

    except subprocess.CalledProcessError as e:
        # 如果出现错误，打印错误信息
        try:
            print(f"提取失败:\n{e.stderr.decode('utf-8')}")
        except UnicodeDecodeError:
            print("UTF-8 解码失败，尝试使用 gbk 解码错误信息...")
            print(f"提取失败:\n{e.stderr.decode('gbk', errors='ignore')}")


if __name__ == "__main__":
    # 设置版本号和相对路径
    version = cfg_version.get("version")  # 修改为你的版本号
    relative_path = "."  # 修改为你所需的相对路径, 可以用 "." 表示当前目录

    # 调用提取函数
    run_extraction(version, relative_path)
