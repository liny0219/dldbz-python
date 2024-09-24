import subprocess
import os


def run_cython_build():
    # 确定 setup.py 文件是否存在
    if not os.path.exists("tool_setup.py"):
        print("Error: tool_setup.py file not found in the current directory.")
        return

    # 构建命令
    command = ["python", "tool_setup.py", "build_ext", "--inplace"]

    # 执行命令
    try:
        print("Running Cython build...")
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 尝试使用 gbk 编码解码 stdout
        try:
            print(result.stdout.decode('utf-8'))
        except UnicodeDecodeError:
            print("UTF-8 解码失败，尝试使用 gbk 解码...")
            print(result.stdout.decode('gbk', errors='ignore'))

        print("Build completed successfully.")

    except subprocess.CalledProcessError as e:
        # 如果出现错误，打印错误信息
        try:
            print(f"Build failed with error:\n{e.stderr.decode('utf-8')}")
        except UnicodeDecodeError:
            print("UTF-8 解码失败，尝试使用 gbk 解码错误信息...")
            print(f"Build failed with error:\n{e.stderr.decode('gbk', errors='ignore')}")
        return


if __name__ == "__main__":
    run_cython_build()
