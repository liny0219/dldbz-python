import subprocess
import shutil
import os
import json
import zipfile


def zip_directory(source_dir, output_dir, output_zip_name):
    """将指定目录压缩成 ZIP 文件并输出到指定目录."""
    # 创建输出目录（如果不存在）
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 生成输出 ZIP 文件的完整路径
    output_zip = os.path.join(output_dir, output_zip_name)

    # 压缩目录为 ZIP 文件
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                # 将文件写入 ZIP，并保持相对路径
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(source_dir, '..')))
    print(f"压缩完成，ZIP 文件已保存到: {output_zip}")


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


def update_version_in_json(json_file):
    """更新 JSON 文件中的版本号."""
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    version_parts = data['version'].split('.')
    version_parts[1] = str(int(version_parts[1]) + 1)  # 增加中间版本号
    new_version = '.'.join(version_parts)
    data['version'] = new_version
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    return new_version


def replace_version_in_spec(spec_file, new_version, output_file):
    """在 spec 文件中替换版本号，并输出到新文件."""
    with open(spec_file, 'r', encoding='utf-8') as file:
        content = file.read()
    updated_content = content.replace('${version}', new_version)
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(updated_content)


def main():
    spec_file = 'startup.spec'
    dist_dir = 'dist'
    json_file = 'config/startup.json'
    tmp_spec_file = 'tmp.spec'

    clean_dist_directory(dist_dir)

    new_version = update_version_in_json(json_file)  # 更新 JSON 文件中的版本号并获取新版本
    zip_filename = f'大霸茶馆v{new_version}.zip'
    replace_version_in_spec(spec_file, new_version, tmp_spec_file)  # 替换 spec 文件中的版本号并保存到 tmp.spec

    run_pyinstaller(tmp_spec_file)  # 使用更新后的 tmp.spec 进行打包

    exe_dir = dist_dir  # EXE 文件名默认放在 dist 目录中
    items_to_copy = [
        ('./battle_script', 'battle_script'),
        ('./config', 'config'),
        ('./data', 'data'),
    ]

    copy_files_and_directories(exe_dir, items_to_copy)
    copy_md_as_txt('readme.md', exe_dir, 'readme.txt')
    zip_directory(dist_dir, dist_dir, zip_filename)


if __name__ == '__main__':
    main()
