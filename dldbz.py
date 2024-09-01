from engine.device_controller import DeviceController
from engine.world import Move_Direct, World
from engine.battle import Battle
from engine.comparator import Comparator
from engine.player import Player
from engine.monopoly import Monopoly
from utils.config_loader import config_loader
from utils.wait import wait_until
import cv2 

if __name__ == '__main__':
    controller = DeviceController("127.0.0.1:5555")
    comparator = Comparator(controller)
    team = 'TBD'
    player = Player(controller, comparator, team)
    world      = World(player)
    monopoly = Monopoly(player,world)
    # world.back_menu1()
    # wait_until(controller.in_game, operate_funcs=[controller.start_game],check_interval=1)
    # monopoly.exhaust_everything()
    ticket_num = 0
    difficulty = 1
    print(monopoly.detect_scenario())
    # monopoly.play_monopoly(ticket_num, difficulty)
    # monopoly.check_get_props()
    # monopoly.check_coin_type_branch()
    # monopoly.check_and_choose_coin_type(coin_type='wealth')
    # monopoly.check_and_choose_forked_road()
    # monopoly.play_monopoly(ticket_num, difficulty)
    # monopoly.check_and_confirm_props_found()
    # comparator.template_in_picture('./refs/monopoly/props_found.png')
    # monopoly.test_a_roll()
    # monopoly.check_end_and_continue()
    # monopoly.check_dedicate_and_cancle()
    # monopoly.check_get_props()
    # print(monopoly.check_forked_road())
    # monopoly.check_little_man()
    # monopoly.check_and_fight_and_continue()
    # monopoly.exhaust_everything()
    # monopoly.move_right()
    # for i in range(10):
    #     print("turn",i)
    #     r = monopoly.in_battle()
    #     print(r)
    # 截图示例
    '''
    #comparator.crop_save_image([879, 369], [910, 386], "your_file_name")
    '''
    
    # 查看1-8号位战斗状态，准确度不高，待优化
    '''
    with Battle(controller, comparator, '测试') as battle:
        battle.check_role_status(1)
        battle.check_role_status(2)
        battle.check_role_status(3)
        battle.check_role_status(4)
        battle.check_role_status(5)
        battle.check_role_status(6)
        battle.check_role_status(7)
        battle.check_role_status(8)
    '''
    
    # 战斗示例

    # with Battle(player, '测试') as b:
    #     while not b.battle_end:
    #         with b.Round() as r1:
    #             r1.skill(5, 0, 3)
    #             r1.skill(6, 1, 3)
    #             r1.skill(7, 2, 0)
    #             r1.skill(8, 3, 3)
    #         if b.battle_end:
    #             break 
    #         with b.Round() as r2:
    #             r2.skill(1, 0, 3)
    #             r2.skill(2, 1, 3)
    #             r2.skill(3, 2, 3)
    #             r2.skill(4, 3, 3)
                    
    # with Battle(player, alias="My Battle") as battle:
    #     with battle.Round() as round:
    #         # Code to be executed during the round
    #         battle.skill(1, 2, boost=1)  # Execute skill 2 with boost 1 for role 1
    #         battle.check_role_status(2)  # Check status of role 2
    #         # More code to be executed during the round
    #     # Code to be executed after the round
    #     print("Round ended")

    # with Battle(player, alias="My Battle") as battle:
    #     while battle.player.health > 0:
    #         with battle.Round() as round:
    #             # Code to be executed during the round
    #             battle.skill(1, 2, boost=1)  # Execute skill 2 with boost 1 for role 1
    #             battle.check_role_status(2)  # Check status of role 2
    #             # More code to be executed during the round
    #         # Code to be executed after the round
    #         print("Round ended")
    #     print("Battle ended")
    # 移动示例，下一步要添加一个移动状态的判断，暂时未实现
    # world.move_once(Move_Direct.LEFT_RIGHT)
    # world.move_until_not_in_world(Move_Direct.LEFT_RIGHT)   # 有bug,需要修改

