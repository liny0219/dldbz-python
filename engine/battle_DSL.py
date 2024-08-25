from engine.battle_hook import BattleHook
from utils.singleton import singleton
@singleton
class BattleDSL:
    def __init__(self):
        # 使用 BattleHook 单例管理 hooks
        self.hook_manager = BattleHook()

    def execute_instruction(self, instruction):
        hook_func_cmd_start = self.hook_manager.get('CmdStart')  # 获取对应指令的 hook 函数
        if hook_func_cmd_start is not None and not hook_func_cmd_start():
            return False

        """ 解析并执行指令 """
        parts = instruction.split(',')
        command = parts[0]  # 获取指令名称
        hook_func = self.hook_manager.get(command)

        if hook_func is not None:
            # 执行对应的 hook 函数，并传递参数
            hook_func(*parts[1:])
        else:
            print(f"Error: No hook function set for command '{command}'.")
        return True

    def run_script(self, filename):
        """ 读取配置文件并执行指令 """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    # 忽略空行和注释行
                    line = line.strip()
                    if line and not line.startswith('#'):
                        is_continue = self.execute_instruction(line)
                        if not is_continue:
                            break
            # 文件读取完毕，执行 Finish Hook
            finish_hook = self.hook_manager.get('Finish')
            if finish_hook:
                finish_hook()
        except UnicodeDecodeError:
            print(f"Error: Unable to decode the file {filename}. Please ensure it is encoded in UTF-8.")
