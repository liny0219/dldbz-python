import subprocess
import os


def run_cython_build():
    # 确定 setup.py 文件是否存在
    if not os.path.exists("setup.py"):
        print("Error: setup.py file not found in the current directory.")
        return

    # 构建命令
    command = ["python", "setup.py", "build_ext", "--inplace"]

    # 执行命令
    try:
        print("Running Cython build...")
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 打印执行结果
        print(result.stdout.decode())
        print("Build completed successfully.")

    except subprocess.CalledProcessError as e:
        # 如果出现错误，打印错误信息
        print(f"Build failed with error:\n{e.stderr.decode()}")
        return


if __name__ == "__main__":
    run_cython_build()
