from engine.battle_hook import BattleHook
from utils.singleton import singleton


@singleton
class BattleDSL:
    def __init__(self, updateUI=None):
        # 使用 BattleHook 单例管理 hooks
        self.hook_manager = BattleHook()
        self.updateUI = updateUI
        self.instructions = []  # 用于存储预读取的指令列表

    def load_instructions(self, filename):
        """ 从文件中预读取指令并存储 """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.instructions = [line.strip() for line in file if line.strip() and not line.startswith('#')]
            if self.updateUI:
                self.updateUI("指令加载成功。")
        except Exception as e:
            if self.updateUI:
                self.updateUI(f"读取指令出错 {filename}. {e}")

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
            # 更新 UI
            if self.updateUI:
                self.updateUI(f"找不到对应战斗指令 '{command}'.")
        return True

    def run_script(self):
        """ 执行预加载的指令 """
        for instruction in self.instructions:
            is_continue = self.execute_instruction(instruction)
            if not is_continue:
                break
        # 文件读取完毕，执行 Finish Hook
        finish_hook = self.hook_manager.get('Finish')
        if finish_hook:
            finish_hook()
