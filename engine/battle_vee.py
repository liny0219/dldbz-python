from engine.battle_hook import BattleHook
import utils.loger as loger
from utils.config_loader import cfg_battle
from functools import partial
from contextlib import contextmanager
from utils.singleton import singleton
from utils.wait import wait_limit, wait_until, wait_until_not, wait_either
from utils.status import ROLE_HP_STATUS, ROLE_MP_STATUS, MATCH_CONFIDENCE
from utils.load import load_battle_configurations
import time

def get_front_front_role_id(role):    # 获某号位站到前排的index
    assert role > 0 & role <= 8   # 最多有8号位
    return (role - 1) % 4


def get_front_role_order(role):  # 获得n号位的前排序号
    return get_front_front_role_id(role) + 1


battle_hook = BattleHook()


@singleton
class Battle:
    def __init__(self, player, alias=''):
        self.player = player
        self.controller = player.controller
        self.comparator = player.comparator
        self.alias = alias
        self.team = player.team
        self.front = [1, 2, 3, 4]
        self.behind = [5, 6, 7, 8]
        self.thread = None
        self.battle_end = False
        self.in_round_ctx = False
        # self.current_record = None
        self.round_number = 0
        self.round_records = []

        load_battle_configurations(self)
        battle_hook.set('CmdStart', lambda: not self.thread.stopped())
        battle_hook.set('RoundStart', lambda: self.WaitRound())
        battle_hook.set('Role', lambda role_id, skill_id, energy_level: self.Skill(
            int(role_id), int(skill_id), int(energy_level)))
        battle_hook.set('XRole', lambda role_id, skill_id, energy_level: self.Skill(
            int(role_id) + 4, int(skill_id), int(energy_level)))
        battle_hook.set(
            'Attack', lambda: self.StartAttack(lambda: self.WaitRound()))
        battle_hook.set('SwitchAll', lambda: self.SwitchAll())
        battle_hook.set('Boost', lambda: self.Boost())
        battle_hook.set('SP', lambda role_id: self.SP(int(role_id)))
        # battle_hook.set('Reset', lambda: self.reset())
        # battle_hook.set('Switch', lambda role_id: self.switch(role_id))
        # battle_hook.set('Wait', lambda time: self.wait(time))
        # battle_hook.set('Skip', lambda time: self.skip(time))

    def __enter__(self):
        wait_until(self._in_battle, thread=self.thread)  # 等待进入战斗
        loger.log_info(f"进入战斗“{self.alias}”!")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print('Battle end!')
        # wait_until_not(self._in_battle, self._confirm_exit_battle)

    def _in_round(self):
        in_round = self._in_battle() and self.comparator.template_in_picture(
            self.check_round_ui_refs)
        return in_round

    def _in_battle(self):
        return self.comparator.template_in_picture(self.check_battle_ui_refs)

    def _not_in_battle(self):
        return not self._in_battle()

    # 当前回合的attack只有在进入新的回合或者战斗结束时才会结束
    def _attack_end(self):
        # 进入新回合内 或者 战斗结束
        attack_end = self._in_round() or (not self._in_battle())
        return attack_end

    def _in_select_skill(self):
        in_select_skill = self._in_battle() and self.comparator.template_in_picture(
            self.check_skill_ui_refs)
        return in_select_skill

    def _confirm_exit_battle(self):
        fallback_coord = self.comparator.template_in_picture(
            self.fallback_refs, return_center_coord=True)
        if fallback_coord:
            return [partial(self.controller.press, self.confirm_coord),
                    partial(self.controller.press, fallback_coord)]   # 点击撤退按钮
        return [partial(self.controller.press, self.confirm_coord)]   # 点击

    def SetThread(self, thread):
        self.thread = thread

    def WaitRound(self, round_number=0):
        if round_number:
            self.round_number = round_number
        self.round_number = self.round_number + 1
        self.in_round_ctx = True
        loger.log_info(f"进入回合{self.round_number}！")
        wait_until(self._in_round, [partial(
            self.controller.press, self.confirm_coord)], thread=self.thread)     # 等待在回合中

    def StartAttack(self, cb=None):
        loger.log_info("开始攻击！")
        self._start_attack()
        # 等待攻击键消失
        wait_until_not(self._in_round, [partial(
            self.controller.press, self.confirm_coord)], thread=self.thread)  # 等待退出回合
        # 等待攻击结束
        end_condition = wait_either(
            self._in_round, self._not_in_battle, thread=self.thread)
        if end_condition == 2:
            self.battle_end = True
        # self.round_records.append(self.current_record)
        self.in_round_ctx = False
        if cb:
            cb()

    def _start_attack(self):
        attack_coord = self.comparator.template_in_picture(
            self.attack_refs, return_center_coord=True)
        if (attack_coord):
            self.controller.press(attack_coord)  # 开始战斗

    def _check_role_status_without_log(self, role):
        def _role_config(role, keyword):
            sider_str = "front"
            if (role > 4):
                sider_str = "behind"
            config_str = f"{sider_str}_role.{keyword}"
            return cfg_battle.get(config_str)

        front_role_id = get_front_front_role_id(role)

        role_rect = _role_config(role, "role_rect")[front_role_id]
        dead_refs = _role_config(role, "hp.dead_refs")
        hp_mid_refs = _role_config(role, "hp.hp_mid_refs")
        hp_high1_refs = _role_config(role, "hp.hp_high1_refs")
        hp_high2_refs = _role_config(role, "hp.hp_high2_refs")

        mp_high_refs = _role_config(role, "mp.mp_high_refs")

        mp_status = ROLE_MP_STATUS.LOW
        hp_status = ROLE_HP_STATUS.LOW

        # 因为低血量会闪烁，所以置信度设为最低
        # 检测蓝量
        mp_high = self.comparator.template_in_picture(
            mp_high_refs, *role_rect, match_level=MATCH_CONFIDENCE.LOW)
        if mp_high:
            mp_status = ROLE_MP_STATUS.HIGH

        # 检测血量
        is_dead = self.comparator.template_in_picture(
            dead_refs, *role_rect, match_level=MATCH_CONFIDENCE.LOW)
        if is_dead:
            hp_status = ROLE_HP_STATUS.DEAD
            return (hp_status, mp_status)

        hp_high1 = self.comparator.template_in_picture(
            hp_high1_refs, *role_rect, match_level=MATCH_CONFIDENCE.LOW)
        hp_high2 = self.comparator.template_in_picture(
            hp_high2_refs, *role_rect, match_level=MATCH_CONFIDENCE.LOW)
        if hp_high1 or hp_high2:
            hp_status = ROLE_HP_STATUS.HIGH
            return (hp_status, mp_status)

        hp_mid = self.comparator.template_in_picture(
            hp_mid_refs, *role_rect, match_level=MATCH_CONFIDENCE.LOW)
        if hp_mid:
            hp_status = ROLE_HP_STATUS.MID
            return (hp_status, mp_status)

        return (hp_status, mp_status)

    def check_role_status(self, role):
        loger.log_info(f"正在获取{role}号位的血量、精力...")
        hp, mp = self._check_role_status_without_log(role)
        loger.log_info(f"{role}号位的血量为{hp}，精力为{mp}")
        return (hp, mp)

    def Skill(self, role, skill, boost=0):
        assert self.in_round_ctx == True  # 必须在Round中执行
        assert role > 0 & role <= 8   # 最多有8号位
        assert skill >= 0 & skill <= 4  # 最多有4个技能(战斗为0)
        assert boost >= 0 & boost <= 3  # 最多boost三个豆

        loger.log_info(f"执行{role}号位的{skill}技能, boost{boost}!...")

        front_role_id = get_front_front_role_id(role)

        # 点击角色, 等待进入选技能界面
        select_role_coord = [self.role_coord_x,
                             self.role_coords_y[front_role_id]]
        self.controller.press(select_role_coord)
        # wait_until(self._in_select_skill, [partial(self.controller.press, select_role_coord)])
        loger.log_info(f"进入选技能界面!")
        role_in_behind = (role in self.behind)
        # 切换人物
        if (role_in_behind):
            loger.log_info(f"切换人物!")
            switch_coord = self.comparator.template_in_picture(
                self.switch_refs, return_center_coord=True)
            if (switch_coord):
                self.controller.press(switch_coord)
                self.front[front_role_id], self.behind[front_role_id] = self.behind[front_role_id],  self.front[front_role_id]

        loger.log_info(f"正在选中技能!")
        skill_start = [self.skill_coord_x, self.skill_coords_y[skill]]
        skill_end = [self.boost_coords_x[boost], self.skill_coords_y[skill]]
        # 滑动+点击确认，等待在回合中
        wait_until(self._in_round, [partial(self.controller.light_swipe, skill_start, skill_end),
                                    partial(self.controller.light_press, self.confirm_coord)], thread=self.thread)

        loger.log_info("释放技能执行完毕")

        # self.current_record.change(role, skill, boost)

    def SwitchAll(self):
        self.front, self.behind = self.behind, self.front  # 交换前后两位
        all_switch_coord = self.comparator.template_in_picture(
            self.all_switch_refs,  return_center_coord=True)
        print(all_switch_coord)
        if (all_switch_coord):
            self.controller.press(all_switch_coord, T=0.5)

    def Boost(self):
        all_boost_coord = self.comparator.template_in_picture(
            self.all_boost_refs,  return_center_coord=True)
        print(all_boost_coord)
        if (all_boost_coord):
            self.controller.press(all_boost_coord, T=0.5)

    def SP(self, role):
        assert self.in_round_ctx == True  # 必须在Round中执行
        assert role > 0 & role <= 8   # 最多有8号位

        loger.log_info(f"执行{role}号位的必杀技能!")

        front_role_id = get_front_front_role_id(role)

        # 点击角色, 等待进入选技能界面
        select_role_coord = [self.role_coord_x,
                             self.role_coords_y[front_role_id]]
        self.controller.press(select_role_coord)
        # wait_until(self._in_select_skill, [partial(self.controller.press, select_role_coord)])
        loger.log_info(f"进入选技能界面!")
        role_in_behind = (role in self.behind)
        # 切换人物
        if (role_in_behind):
            loger.log_info(f"切换人物!")
            switch_coord = self.comparator.template_in_picture(
                self.switch_refs, return_center_coord=True)
            if (switch_coord):
                self.controller.press(switch_coord)
                self.front[front_role_id], self.behind[front_role_id] = self.behind[front_role_id],  self.front[front_role_id]

        loger.log_info(f"正在选中必杀!")

        self.controller.press(self.sp_coords)
        time.sleep(0.4)
        self.controller.press(self.sp_confirm_coords)
