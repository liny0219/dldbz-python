import subprocess
import shutil
import os


def run_pyinstaller(spec_file):
    """执行 PyInstaller 打包命令."""
    try:
        # 执行 pyinstaller 打包命令
        subprocess.run(['pyinstaller', spec_file], check=True)
        print(f"打包成功: {spec_file}")
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        exit(1)


def copy_files_and_directories(dest_dir, items_to_copy):
    """
    将指定的文件和目录复制到目标目录.

    :param dest_dir: EXE 文件的目标目录
    :param items_to_copy: 要复制的文件和目录列表 [(源路径, 目标路径), ...]
    """
    for src, dst in items_to_copy:
        dst_path = os.path.join(dest_dir, dst)

        try:
            if os.path.isdir(src):
                # 如果是目录，复制整个目录
                shutil.copytree(src, dst_path, dirs_exist_ok=True)
                print(f"复制目录: {src} 到 {dst_path}")
            else:
                # 如果是文件，复制文件
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src, dst_path)
                print(f"复制文件: {src} 到 {dst_path}")
        except Exception as e:
            print(f"复制失败: {e}")


def clean_dist_directory(dist_dir):
    """删除 dist 目录."""
    if os.path.exists(dist_dir):
        try:
            shutil.rmtree(dist_dir)
            print(f"已删除 dist 目录: {dist_dir}")
        except Exception as e:
            print(f"删除 dist 目录失败: {e}")
            exit(1)


def main():
    # 指定你的 .spec 文件
    spec_file = 'main.spec'

    # 定义 dist 目录路径
    dist_dir = 'dist'

    # 删除 dist 目录
    clean_dist_directory(dist_dir)

    # 运行 pyinstaller 打包
    run_pyinstaller(spec_file)

    # 定义 EXE 文件所在的目录（通常是 dist 目录下的同名文件夹）
    exe_dir = dist_dir  # EXE 文件名默认放在 dist 目录中

    # 定义要复制的文件和目录 [(源路径, 目标路径)]
    items_to_copy = [
        ('./battle_script', 'battle_script'),  # 将 external_folder 复制到 EXE 同级目录
        ('./config', 'config')  # 将 config.yaml 文件复制到 EXE 同级 config 目录中
        # 你可以根据需要继续添加更多目录或文件
    ]

    # 复制指定的目录和文件到 EXE 的同级目录
    copy_files_and_directories(exe_dir, items_to_copy)


if __name__ == '__main__':
    main()
