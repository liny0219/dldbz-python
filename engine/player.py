from utils.config_loader import config_loader


hpmp_location = config_loader("battle.role_info.role_hpmp_location")

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
    
    def get_battle_status(self):
        # 置信度初始化
        self.hp_conf, self.mp_conf = 0.0, 0.0
        # position号位的HpMp读取范围
        crd1, crd2 = hpmp_location[ self.position_team - 1 ]
        # 如果置信度在90%以下, 重新判断
        while self.hp_conf<0.9 or self.mp_conf<0.9:
            self.player.eyes.crop_save_image('hpmp.jpg',leftup_coordinate = crd1, rightdown_coordinate = crd2)
            result = self.player.ocr.ocr('hpmp.jpg',cls=True)
            self.hp, self.hp_conf = result[0][0][1]
            self.mp, self.mp_conf = result[0][1][1]
        self.hp = int(self.hp.replace(',',''))
        self.mp = int(self.mp.replace(',',''))

    def get_bp(self):
        pass


class Team:
    def __init__(self):
        # roles的index称之为role_id, 与角色绑定
        self.roles = {1:None, 2:None, 3:None, 4:None, 
                      5:None, 6:None, 7:None, 8:None }
        
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

        # 前排. front的index称之为front_id, 不与角色绑定
        self.front = {1:None, 2:None, 3:None, 4:None}

        # 后排. rear的index称之为rear_id, 不与角色绑定
        self.rear = {1:None, 2:None, 3:None, 4:None}
        



#player是大脑
class Player:
    def __init__(self, controller, comparator, team):
        self.hands = controller 
        self.eyes = comparator
        self.team = team

    