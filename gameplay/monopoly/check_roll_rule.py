import json
from app_data import app_data
from gameplay.monopoly.config import config


def check_roll_rule(number):
    if not number:
        app_data.update_ui("检查距离失败", 'debug')
        return 0
    try:
        rules_map = {
            "801": config.cfg_r801,
            "802": config.cfg_r802,
            "803": config.cfg_r803
        }
        rule = rules_map.get(config.cfg_type, "")
        if not rule:
            return 0
        rule_json = f"[{rule}]"
        ranges = json.loads(rule_json)
        for start, end, bp in ranges:
            if start >= number > end:
                return bp
        return 0
    except Exception as e:
        app_data.update_ui(f"检查自定义扔骰子规则出现异常 {str(e)}")
        return 0
