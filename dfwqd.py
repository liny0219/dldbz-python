import os
import time
from fun.tools import backworld
from engine.device_controller import DeviceController
from engine.world import World
from engine.comparator import Comparator
from utils.config_loader import config_loader

current_path = os.path.dirname(os.path.abspath(__file__))
assert_path = './refs/dfw/'


def run_task():
    while True:
        event = comparator.template_in_picture(assert_path +  'dfwysz.png')
        if event:
            controller.d.click(853, 435)
        time.sleep(1)


# 分支 1富足 2权威 3名望
# 代币类型 1富足 2权威 3名望
# 随机事件 1 左边加难度 2右边减难度
def run(ticket_number, difficulty, wealth, coin_type, random_event):
    # backworld()
    # 打开大富翁
    event = comparator.template_in_picture(assert_path +  'monopoly_game_board.png', return_center_coord=True)
    if event:
        controller.press(event)

    while True:
        # 选择穷极之人游戏盘
        event = comparator.template_in_picture(assert_path +  'game_board_exhaust_everything.png', return_center_coord=True)
        if event:
            controller.press(event)
            # 游玩选难度和票
            event = comparator.template_in_picture(assert_path +  'play.png', return_center_coord=True)
            if event:
                controller.press(event)
                controller.d.click(243, 215)  # 0票
                for i in range(0, ticket_number):
                    controller.d.click(371, 220)  # 加票
                for i in range(0, difficulty):
                    controller.d.click(718, 212)  # 加难度
                # 开始游玩
                event = comparator.template_in_picture(assert_path +  'play2.png', return_center_coord=True)
                if event:
                    controller.press(event)
                ysz(wealth, coin_type, random_event)


def ysz(wealth, coin_type, random_event):
    xzfz = 1
    little_man = 1

    while True:
        # 摇塞子
        event_ysz = comparator.template_in_picture(assert_path +  'role_dice.png')
        if event_ysz:
            controller.press((853, 435), T=200, operate_latency=1000)
        # 确定
        event = comparator.template_in_picture(assert_path +  'monopoly_confirm.png', return_center_coord=True)
        if event:
            controller.press(event)
        # 确定
        event = comparator.template_in_picture(assert_path +  'monopoly_confirm2.png', return_center_coord=True)
        if event:
            controller.press(event)
        # 长按跳过
        if little_man == 1:
            event = comparator.template_in_picture(assert_path +  'little_man.png', return_center_coord=True)
            if event:
                controller.press(event, 2000)
                little_man = 0
        # 路线选择
        if wealth == 1 and xzfz == 1:
            # 富足路线
            event = comparator.template_in_picture(assert_path +  'wealth_route.png', return_center_coord=True)
            if event:
                controller.press(event)
                cl1xz = 1
        elif wealth == 2 and xzfz == 1:
            # 权威路线
            event = comparator.template_in_picture(assert_path +  'authority_route.png', return_center_coord=True)
            if event:
                controller.press(event)
                xzfz = 0
        elif wealth == 3 and xzfz == 1:
            # 名望路线
            event = comparator.template_in_picture(assert_path +  'fame_route.png', return_center_coord=True)
            if event:
                controller.press(event)
                xzfz = 0

        event = comparator.template_in_picture(assert_path +  'card_of_fame.png', return_center_coord=True)
        if event:
            # 选择名望的卡片
            if coin_type == 3:
                controller.press(event)
            # 选择富足的卡片
            elif coin_type == 1:
                event = comparator.template_in_picture(assert_path +  'card_of_wealth.png', return_center_coord=True)
                if event:
                    controller.press(event)
            # 选择权威的卡片
            elif coin_type == 2:
                event = comparator.template_in_picture(assert_path +  'card_of_authority.png', return_center_coord=True)
                if event:
                    controller.press(event)

        # 战斗委托
        event = comparator.template_in_picture(assert_path +  'attack.png')
        if event:
            controller.d.click(367, 478)
            # 战斗委托开始
            controller.sleep_ms(500)
            event = comparator.template_in_picture(assert_path +  'dz_wtks.png', return_center_coord=True)
            if event:
                controller.press(event)

        # event = comparator.template_in_picture(assert_path +  'sj3.png', return_center_coord=True)
        # if event:
        #     controller.press(event)
        event = comparator.template_in_picture(assert_path +  'js1.png')
        
        if event:
            break

        controller.d.click(391, 250)  # 向左
        controller.d.click(391, 250)  # 向左
        controller.d.click(477, 341)  # 向下
        controller.d.click(477, 341)  # 向下
            # controller.d.click(564, 250)  # 向右
        # 摇塞子
        event_ysz = comparator.template_in_picture(assert_path +  'role_dice.png')
        if event_ysz:
            controller.d.click(853, 435)
            controller.d.click(853, 435)
            controller.d.click(853, 435)

        if random_event == 1:
            controller.d.click(335, 308)
            controller.d.click(335, 308)

        if random_event == 2:
            controller.d.click(564, 250)
            controller.d.click(564, 250)



if __name__ == '__main__':
    controller = DeviceController(config_loader.get('adb_port'))
    comparator = Comparator(controller)
    world = World(controller, comparator)

    # thread1 = threading.Thread(target=run_task)
    # thread1.start()

    # 分支 1富足 2权威 3名望
    # 代币类型 1富足 2权威 3名望
    # 随机事件 1 左边加难度 2右边减难度

    ticket_number = 0
    difficulty = 2
    wealth = 1
    coin_type = 3
    random_event = 1

    run(ticket_number, difficulty, wealth, coin_type, random_event)
