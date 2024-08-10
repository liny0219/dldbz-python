from utils.config_loader import config_loader
import utils.loger as loger
import time

class BattleEngine:
    def __init__(self, controller, comparator):
        self.controller  = controller
        self.comparator  = comparator

        self.role_coords_y = \
            config_loader.get("battle.role_coords_y")     # 角色y坐标
        self.role_coord_x = \
            config_loader.get("battle.role_coord_x")      # 角色x坐标
        self.switch_coord = \
            config_loader.get("battle.switch_coord")      # 前后排切换按钮坐标

        self.skill_coords_y = \
            config_loader.get("battle.skill_coords_y")    # 技能y坐标
        self.skill_coord_x  = \
            config_loader.get("battle.skill_coord_x")     # 技能x坐标

        self.boost_coords_x = \
            config_loader.get("battle.boost_coords_x")    # boost终点x坐标
 
        self.fallback_coord   = \
            config_loader.get("battle.fallback_coord")    # 撤退按钮坐标
        self.support_coord    = \
            config_loader.get("battle.support_coord")     # 支援者按钮坐标
        self.all_switch_coord = \
            config_loader.get("battle.all_switch_coord")  # 全员交替按钮坐标
        self.all_boost_coord  = \
            config_loader.get("battle.all_boost_coord")   # 全员加成按钮坐标
        
        self.battle_coord = \
            config_loader.get("battle.battle_coord")      # “战斗”坐标
        
    def role_coord(self, role_order):
        assert role_order > 0 & role_order <= 4           # 最多有4号位

        coord_x = self.role_coord_x
        coord_y = self.role_coords_y[role_order - 1]

        return [coord_x, coord_y]
    
    def boost_coord(self, skill_order = 0):
        assert skill_order >=0 & skill_order <= 4         # 最多有4个技能(战斗为0) 

        coord_x = self.skill_coord_x
        coord_y = self.skill_coords_y[skill_order]
        return [coord_x, coord_y]

    def skill_coord(self, skill_order, boost):
        assert skill_order >= 0 & skill_order <= 4        # 最多有4个技能(战斗为0) 
        assert boost >= 0 & boost <= 3                    # 最多boost三个豆
        coord_x = self.boost_coords_x[boost]
        coord_y = self.skill_coords_y[skill_order]
        return [coord_x, coord_y]

    def in_battle(self):
        return self.comparator.match_features(config_loader.get("battle.check_battle_ui"))

    def in_round(self):
        return self.comparator.match_features(config_loader.get("battle.check_round_ui"))

    def in_select_skill(self):
        return self.comparator.match_content(*config_loader.get("battle.check_skill_text.coord_lt"),\
                                             *config_loader.get("battle.check_skill_text.coord_rb"),\
                                            config_loader.get("battle.check_skill_text.text"))

    def skill(self, role, skill, boost = 0):
        select_role_coord = self.role_coord(role)
        print(select_role_coord)
        self.controller.press(*select_role_coord)
        time.sleep(0.5)
        print("在战斗中",self.in_battle())
        print("在回合中",self.in_round())
        print("在技能界面",self.in_select_skill())

        '''
        skill_start = self.skill_coord(skill)
        if boost == 0:
            skill_end  = [skill_start[0] - self.boost_step_x, skill_start[1]]    # 如果没有boost则往回拉
        else:
            skill_end = [skill_start[0] + boost * self.boost_step_x, skill_start[1]]
        
        #self.latency_click(*skill_end)
        print(role,skill,boost)
        #self.latency_click(*skill_start)
        #self.device.swipe(*skill_start, *skill_end, steps= self.swipe_steps)
        '''