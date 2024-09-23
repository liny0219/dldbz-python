from setuptools import setup, Extension
from Cython.Build import cythonize
import os

# 自动查找项目中的所有 Python 源文件
def find_pyx_files(directory):
    pyx_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            # 排除带有 tool_ 前缀的文件
            if (file.endswith(".py") or file.endswith(".pyx")) and not file.startswith("tool_"):
                # 获取相对路径并转换成模块名称格式（将/替换为.）
                relative_path = os.path.relpath(os.path.join(root, file), directory)
                module_name = relative_path.replace(os.path.sep, ".").rsplit(".", 1)[0]
                pyx_files.append(Extension(module_name, [os.path.join(root, file)]))
    return pyx_files


# 获取所有需要编译的源文件，保留模块路径
extensions = cythonize(
    find_pyx_files("."),  # 传入当前目录
    language_level="3",  # 或 "3str" 表示 Python 3 语法
    build_dir="build/temp",  # 指定临时文件的生成目录
    compiler_directives={'language_level': "3"}  # 强制使用 Python 3 语法
)

# setup 配置
setup(
    name="大霸茶馆",
    ext_modules=extensions,
    script_args=["build_ext", "--build-lib", "build/lib"],  # 指定生成的库文件存放目录
)
