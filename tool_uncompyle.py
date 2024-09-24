import subprocess
import os

def run_uncompyle6():
    # 设置相对路径
    pyc_file = os.path.join("exe_extracted", "PYZ-00.pyz_extracted", "view", "startup.cp37-win_amd64.pyd")
    
    # 构建 uncompyle6 命令
    command = ['uncompyle6', '-o', '.', pyc_file]
    
    # 运行命令
    try:
        print(f"正在反编译 {pyc_file}...")
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 打印结果
        print(result.stdout.decode())
        print("反编译完成.")
    except subprocess.CalledProcessError as e:
        # 捕获错误并打印
        print(f"反编译失败:\n{e.stderr.decode()}")

if __name__ == "__main__":
    run_uncompyle6()
