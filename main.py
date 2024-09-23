
import sys
import os

# 添加编译后 .pyd 文件的路径到 sys.path
sys.path.insert(0, os.path.abspath('build/lib'))
from view.startup import AppModule
# 确保加载的是编译后的模块
if __name__ == "__main__":
    app = AppModule()
    app.run()
