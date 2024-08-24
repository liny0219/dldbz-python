import os

from engine.device_controller import DeviceController
from engine.world import  World
from engine.comparator import Comparator
from utils.config_loader import cfg_startup

current_path = os.path.dirname(os.path.abspath(__file__))
assert_path = './ref/dfw/'

controller = DeviceController(cfg_startup.get('adb_port'))
comparator = Comparator(controller)
world = World(controller, comparator)
operate_latency = 1000
def backworld():
    while True:
        # #开始游戏
        # event = comparator.template_in_picture(assert_path +  'begin_game.png', return_center_coord=True)
        # if event:
        #     controller.press(event,operate_latency=operate_latency)
        #点掉菜单
        # event = comparator.template_in_picture(assert_path +  'others.png', return_center_coord=True)
        # if event:
        #     controller.press((516, 316),operate_latency=operate_latency)
        #点掉打叉
        event = comparator.template_in_picture(assert_path +  'cross1.png', return_center_coord=True)
        if event:
            controller.press(event,operate_latency=operate_latency)
        event = comparator.template_in_picture(assert_path +  'cross2.png', return_center_coord=True)
        if event:
            controller.press(event,operate_latency=operate_latency)
        event = comparator.template_in_picture(assert_path +  'cancel.png', return_center_coord=True)
        if event:
            controller.press(event,operate_latency=operate_latency)
        event = comparator.template_in_picture(assert_path +  'No.png', return_center_coord=True)


        if event:
            controller.press(event,operate_latency=operate_latency)
        event = comparator.template_in_picture(assert_path +  'monopoly_game_board.png', return_center_coord=True)
        if event:
            print("Back to the world, and find the monopoly game board.")
            break




