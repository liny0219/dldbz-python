import subprocess
import shutil
import os


def run_pyinstaller(spec_file):
    """执行 PyInstaller 打包命令."""
    try:
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
                shutil.copytree(src, dst_path, dirs_exist_ok=True)
                print(f"复制目录: {src} 到 {dst_path}")
            else:
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


def copy_md_as_txt(source_md, dest_dir, output_name):
    """
    将 Markdown 文件作为文本文件复制到指定目录，只更改文件扩展名。
    :param source_md: 源 Markdown 文件路径
    :param dest_dir: 目标目录
    :param output_name: 输出文件名（应包括.txt扩展名）
    """
    output_path = os.path.join(dest_dir, output_name)
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        shutil.copy2(source_md, output_path)
        print(f"已将 {source_md} 复制为 {output_path}")
    except Exception as e:
        print(f"复制文件失败: {e}")


def main():
    spec_file = 'startup.spec'
    dist_dir = 'dist'

    clean_dist_directory(dist_dir)
    run_pyinstaller(spec_file)

    exe_dir = dist_dir  # EXE 文件名默认放在 dist 目录中
    items_to_copy = [
        ('./battle_script', 'battle_script'),
        ('./config', 'config')
    ]

    copy_files_and_directories(exe_dir, items_to_copy)
    copy_md_as_txt('readme.md', exe_dir, 'readme.txt')


if __name__ == '__main__':
    main()
