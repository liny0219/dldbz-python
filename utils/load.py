from utils.config_loader import config_loader


def load_controller_configurations(controller):
    controller.rand_press_px = config_loader.get("controller.rand_press_px")
    controller.press_duration = config_loader.get("controller.press_duration")
    controller.swipe_duration = config_loader.get("controller.swipe_duration")
    controller.operate_latency = config_loader.get("controller.operate_latency")
    controller.default_sleep_ms = config_loader.get("controller.default_sleep_ms")

def load_battle_configurations(instance):
    instance.check_battle_ui_refs  = config_loader.get("battle.check.check_battle_ui_refs")   # 检测战斗图片
    instance.check_round_ui_refs   = config_loader.get("battle.check.check_round_ui_refs")    # 检测回合结束图片
    instance.check_skill_ui_refs   = config_loader.get("battle.check.check_skill_ui_refs")    # 检测技能界面图片
            
    instance.role_coords_y = config_loader.get("battle.coord.role_coords_y")     # 角色y坐标
    instance.role_coord_x = config_loader.get("battle.coord.role_coord_x")      # 角色x坐标
    instance.skill_coords_y = config_loader.get("battle.coord.skill_coords_y")    # 技能y坐标
    instance.skill_coord_x  = config_loader.get("battle.coord.skill_coord_x")     # 技能x坐标
    instance.boost_coords_x = config_loader.get("battle.coord.boost_coords_x")    # boost终点x坐标
    instance.confirm_coord = config_loader.get("general.confirm_coord")     # 额外点击

    instance.switch_refs     = config_loader.get("battle.button.switch_refs")       # 前后排切换按钮图片
    instance.fallback_refs   = config_loader.get("battle.button.fallback_refs")     # 撤退按钮图片
    instance.supports_refs   = config_loader.get("battle.button.supports_refs")     # 支援者按钮图片
    instance.all_switch_refs = config_loader.get("battle.button.all_switch_refs")   # 全员交替按钮图片
    instance.all_boost_refs  = config_loader.get("battle.button.all_boost_refs")    # 全员加成按钮图片
    instance.attack_refs = config_loader.get("battle.button.attack_refs")       # “攻击”图片
