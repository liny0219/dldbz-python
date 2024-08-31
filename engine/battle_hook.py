from utils.singleton import singleton


@singleton
class BattleHook:
    def __init__(self, log_enabled=False):
        # 控制日志输出的属性
        self.log_enabled = log_enabled

        # 初始化默认的 hook 函数，包含所有可能的指令
        self.hooks = {
            "Role": self.default_role_hook,         # 普通攻击
            "XRole": self.default_xrole_hook,       # 切换并攻击
            "Boost": self.default_boost_hook,       # 设置全能量
            "Attack": self.default_attack_hook,     # 执行攻击
            "SwitchAll": self.default_switch_all_hook,  # 切换前后排
            "SP": self.default_sp_hook,             # 特殊技能 (Skill_SP 更正为 SP)
            "Reset": self.default_reset_hook,       # 重置技能和能量
            "Switch": self.default_switch_hook,     # 切换特定角色位置
            "Wait": self.default_wait_hook,         # 等待指定时间
            "Skip": self.default_skip_hook,         # 跳过指定时间
            "BattleStart": self.default_battle_start_hook,  # 战斗开始
            "BattleEnd": self.default_battle_end_hook,  # 战斗结束
            "CmdStart": self.default_cmd_start_hook,  # 指令开始
            "CmdEnd": self.default_cmd_end_hook,      # 指令结束
            "Finish": self.default_finish_hook,  # 脚本结束后的钩子
        }
        # 保留默认行为，用于在自定义 hook 时也执行默认行为
        self.default_hooks = self.hooks.copy()

    def log(self, message):
        """ 控制日志输出的方法 """
        if self.log_enabled:
            print(message)

    def set(self, command, hook_func):
        """ 设置自定义 hook 函数，并保留默认行为 """
        if command in self.hooks:
            def wrapped_hook(*args, **kwargs):
                # 调用默认行为
                self.default_hooks[command](*args, **kwargs)
                # 调用自定义行为
                return hook_func(*args, **kwargs)
            self.hooks[command] = wrapped_hook
        else:
            print(f"Warning: Unknown command '{command}'.")

    def get(self, command):
        """ 获取对应指令的 hook 函数 """
        return self.hooks.get(command, None)

    # 以下是各指令的默认行为

    def default_role_hook(self, role_id, skill_id, energy_level, enemy_id=None, position="down"):
        direction = {
            "up": "向上",
            "down": "向下",
            "left": "向左",
            "right": "向右"
        }.get(position, "未知方向")
        self.log(f"Default Role Hook: Role {role_id}, Skill {skill_id}, Energy {
                 energy_level}, Enemy {enemy_id} at {direction}")

    def default_xrole_hook(self, role_id, skill_id, energy_level):
        self.log(f"Default XRole Hook: Role {role_id}, Skill {skill_id}, Energy {energy_level}")

    def default_boost_hook(self):
        self.log("Default Boost Hook: Set Boost to Full.")

    def default_attack_hook(self):
        self.log("Default Attack Hook: Executed Attack.")

    def default_switch_all_hook(self):
        self.log("Default SwitchAll Hook: Switched all roles between front and back rows.")

    def default_sp_hook(self, role_id):
        self.log(f"Default SP Hook: Role {role_id} used special skill.")

    def default_reset_hook(self):
        self.log("Default Reset Hook: All characters' skills and energy have been reset to 0.")

    def default_switch_hook(self, role_id):
        self.log(f"Default Switch Hook: Switched role {role_id} to a different position.")

    def default_wait_hook(self, duration):
        self.log(f"Default Wait Hook: Waiting for {duration} milliseconds.")

    def default_skip_hook(self, duration):
        self.log(f"Default Skip Hook: Skipping {duration} milliseconds (placeholder).")

    def default_battle_start_hook(self):
        self.log("Default BattleStart Hook: Battle has started.")

    def default_battle_end_hook(self):
        self.log("Default BattleEnd Hook: Battle has ended.")

    def default_cmd_start_hook(self):
        self.log("Default CmdStart Hook: cmd has started.")

    def default_cmd_end_hook(self):
        self.log("Default CmdEnd Hook: cmd has ended.")

    def default_finish_hook(self):
        self.log("Default Finish Hook: Script execution has finished.")
