from enum import Enum
from utils.config_loader import config_loader
from utils.status import MATCH_CONFIDENCE
from utils.wait import wait_until, wait_until_not
from functools import partial

class GAMEBOARD(Enum):
    DANGER_20 = 0
    DANGER_25 = 1
    DANGER_60 = 2
    

class Monopoly:
    def __init__(self, player, world):
        self.player = player
        self.controller   = player.controller
        self.comparator   = player.comparator
        self.world = world

        self.meet_little_man = False

        self.check_play_board_refs = config_loader.get('monopoly.check.check_play_board_refs')
        self.check_in_monopoly_menu_refs = config_loader.get('monopoly.check.check_in_monopoly_menu_refs')
        self.check_exhaust_everything_refs = config_loader.get('monopoly.check.check_exhaust_everything_refs')
        self.check_monopoly_setting_refs = config_loader.get('monopoly.check.check_monopoly_setting_refs')
        self.check_play_refs = config_loader.get('monopoly.check.check_play_refs')
        self.check_waitroll_refs = config_loader.get('monopoly.check.check_waitroll_refs')
        self.check_little_man_refs = config_loader.get('monopoly.check.check_little_man_refs')
        self.check_confirm_refs = config_loader.get('monopoly.check.check_confirm_refs')
        self.check_wealth = config_loader.get('monopoly.check.check_wealth_refs')
        self.check_authority = config_loader.get('monopoly.check.check_authority_refs')
        self.check_fame = config_loader.get('monopoly.check.check_fame_refs')
        self.check_card_of_wealth = config_loader.get('monopoly.check.check_card_of_wealth_refs')
        self.check_card_of_authority = config_loader.get('monopoly.check.check_card_of_authority_refs')
        self.check_card_of_fame = config_loader.get('monopoly.check.check_card_of_fame_refs')
        self.check_battle_ui_refs = config_loader.get('battle.check.check_battle_ui_refs')
        self.check_battle_monster_bear = config_loader.get('monopoly.battle.check.check_battle_monster_bear_refs')
        self.check_battle_monster_fire_refs = config_loader.get('monopoly.battle.check.check_battle_monster_fire_refs')
        self.check_battle_monster_girl_refs = config_loader.get('monopoly.battle.check.check_battle_monster_girl_refs')
    # def goto(self, board : GAMEBOARD):
        

    def roll_dice(self):  
        event_roll = self.comparator.template_in_picture(self.check_waitroll_refs, return_center_coord=True)
        if event_roll:
            self.controller.press(event_roll, T=200, operate_latency=1000)
            self.controller.press(event_roll, T=200)
        
    def check_little_man(self):
        if not self.meet_little_man:
            event = self.comparator.template_in_picture(self.check_little_man_refs, return_center_coord=True)
            if event:
                self.controller.press(event, T=2000)
                self.meet_little_man = True

    def check_and_confirm(self):
        event = self.comparator.template_in_picture(self.check_confirm_refs, return_center_coord=True)
        if event:
            self.controller.press(event)
    def check_and_play(self):
        event = self.comparator.template_in_picture(self.check_play_refs, return_center_coord=True)
        if event:
            self.controller.press(event)

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

    def in_battle(self):
        if not self.comparator.template_in_picture(self.check_battle_ui_refs):
            return None 
        else:
            if self.comparator.template_in_picture(self.check_battle_monster_bear, match_level = MATCH_CONFIDENCE.VERY_LOW):
                return "Bear"
            elif self.comparator.template_in_picture(self.check_battle_monster_fire_refs, match_level = MATCH_CONFIDENCE.VERY_LOW):
                return "Fire"
            elif self.comparator.template_in_picture(self.check_battle_monster_girl_refs, match_level = MATCH_CONFIDENCE.VERY_LOW):
                return "Girl"
            
    def move_down(self):
        self.controller.press([482, 336])
    def move_right(self):
        self.controller.press([560, 246])
    def move_left(self):
        self.controller.press([404, 246])
    def in_monopoly_game(self):
        return self.comparator.template_in_picture(self.check_waitroll_refs)
    def in_monopoly_menu(self):
        return self.comparator.template_in_picture(self.check_in_monopoly_menu_refs)
    # def check_and_click_play_board(self):
    #     event = self.comparator.template_in_picture(self.check_play_board_refs, return_center_coord=True)
    #     if event:
    #         self.controller.press(event)
    
    def check_and_click_exhaust_everything(self):
        event = self.comparator.template_in_picture(self.check_exhaust_everything_refs, return_center_coord=True)
        if event:
            self.controller.press(event)
    def in_monopoly_setting(self):
        return self.comparator.template_in_picture(self.check_monopoly_setting_refs)
    def start_playing_exhaust_everything(self, ticket_num=0,difficulty=0):
        #运行此函数时必须在menu1界面
        wait_until(self.in_monopoly_menu, operate_funcs=[partial(self.controller.press, [454, 464])] )
        wait_until(self.in_monopoly_setting, operate_funcs=[partial(self.controller.press, [694, 376]), partial(self.controller.press, [844, 452])] )
        self.initialize_monopoly_setting()
        self.add_ticket_num(ticket_num)
        self.add_difficulty(difficulty)
        wait_until(self.in_monopoly_game, operate_funcs=[partial(self.controller.press, [598, 430])] )

    def play_monopoly(self, ticket_num=0,difficulty=0):
        """
        Open the game if it is not opened.

        This function first call `world.back_menu1` to go back to the menu where the monopoly game button is.
        Then it press the monopoly game button if it exists.
        Finally, it waits until the monopoly game menu appears.

        This function is often used in the `world`'s `loop` method to ensure that the monopoly game is opened before the game loop starts.
        """
        self.world.back_menu1()
        self.start_playing_exhaust_everything(ticket_num=ticket_num,difficulty=difficulty)

    def initialize_monopoly_setting(self):
        self.controller.light_press([246, 222],T = 100)
    def add_ticket_num(self,n):
        for _ in range(n):
            self.controller.light_press([372, 222],T = 100)
    def add_difficulty(self,n):
        for _ in range(n):
            self.controller.light_press([716, 222],T = 100)