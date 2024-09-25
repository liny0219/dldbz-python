from app_data import app_data
from engine.battle_pix import battle_pix
from utils.config_loader import reload_config, cfg_monopoly, cfg_startup


class config:
    cfg_ticket = 0
    cfg_lv = 0
    cfg_net_retry = 1
    cfg_type = ""
    cfg_crossing = ""
    cfg_auto_battle = 0
    cfg_isContinue = 0
    cfg_check_interval = 0
    cfg_check_roll_dice_interval = 0
    cfg_check_roll_dice_time = 0
    cfg_check_roll_rule = 0
    cfg_check_roll_rule_wait = 0
    cfg_bp_type = ""
    cfg_r801 = ""
    cfg_r802 = ""
    cfg_r803 = ""
    cfg_enemy_map = {}
    cfg_action_map = {}
    cfg_enemy_match_threshold = 0
    cfg_enemy_check = 0
    cfg_round_time = 0
    cfg_wait_time = 0
    cfg_exe_path = ""


def set_config():
    reload_config()
    battle_pix.set(app_data)
    try:
        config.cfg_ticket = int(cfg_monopoly.get("ticket"))
        config.cfg_lv = int(cfg_monopoly.get("lv"))
        config.cfg_type = cfg_monopoly.get("type")
        config.cfg_crossing = cfg_monopoly.get(f"crossing.{config.cfg_type}")
        config.cfg_auto_battle = int(cfg_monopoly.get("auto_battle"))
        config.cfg_isContinue = int(cfg_monopoly.get("isContinue"))
        config.cfg_check_interval = float(cfg_monopoly.get("check_interval"))
        config.cfg_check_roll_dice_interval = float(cfg_monopoly.get("check_roll_dice_interval"))
        config.cfg_check_roll_dice_time = int(cfg_monopoly.get("check_roll_dice_time"))
        config.cfg_check_roll_rule = int(cfg_monopoly.get("check_roll_rule"))
        config.cfg_check_roll_rule_wait = float(cfg_monopoly.get("check_roll_rule_wait"))
        config.cfg_bp_type = cfg_monopoly.get("bp_type")
        config.cfg_r801 = cfg_monopoly.get("bp.801")
        config.cfg_r802 = cfg_monopoly.get("bp.802")
        config.cfg_r803 = cfg_monopoly.get("bp.803")
        config.cfg_enemy_map = cfg_monopoly.get("enemy")
        config.cfg_action_map = cfg_monopoly.get("action")
        config.cfg_enemy_match_threshold = float(cfg_monopoly.get("enemy_match_threshold"))
        config.cfg_enemy_check = int(cfg_monopoly.get("enemy_check"))
        config.cfg_round_time = int(cfg_monopoly.get("round_time"))*60
        config.cfg_wait_time = int(cfg_monopoly.get("wait_time"))*60
        config.cfg_exe_path = cfg_startup.get("exe_path")
        return True
    except Exception as e:
        app_data.update_ui(f"{e}")
        return False
