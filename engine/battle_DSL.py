
from engine.battle_hook import BattleHook
from utils.singleton import singleton

@singleton
class BattleDSL:
    def __init__(self):
        # 使用 BattleHook 单例实例来管理 hooks
        self.hook_manager = BattleHook()

    def execute_instruction(self, instruction):
        # 解析指令并执行相应的 hook 函数
        parts = instruction.split(',')
        command = parts[0]
        hook_func = self.hook_manager.get(command)

        if hook_func is not None:
            # 传递指令参数给对应的 hook 函数
            hook_func(*parts[1:])
        else:
            print(f"Error: No hook function set for command '{command}'.")

    def run_script(self, filename):
        # 读取配置文件并执行指令
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    # 忽略空行和注释行
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.execute_instruction(line)
        except UnicodeDecodeError:
            print(f"Error: Unable to decode the file {filename}. Please ensure it is encoded in UTF-8.")
