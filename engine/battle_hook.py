
from utils.singleton import singleton

@singleton
class BattleHook:
    def __init__(self):
        # 初始化默认的 hook 函数为打印行为
        self.hooks = {
            "Role": self.default_role_hook,
            "XRole": self.default_xrole_hook,
            "FullEnergy": self.default_full_energy_hook,
            "Attack": self.default_attack_hook,
            "SwitchAll": self.default_switch_all_hook
        }

        # 保存原始的默认 hook 函数
        self.default_hooks = self.hooks.copy()

    def set(self, command, hook_func):
        """设置对应指令的 hook 函数，并保留默认行为"""
        if command in self.hooks:
            def wrapped_hook(*args, **kwargs):
                # 调用默认的行为
                self.default_hooks[command](*args, **kwargs)
                # 然后调用用户自定义的行为
                hook_func(*args, **kwargs)
            self.hooks[command] = wrapped_hook
        else:
            print(f"Warning: Unknown command '{command}'.")

    def get(self, command):
        """获取对应指令的 hook 函数"""
        return self.hooks.get(command, None)

    # 默认的打印行为 hook 函数
    def default_role_hook(self, role_id, skill_id, energy_level):
        print(f"Default Role Hook: Role {role_id}, Skill {skill_id}, Energy {energy_level}")

    def default_xrole_hook(self, role_id, skill_id, energy_level):
        print(f"Default XRole Hook: Role {role_id}, Skill {skill_id}, Energy {energy_level}")

    def default_full_energy_hook(self):
        print("Default FullEnergy Hook: Set energy to Full.")

    def default_attack_hook(self):
        print("Default Attack Hook: Executed Attack.")

    def default_switch_all_hook(self):
        print("Default SwitchAll Hook: Switched all roles between front and back rows.")
