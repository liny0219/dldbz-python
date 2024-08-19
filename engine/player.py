from utils.config_loader import config_loader
from utils.ocr_utils import extract_value_credential_from_result,my_str2int
from utils.image_process import match_pic_coord,match_pic_coord_k
import utils.loger as loger
from functools import partial
from engine.comparator import Comparator
from contextlib import contextmanager
from utils.wait import wait_until, wait_until_not
from utils.status import ROLE_HP_STATUS, ROLE_MP_STATUS, MATCH_CONFIDENCE
# from engine.battle import RoundRecord
import cv2
import time

hpmp_location = config_loader.get("battle.role_info.role_hpmp_location")

class Role:
    def __init__(self, name):
        # 角色名, 例: "塞拉斯"
        self.name = name 

        # 技能列表 ["普通攻击", "1技能", "2技能", "3技能", "4技能"]
        self.skill_list = config_loader("roles."+name+".skill_list")

        # 角色初始化时, 默认未加入队伍
        self.player = None
        self.team = None
        self.role_id_team = None
        self.position_team = None

        # 角色参数
        self.hp = None
        self.mp = None
        self.bp = None
        self.shield = None
        self.buffs = []
        self.debuffs = []
        


    #角色加入队伍时调用
    def enter_team(self, team, role_id_team):
        #队伍名称
        self.team = team
        #队伍内角色编号
        self.role_id_team = role_id_team 

        #如果team是一个BattleTeam, 就需要有操控者以及角色站位
        if isinstance(team, BattleTeam):
            #角色的操控者就是队伍的操控者
            self.player = team.player
            # 队伍内角色站位(角色站位在战斗中会变化 )
            # 注:初始加入team时, 角色站位就是队伍内的位置
            self.position_team = self.role_id_team 

    # 角色离开队伍时调用
    def leave_team(self):
        self.team = None
        self.player = None
        self.role_id_team = None
        self.position_team = None

    # 检查是否已经加入队伍
    def in_team(self):
        if isinstance(self.team, Team):
            return True 
        return False

    # 检查是否在队伍前排
    def in_front(self):
        if self.in_team() and self.position_team <= 4:
            return True 
        return False 
    
    def check_status(self):
        pass
    def get_battle_status(self):
        # 置信度初始化
        self.hp_conf, self.mp_conf = 0.0, 0.0
        # position号位的HpMp读取范围
        crd1, crd2 = hpmp_location[ self.position_team - 1 ]
        # 如果置信度在90%以下, 重新判断
        while self.hp_conf<0.9 or self.mp_conf<0.9:
            self.player.comparator.crop_save_image('hpmp.jpg',leftup_coordinate = crd1, rightdown_coordinate = crd2)
            result = self.player.comparator.ocr('hpmp.jpg',cls=True)
            self.hp, self.hp_conf = result[0][0][1]
            self.mp, self.mp_conf = result[0][1][1]
        self.hp = int(self.hp.replace(',',''))
        self.mp = int(self.mp.replace(',',''))

    def get_bp(self):
        pass


class Team:
    def __init__(self, alias=''):
        # roles的index称之为role_id, 与角色绑定
        self.roles = {1:None, 2:None, 3:None, 4:None, 
                      5:None, 6:None, 7:None, 8:None }
        self.alias = alias
        
    #把id号位角色踢出队伍    
    def discard_role(self,id):
        if isinstance(self.roles[id], Role):
            self.roles[id].leave_team()
        self.roles[id] = None 

    #把role加到队伍内id号位
    def add_role(self, role, id):
        if self.roles[id] == None:
            self.roles[id] = role
            role.enter_team(self, id)
        else:
            print(f"The {id}-th role is occupied, please discard it first.")


class BattleTeam(Team):

    def __init__(self, player):
        super().__init__()
        #BattleTeam的操控者
        self.player = player

        self.controller   = self.player.controller
        self.comparator   = self.player.comparator

        # 前排. front的index称之为front_id, 不与角色绑定
        self.front = {1:None, 2:None, 3:None, 4:None}

        # 后排. rear的index称之为rear_id, 不与角色绑定
        self.behind = {1:None, 2:None, 3:None, 4:None}
        
    def add_role(self, role, id):
        if self.roles[id] == None:
            self.roles[id] = role
            role.enter_team(self, id)
            position = id2position(id)
            if role.in_front():
                self.front[position] = role 
            else:
                self.behind[position] = role
        else:
            print(f"The {id}-th role is occupied, please discard it first.")


    def check_front_role_status(self):
        shield = cv2.imread('./refs/battle/shield.png')
        credential = 0.0
        #只要置信度的最小值比0.9小就重新采样
        while credential<0.9:
            cred = []
            img = self.controller.capture_screenshot()
            # 看当前截图前四个最像护盾的位置存不存在护盾
            shield_coords = match_pic_coord_k(img, shield,k=4)
            find_shield = shield_coords is not None
            # 如果截到了盾牌
            if find_shield:
                #每个拥有盾牌的角色的数据范围
                sh_imgs = [img[y-5:y+50,x+50:x+120] for x,y in shield_coords]
                #读取每个拥有盾牌的角色的盾牌数和mp
                result_shs = [self.comparator.ocr.ocr(sh_img)[0] for sh_img in sh_imgs]
                #第一行数据为盾牌数
                sh_vals = [my_str2int(result_sh[0][1][0]) for result_sh in result_shs]
                #第二行数据为mp
                sh_mps = [my_str2int(result_sh[1][1][0]) for result_sh in result_shs]
                #等一秒再截一张无盾图
                time.sleep(1)
                img = self.controller.capture_screenshot()
            x1,y1 = self.front_role_status[0]
            x2, y2 = self.front_role_status[1]
            front_role_status = img[y1:y2,x1:x2]
            result = self.comparator.ocr.ocr(front_role_status)[0]
            for i in range(0, len(result), 2):
                front_role_id = i//2 + 1
                #置信度更新
                cred.append(result[i][1][1])
                cred.append(result[i+1][1][1])
                #Hp更新
                self.front[front_role_id].hp = my_str2int(result[i][1][0])
                #Mp更新
                mp = my_str2int(result[i+1][1][0])
                self.front[front_role_id].mp = mp
                #如果存在拥有盾牌的角色 且当前front_role_id的mp等于某个带盾角色的mp
                if find_shield and mp in sh_mps:
                    #获取该带盾角色的盾数
                    sh_val = sh_vals[sh_mps.index(mp)]
                    #更新该带盾角色的盾数
                    self.front[front_role_id].shield = sh_val
            #更新置信度
            credential = min(cred)
        
           
def id2position(id):
    return (id - 1) % 4 + 1

            

            










#player是玩家
class Player:
    def __init__(self, controller, comparator, team):
        self.controller = controller 
        self.comparator = comparator
        self.team = team

  
