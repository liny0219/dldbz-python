from engine.battle_hook import BattleHook
import utils.loger as loger
from utils.config_loader import cfg_battle
from functools import partial
from utils.singleton import singleton
from utils.wait import wait_until, wait_until_not, wait_either
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
    def __init__(self, player, alias='', updateUI=None):
        self.finish_hook = None
        self.updateUI = updateUI

        self.player = player
        self.controller = player.controller
        self.comparator = player.comparator
        self.alias = alias
        self.team = player.team
        self.front = [1, 2, 3, 4]
        self.behind = [5, 6, 7, 8]

        self.battle_end = False
        self.in_round_ctx = False
        self.round_number = 0
        self.round_records = []

        load_battle_configurations(self)

        # 设置 Hook 函数，返回值为 bool 类型，表示是否继续执行
        battle_hook.set(
            'Finish', lambda: self.finish_hook and self.finish_hook())
        battle_hook.set('CmdStart', lambda: not self.thread.stopped())
        battle_hook.set('BattleStart', lambda: self.WaitRound(True))
        battle_hook.set('BattleEnd', lambda: self.BattleEnd())
        battle_hook.set('Role', lambda role_id, skill_id, energy_level: self.Skill(
            int(role_id), int(skill_id), int(energy_level)))
        battle_hook.set('XRole', lambda role_id, skill_id, energy_level: self.Skill(
            int(role_id) + 4, int(skill_id), int(energy_level)))
        battle_hook.set('Attack', lambda: self.StartAttack(
            lambda: self.WaitRound()))
        battle_hook.set('SwitchAll', lambda: self.SwitchAll())
        battle_hook.set('Boost', lambda: self.Boost())
        battle_hook.set('SP', lambda role_id: self.SP(int(role_id)))
        battle_hook.set('Wait', lambda time: self.Wait(time))
        battle_hook.set('Skip', lambda time: self.Skip(time))

    def __enter__(self):
        start_time = time.time()
        wait_until(self._in_battle, thread=self.thread)  # 等待进入战斗
        self.log_info(f"进入战斗“{self.alias}”! 耗时：{time.time() - start_time:.2f} 秒")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.log_info('战斗结束！')
        # wait_until_not(self._in_battle, self._confirm_exit_battle)

    def _in_round(self):
        in_round = self._in_battle() and self.comparator.template_in_picture(
            self.check_round_ui_refs)
        return in_round

    def _in_battle(self):
        return self.comparator.template_in_picture(self.check_battle_ui_refs)

    def _not_in_battle(self):
        return not self._in_battle()

    def _attack_end(self):
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

    def setThread(self, thread):
        self.thread = thread

    def reset(self):
        self.battle_end = False
        self.in_round_ctx = False
        self.round_number = 0
        self.round_records = []

    def WaitRound(self, resetRound=False, newRound=True):
        start_time = time.time()
        inRound = wait_until(self._in_round, [partial(
            self.controller.press, self.confirm_coord, press_duration=10, operate_latency=10)], thread=self.thread)
        if inRound and newRound:
            if resetRound == True:
                self.round_number = 0
            self.round_number += 1
            self.in_round_ctx = True
            self.log_info(f"进入回合{self.round_number}！ 耗时：{time.time() - start_time:.2f} 秒")
        else:
            inBattle = self._in_battle()
            if not inBattle:
                self.Skip(2000)
            else:
                if self.thread.stopped():
                    self.log_info(f"self.thread.stopped")
                    return False
            return True

    def StartAttack(self, cb=None):
        start_time = time.time()
        self.log_info("开始攻击！")
        self._start_attack()
        wait_until_not(self._in_round, [partial(
            self.controller.press, self.confirm_coord)], thread=self.thread)
        end_condition = wait_either(
            self._in_round, self._not_in_battle, thread=self.thread)
        if end_condition == 2:
            self.battle_end = True
        self.in_round_ctx = False
        if cb:
            cb()
        self.log_info(f"攻击结束！耗时：{time.time() - start_time:.2f} 秒")

    def _start_attack(self):
        attack_coord = self.comparator.template_in_picture(
            self.attack_refs, return_center_coord=True)
        if attack_coord:
            self.controller.press(attack_coord)  # 开始战斗

    def check_role_status(self, role):
        self.log_info(f"正在获取{role}号位的血量、精力...")
        hp, mp = self._check_role_status_without_log(role)
        self.log_info(f"{role}号位的血量为{hp}，精力为{mp}")
        return (hp, mp)

    def Skill(self, role, skill, boost=0):
        assert self.in_round_ctx == True  # 必须在Round中执行
        assert role > 0 & role <= 8   # 最多有8号位
        assert skill >= 0 & skill <= 4  # 最多有4个技能(战斗为0)
        assert boost >= 0 & boost <= 3  # 最多boost三个豆

        start_time = time.time()
        self.log_info(f"执行{role}号位的{skill}技能, boost {boost}!...")

        front_role_id = get_front_front_role_id(role)
        select_role_coord = [self.role_coord_x,
                             self.role_coords_y[front_role_id]]
        self.controller.press(select_role_coord)
        self.log_info(f"进入选技能界面!")
        role_in_behind = (role in self.behind)
        if role_in_behind:
            self.log_info(f"切换人物!")
            switch_coord = self.comparator.template_in_picture(
                self.switch_refs, return_center_coord=True)
            if switch_coord:
                self.controller.press(switch_coord)
                self.front[front_role_id], self.behind[front_role_id] = self.behind[front_role_id],  self.front[front_role_id]

        self.log_info(f"正在选中技能!")
        skill_start = [self.skill_coord_x, self.skill_coords_y[skill]]
        skill_end = [self.boost_coords_x[boost], self.skill_coords_y[skill]]
        wait_until(self._in_round, [partial(self.controller.light_swipe, skill_start, skill_end),
                                    partial(self.controller.light_press, self.confirm_coord)], thread=self.thread)
        self.log_info(f"技能执行完毕，耗时：{time.time() - start_time:.2f} 秒")

    def SwitchAll(self):
        start_time = time.time()
        self.front, self.behind = self.behind, self.front
        all_switch_coord = self.comparator.template_in_picture(
            self.all_switch_refs,  return_center_coord=True)
        if all_switch_coord:
            self.controller.press(all_switch_coord, T=0.5)
        self.log_info(f"前后排切换完成，耗时：{time.time() - start_time:.2f} 秒")

    def Boost(self):
        start_time = time.time()
        all_boost_coord = self.comparator.template_in_picture(
            self.all_boost_refs,  return_center_coord=True)
        if all_boost_coord:
            self.controller.press(all_boost_coord, T=0.5)
        self.log_info(f"全能量提升完成，耗时：{time.time() - start_time:.2f} 秒")

    def SP(self, role):
        assert self.in_round_ctx == True  # 必须在Round中执行
        assert role > 0 & role <= 8   # 最多有8号位

        start_time = time.time()
        self.log_info(f"执行{role}号位的必杀技能!")

        front_role_id = get_front_front_role_id(role)
        select_role_coord = [self.role_coord_x,
                             self.role_coords_y[front_role_id]]
        self.controller.press(select_role_coord)
        self.log_info(f"进入选技能界面!")
        role_in_behind = (role in self.behind)
        if role_in_behind:
            self.log_info(f"切换人物!")
            switch_coord = self.comparator.template_in_picture(
                self.switch_refs, return_center_coord=True)
            if switch_coord:
                self.controller.press(switch_coord)
                self.front[front_role_id], self.behind[front_role_id] = self.behind[front_role_id],  self.front[front_role_id]

        self.log_info(f"正在选中必杀!")
        self.controller.press(self.sp_coords)
        time.sleep(0.4)
        self.controller.press(self.sp_confirm_coords)
        self.log_info(f"必杀技执行完毕，耗时：{time.time() - start_time:.2f} 秒")

    def Wait(self, time_in_ms):
        time_in_seconds = int(time_in_ms) / 1000.0
        self.log_info(f"等待 {time_in_ms} 毫秒...")
        time.sleep(time_in_seconds)

    def Skip(self, time_in_ms):
        self.log_info(f"跳过 {time_in_ms} 毫秒...")
        self.controller.press(self.confirm_coord, int(time_in_ms))

    def BattleEnd(self):
        self.log_info(f"战斗结束...")

    def setFinishHook(self, finish_hook):
        self.finish_hook = finish_hook

    def log_info(self, message):
        loger.log_info(message)
        if self.updateUI:
            self.updateUI(message)
