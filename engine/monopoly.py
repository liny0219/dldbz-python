from enum import Enum
from utils.config_loader import config_loader
from utils.status import MATCH_CONFIDENCE
class GAMEBOARD(Enum):
    DANGER_20 = 0
    DANGER_25 = 1
    DANGER_60 = 2
    

class Monopoly:
    def __init__(self, player):
        self.player = player
        self.controller   = player.controller
        self.comparator   = player.comparator

        self.meet_little_man = False


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

    def check_confirm(self):
        event = self.comparator.template_in_picture(self.check_confirm_refs, return_center_coord=True)
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
    # def move_up(self):
    #     self.controller.press([558, 246])