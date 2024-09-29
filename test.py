from utils.config_loader import cfg_monopoly
from engine.comparator import comparator
from engine.world import world
from engine.u2_device import u2_device
from engine.battle_pix import battle_pix
from gameplay.monopoly.index import Monopoly
import os
u2_device.connect()
cfg_enemy_map = cfg_monopoly.get("enemy")
cfg_action_map = cfg_monopoly.get("action")
update_ui = print
# test find enemy
# def on_get_enmey():
#     screenshot = comparator._screenshot_cropped_image(convert_gray=False)
#     enemy = cfg_enemy_map.get('802')
#     action = cfg_action_map.get('802')
#     current_enemy = None

#     if not enemy or not action:
#         return

#     for key, value in enemy.items():
#         if not value:
#             continue
#         update_ui(f"开始匹配敌人{key}")

#         normalized_path =  os.path.normpath(value)
#         result = comparator.template_compare(
#             normalized_path, [(15, 86), (506, 448)],
#             return_center_coord=True,
#             match_threshold=0.5,
#             screenshot=screenshot, pack=False)
#         print(result)

#         if result:
#             current_enemy = key
#             update_ui(f"匹配到敌人{current_enemy}")
#             break
#         else:
#             update_ui(f"未匹配到敌人{key}")
#     if not current_enemy:
#         update_ui("未匹配到任何敌人")
#         return

#     current_action = action.get(current_enemy)
#     if not current_action:
#         update_ui(f"未找到敌人{current_enemy}的行动")
#         return
#     for value in current_action:
#         if len(value) == 0:
#             continue
#         parts = value.split(',')
#         command = parts[0]
#         update_ui(f"执行命令{command}")
#         if command == "Click":
#             x = int(parts[1])
#             y = int(parts[2])
#             engine.press([x, y])

# print(battle_pix.is_in_battle())
# on_get_enmey()
# a = cfg_monopoly.get('enemy')
# print(type(a))
# print(a.get('802'))


# test event
def check_evtent():
    update_ui("check-事件", 'debug')
    screenshot = comparator._screenshot_cropped_image(convert_gray=False)
    coord = comparator.template_compare(f"./assets/monopoly/btn_options.png",
                                        return_center_coord=True, screenshot=screenshot)
    if coord:
        update_ui("find-事件", 'debug')
        x, y = coord
        offfset = 120
        u2_device.device.click(x + offfset, y)
        return True
    return False


check_evtent()
