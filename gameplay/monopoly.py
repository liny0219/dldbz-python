from __future__ import annotations
from enum import Enum
from engine.world import World
from global_data import GlobalData
from utils.config_loader import cfg_monopoly
from utils.status import MATCH_CONFIDENCE
from utils.wait import wait_until, wait_until_not
from functools import partial


class GAMEBOARD(Enum):
    DANGER_20 = 0
    DANGER_25 = 1
    DANGER_60 = 2


class Monopoly:
    def __init__(self, global_data: GlobalData):
        self.global_data = global_data
        self.controller = global_data.controller
        self.comparator = global_data.comparator
        self.world = World(global_data)
        self.meet_little_man = False
        self.game_over = False
        self.set_config()

    def set_config(self):
        self.check_play_board_refs = cfg_monopoly.get('check.check_play_board_refs')
        self.check_in_monopoly_menu_refs = cfg_monopoly.get('check.check_in_monopoly_menu_refs')
        self.check_exhaust_everything_refs = cfg_monopoly.get('check.check_exhaust_everything_refs')
        self.check_monopoly_setting_refs = cfg_monopoly.get('check.check_monopoly_setting_refs')
        self.check_play_refs = cfg_monopoly.get('check.check_play_refs')
        self.check_waitroll_refs = cfg_monopoly.get('check.check_waitroll_refs')
        self.check_little_man_refs = cfg_monopoly.get('check.check_little_man_refs')
        self.check_confirm_refs = cfg_monopoly.get('check.check_confirm_refs')
        self.check_props_found_refs = cfg_monopoly.get('check.check_props_found_refs')
        self.check_get_props_refs = cfg_monopoly.get('check.check_get_props_refs')

        self.check_dedicate_refs = cfg_monopoly.get('check.check_dedicate_refs')

        self.first_forked_road_refs = cfg_monopoly.get('check.first_forked_road_refs')
        self.second_forked_road_refs = cfg_monopoly.get('check.second_forked_road_refs')
        self.third_forked_road_refs = cfg_monopoly.get('check.third_forked_road_refs')
        self.fourth_forked_road_refs = cfg_monopoly.get('check.fourth_forked_road_refs')

        self.check_choose_coin_type_refs = cfg_monopoly.get('check.check_choose_coin_type_refs')
        self.check_end_refs = cfg_monopoly.get('check.check_end_refs')

        self.check_card_of_wealth = cfg_monopoly.get('check.check_card_of_wealth_refs')
        self.check_card_of_authority = cfg_monopoly.get('check.check_card_of_authority_refs')
        self.check_card_of_fame = cfg_monopoly.get('check.check_card_of_fame_refs')

        self.check_battle_ui_refs = cfg_monopoly.get('battle.check.check_battle_ui_refs')
        self.check_battle_monster_bear = cfg_monopoly.get('battle.check.check_battle_monster_bear_refs')
        self.check_battle_monster_fire_refs = cfg_monopoly.get('battle.check.check_battle_monster_fire_refs')
        self.check_battle_monster_girl_refs = cfg_monopoly.get('battle.check.check_battle_monster_girl_refs')
        self.check_battle_monster_red_dress_refs = cfg_monopoly.get('battle.check.check_battle_monster_red_dress_refs')

        self.minus_ticket_coord = cfg_monopoly.get('button.minus_ticket_coord')
        self.add_difficulty_coord = cfg_monopoly.get('button.add_difficulty_coord')
        self.add_ticket_num_coord = cfg_monopoly.get('button.add_ticket_num_coord')
        self.move_down_coord = cfg_monopoly.get('button.move_down_coord')
        self.move_left_coord = cfg_monopoly.get('button.move_left_coord')
        self.move_right_coord = cfg_monopoly.get('button.move_right_coord')
    # def goto(self, board : GAMEBOARD):
        self.forked_road_actions = {'first_forked_road': self.move_down_coord,
                                    'second_forked_road': self.move_left_coord,
                                    'third_forked_road': self.move_down_coord,
                                    'fourth_forked_road': self.move_down_coord}

    def start(self):
        self.world.back_menu1()
        wait_until(self.controller.in_game, operate_funcs=[
                   self.controller.start_game], check_interval=1, thread=self.global_data.thread)
        ticket_num = 0
        difficulty = 1
        self.play_monopoly(ticket_num, difficulty)
        self.check_get_props()
        self.check_coin_type_branch()
        self.check_and_choose_coin_type(coin_type='wealth')
        self.check_and_choose_forked_road()
        self.play_monopoly(ticket_num, difficulty)
        self.check_and_confirm_props_found()
        self.comparator.template_in_picture('./refs/monopoly/props_found.png')
        self.test_a_roll()
        # self.check_end_and_continue()
        # self.check_dedicate_and_cancle()
        self.check_get_props()
        print(self.check_forked_road())
        self.check_little_man()
        self.check_and_fight_and_continue()
        # self.exhaust_everything()
        self.move_right()
        for i in range(10):
            print("turn", i)
            r = self.global_data.battle._in_battle()
            print(r)

    def check_have_dice(self):
        return self.comparator.template_in_picture(self.check_waitroll_refs, return_center_coord=True)

    def check_have_dice_or_game_over(self):
        if self.game_over:
            return True
        return self.check_have_dice()

    def roll_dice(self):
        # event_roll = self.comparator.template_in_picture(self.check_waitroll_refs, return_center_coord=True)
        have_dice = self.check_have_dice()
        if have_dice:
            self.controller.press(have_dice, T=200, operate_latency=500)
            self.controller.press(have_dice, T=200)

    def check_props_found(self):
        return self.comparator.template_in_picture(self.check_props_found_refs, return_center_coord=True)

    def check_and_confirm_props_found(self):
        have_props_found = self.check_props_found()
        if have_props_found:
            x = have_props_found[0]
            y = have_props_found[1] + 128
            self.controller.light_press([x, y])

    def random_press(self):
        self.controller.light_press([94, 80])

    def test_a_roll(self, coin_type='wealth'):
        self.roll_dice()
        wait_until(self.check_have_dice_or_game_over,
                   operate_funcs=[self.random_press,
                                  partial(self.check_little_man, coin_type=coin_type),
                                  self.check_and_confirm_props_found,
                                  self.check_and_choose_forked_road,
                                  partial(self.check_dedicate_and_continue, willing=False),
                                  self.check_and_fight_and_continue,
                                  self.check_game_over_and_continue], thread=self.global_data.thread)
        # 由于有时候会往后退再次遇到事件所以要check两次
        if not self.check_have_dice():
            wait_until(self.check_have_dice,
                       operate_funcs=[self.random_press,
                                      partial(self.check_little_man, coin_type=coin_type),
                                      self.check_and_confirm_props_found,
                                      self.check_and_choose_forked_road,
                                      partial(self.check_dedicate_and_continue, willing=False),
                                      self.check_and_fight_and_continue], thread=self.global_data.thread)

    def check_get_props(self):
        return self.comparator.template_in_picture(self.check_get_props_refs)

    def check_little_man(self, coin_type='wealth'):
        if not self.meet_little_man:
            event = self.comparator.template_in_picture(self.check_little_man_refs, return_center_coord=True)
            if event:
                self.controller.press(event, T=2000)
                self.meet_little_man = True
                wait_until(self.check_coin_type_branch, operate_funcs=[
                           self.random_press], thread=self.global_data.thread)
                wait_until_not(self.check_coin_type_branch, operate_funcs=[
                               partial(self.choose_coin_type, coin_type=coin_type)], thread=self.global_data.thread)

    def check_coin_type_branch(self):
        return self.comparator.template_in_picture(self.check_choose_coin_type_refs)

    def choose_coin_type(self, coin_type):
        if coin_type == 'wealth':
            self.controller.light_press([334, 270])
        elif coin_type == 'authority':
            self.controller.light_press([624, 272])
        elif coin_type == 'fame':
            self.controller.light_press([334, 352])

    def check_and_choose_coin_type(self, coin_type):
        if self.check_coin_type_branch():
            self.choose_coin_type(coin_type)

    def check_forked_road(self):
        first_forked_road = self.comparator.template_in_picture(self.first_forked_road_refs, leftup_coordinate=[
                                                                704, 340], rightdown_coordinate=[762, 438])
        if first_forked_road:
            return 'first_forked_road'
        second_forked_road = self.comparator.template_in_picture(self.second_forked_road_refs, leftup_coordinate=[
                                                                 42, 224], rightdown_coordinate=[110, 266])
        if second_forked_road:
            return 'second_forked_road'
        third_forked_road = self.comparator.template_in_picture(self.third_forked_road_refs, leftup_coordinate=[
                                                                296, 140], rightdown_coordinate=[348, 212])
        if third_forked_road:
            return 'third_forked_road'
        fourth_forked_road = self.comparator.template_in_picture(self.fourth_forked_road_refs, leftup_coordinate=[
                                                                 598, 348], rightdown_coordinate=[670, 408])
        if fourth_forked_road:
            return 'fourth_forked_road'

    def check_and_choose_forked_road(self):
        have_forked_road = self.check_forked_road()
        if have_forked_road:
            action_coord = self.forked_road_actions[have_forked_road]
            self.controller.light_press(action_coord)

    def check_dedicate(self):
        return self.comparator.template_in_picture(self.check_dedicate_refs)

    def check_dedicate_and_continue(self, willing=False):
        if self.check_dedicate():
            if willing:
                self.controller.light_press([626, 312])
            else:
                self.controller.light_press([336, 312])

    def check_wealth_route(self):
        event = self.comparator.template_in_picture(self.check_wealth, return_center_coord=True)
        if event:
            self.controller.press(event)

    def check_authority_route(self):
        event = self.comparator.template_in_picture(self.check_authority, return_center_coord=True)
        if event:
            self.controller.press(event)

    def check_fame_route(self):
        event = self.comparator.template_in_picture(self.check_fame, return_center_coord=True)
        if event:
            self.controller.press(event)

    def check_wealth_card(self):
        event = self.comparator.template_in_picture(self.check_card_of_wealth, return_center_coord=True)
        if event:
            self.controller.press(event)

    def check_authority_card(self):
        event = self.comparator.template_in_picture(self.check_card_of_authority, return_center_coord=True)
        if event:
            self.controller.press(event)

    def check_fame_card(self):
        event = self.comparator.template_in_picture(self.check_card_of_fame, return_center_coord=True)
        if event:
            self.controller.press(event)

    def check_boss(self):
        if self.comparator.template_in_picture(self.check_battle_monster_bear, match_level=MATCH_CONFIDENCE.VERY_LOW):
            return "Bear"
        elif self.comparator.template_in_picture(self.check_battle_monster_fire_refs, match_level=MATCH_CONFIDENCE.VERY_LOW):
            return "Fire"
        elif self.comparator.template_in_picture(self.check_battle_monster_girl_refs, match_level=MATCH_CONFIDENCE.VERY_LOW):
            return "Girl"
        elif self.comparator.template_in_picture(self.check_battle_monster_red_dress_refs, match_level=MATCH_CONFIDENCE.VERY_LOW):
            return "Red_Dress"
        else:
            return "Others"

    def check_in_battle(self):
        return self.comparator.template_in_picture(self.check_battle_ui_refs)

    def check_boss_and_fight(self):
        # 后续还要优化, 暂时只能委托
        boss = self.check_boss()
        if boss:
            print(boss)
            self.controller.light_press([368, 484])
            self.controller.light_press([834, 490])
            wait_until_not(self.check_in_battle, timeout=300, check_interval=3, thread=self.global_data.thread)

    def check_and_fight_and_continue(self):
        in_battle = self.check_in_battle()
        if in_battle:
            self.check_boss_and_fight()
            wait_until(self.check_get_props, operate_funcs=[
                       self.random_press], timeout=20, thread=self.global_data.thread)
            wait_until_not(self.check_get_props, operate_funcs=[partial(
                self.controller.light_press, [480, 474])], thread=self.global_data.thread)

    def check_end(self):
        return self.comparator.template_in_picture(self.check_end_refs)

    def check_game_over_and_continue(self):
        if self.check_end():
            self.controller.light_press([486, 416])
            self.game_over = True

    def move_down(self):
        self.controller.press(self.move_down_coord)

    def move_right(self):
        self.controller.press(self.move_right_coord)

    def move_left(self):
        self.controller.press(self.move_left_coord)

    def in_monopoly_game(self):
        return self.comparator.template_in_picture(self.check_waitroll_refs)

    def in_monopoly_menu(self):
        return self.comparator.template_in_picture(self.check_in_monopoly_menu_refs)

    def in_monopoly_setting(self):
        return self.comparator.template_in_picture(self.check_monopoly_setting_refs)

    def start_playing_exhaust_everything(self, ticket_num=0, difficulty=0):
        # 运行此函数时必须在menu1界面
        wait_until(self.in_monopoly_menu, operate_funcs=[partial(
            self.controller.press, [454, 464], operate_latency=1000)], thread=self.global_data.thread)
        while True:
            if self.global_data.thread.stopped():
                # 如果线程结束则直接
                print("Thread has ended. 1")
                break
            wait_until(self.in_monopoly_setting, operate_funcs=[partial(
                self.controller.press, [694, 376]), partial(self.controller.press, [844, 452])], thread=self.global_data.thread)
            self.initialize_monopoly_setting()
            self.add_ticket_num(ticket_num)
            self.add_difficulty(difficulty)
            wait_until(self.in_monopoly_game, operate_funcs=[partial(
                self.controller.press, [598, 430])], thread=self.global_data.thread)
            self.game_over = False
            while not self.game_over:
                if self.global_data.thread.stopped():
                    # 如果线程结束则直接
                    print("Thread has ended. 2")
                    break
                self.test_a_roll()

    def play_monopoly(self, ticket_num=0, difficulty=0):
        """
        Open the game if it is not opened.

        This function first call `world.back_menu1` to go back to the menu where the monopoly game button is.
        Then it press the monopoly game button if it exists.
        Finally, it waits until the monopoly game menu appears.

        This function is often used in the `world`'s `loop` method to ensure that the monopoly game is opened before the game loop starts.
        """
        self.world.back_menu1()
        self.start_playing_exhaust_everything(ticket_num=ticket_num, difficulty=difficulty)

    def initialize_monopoly_setting(self):
        self.controller.light_press(self.minus_ticket_coord, T=100)

    def add_ticket_num(self, n):
        for _ in range(n):
            self.controller.light_press(self.add_ticket_coord, T=100)

    def add_difficulty(self, n):
        for _ in range(n):
            self.controller.light_press(self.add_difficulty_coord, T=100)


# others

    # def check_and_click_play_board(self):
    #     event = self.comparator.template_in_picture(self.check_play_board_refs, return_center_coord=True)
    #     if event:
    #         self.controller.press(event)

    # def check_and_click_exhaust_everything(self):
    #     event = self.comparator.template_in_picture(self.check_exhaust_everything_refs, return_center_coord=True)
    #     if event:
    #         self.controller.press(event)
