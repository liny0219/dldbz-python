
from __future__ import annotations
from typing import TYPE_CHECKING
from engine.battle_DSL import BattleDSL
import utils.loger as loger
from functools import partial
from utils.singleton import singleton
from utils.wait import wait_until, wait_until_not, wait_either
from utils.config_loader import cfg_common, cfg_battle
import time

if TYPE_CHECKING:
    from global_data import GlobalData


def get_front_front_role_id(role):    # 获某号位站到前排的index
    assert role > 0 & role <= 8   # 最多有8号位
    return (role - 1) % 4


def get_front_role_order(role):  # 获得n号位的前排序号
    return get_front_front_role_id(role) + 1


@singleton
class Battle:
    def __init__(self, globData: GlobalData):
        self.finish_hook = None
        self.front = [1, 2, 3, 4]
        self.behind = [5, 6, 7, 8]
        self.enemy = None
        self.thread = None
        self.battle_end = False
        self.in_round_ctx = False
        self.round_number = 0
        self.round_records = []
        self.set_global_data(globData)

    def set_global_data(self, globData: GlobalData):
        self.globData = globData
        self.controller = globData.controller
        self.comparator = globData.comparator
        self.updateUI = globData.updateUI
        self.battle_dsl = BattleDSL(globData.updateUI)
        # 设置 Hook 函数，返回值为 bool 类型，表示是否继续执行
        battle_hook = self.battle_dsl.hook_manager
        battle_hook.set(
            'Finish', lambda: self.finish_hook and self.finish_hook())
        battle_hook.set('CmdStart', lambda: not self.globData.thread.stopped())
        battle_hook.set('BattleStart', lambda: (self._wait_round(True)))
        battle_hook.set('BattleEnd', lambda: self.hook_battle_end())
        battle_hook.set('Role', lambda role_id, skill_id, energy_level, x=None, y=None: self.cmd_role(
            int(role_id), int(skill_id), int(energy_level), x, y))
        battle_hook.set('XRole', lambda role_id, skill_id, energy_level, x=None, y=None: self.cmd_role(
            int(role_id) + 4, int(skill_id), int(energy_level), x, y))
        battle_hook.set('Attack', lambda: self.cmd_start_attack(
            lambda: self._wait_round()))
        battle_hook.set('SwitchAll', lambda: self.btn_switch_all())
        battle_hook.set('Boost', lambda: self.btn_all_boost())
        battle_hook.set('SP', lambda role_id: self.cmd_sp(int(role_id)))
        battle_hook.set('Wait', lambda time: self.cmd_wait(time))
        battle_hook.set('Skip', lambda time: self.cmd_skip(time))
        battle_hook.set('Click', lambda x, y: self.controller.press([int(x), int(y)]))

    def set_config(self):
        self.check_battle_ui_refs = cfg_battle.get("check.check_battle_ui_refs")   # 检测战斗图片
        self.check_round_ui_refs = cfg_battle.get("check.check_round_ui_refs")    # 检测回合结束图片
        self.check_skill_ui_refs = cfg_battle.get("check.check_skill_ui_refs")    # 检测技能界面图片

        self.role_coords_y = cfg_battle.get("coord.role_coords_y")     # 角色y坐标
        self.role_coord_x = cfg_battle.get("coord.role_coord_x")      # 角色x坐标
        self.skill_coords_y = cfg_battle.get("coord.skill_coords_y")    # 技能y坐标
        self.skill_coord_x = cfg_battle.get("coord.skill_coord_x")     # 技能x坐标
        self.boost_coords_x = cfg_battle.get("coord.boost_coords_x")    # boost终点x坐标
        self.confirm_coord = cfg_common.get("general.confirm_coord")     # 额外点击

        self.switch_refs = cfg_battle.get("button.switch_refs")       # 前后排切换按钮图片
        self.fallback_refs = cfg_battle.get("button.fallback_refs")     # 撤退按钮图片
        self.supports_refs = cfg_battle.get("button.supports_refs")     # 支援者按钮图片
        self.all_switch_refs = cfg_battle.get("button.all_switch_refs")   # 全员交替按钮图片
        self.all_boost_refs = cfg_battle.get("button.all_boost_refs")    # 全员加成按钮图片
        self.attack_refs = cfg_battle.get("button.attack_refs")       # “攻击”图片

        self.sp_coords = cfg_battle.get("coord.sp_coords")            # sp坐标
        self.sp_confirm_coords = cfg_battle.get("coord.sp_confirm_coords")  # sp确认坐标

    def run(self, path):
        self.thread = self.globData.thread
        self.reset()
        self.set_config()
        self.battle_dsl.load_instructions(path)
        self.battle_dsl.run_script()

    def reset(self):
        self.enemy = None
        self.battle_end = False
        self.in_round_ctx = False
        self.round_number = 0
        self.round_records = []

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

    def _select_enemy(self, x=None, y=None):
        if (not x or not y):
            return
        self.controller.press([int(x), int(y)])
        time.sleep(0.2)

    def _wait_round(self, resetRound=False, newRound=True):
        inRound = wait_until(self._in_round, [partial(
            self.controller.press, self.confirm_coord, press_duration=10, operate_latency=10)], thread=self.globData.thread)
        if inRound and newRound:
            if resetRound == True:
                self.round_number = 0
            self.round_number += 1
            self.in_round_ctx = True
            self._log_info(f"进入回合{self.round_number}")
        else:
            inBattle = self._in_battle()
            if not inBattle:
                self.cmd_skip(2000)
            else:
                if self.globData.thread.stopped():
                    return False
            return True

    def cmd_start_attack(self, cb=None):
        start_time = time.time()
        self._log_info("开始攻击!")
        self.btn_start_attack()
        wait_until_not(self._in_round, thread=self.globData.thread)
        end_condition = wait_either(
            self._in_round, self._not_in_battle, thread=self.globData.thread)
        if end_condition == 2:
            self.battle_end = True
        self.in_round_ctx = False
        if cb:
            cb()

    def cmd_role(self, role, skill, boost=0, x=None, y=None):
        assert self.in_round_ctx == True  # 必须在Round中执行
        assert role > 0 & role <= 8   # 最多有8号位
        assert skill >= 0 & skill <= 4  # 最多有4个技能(战斗为0)
        assert boost >= 0 & boost <= 3  # 最多boost三个豆

        self._log_info(f"执行{role}号位的{skill}技能, 加成{boost} ")

        front_role_id = get_front_front_role_id(role)
        select_role_coord = [self.role_coord_x,
                             self.role_coords_y[front_role_id]]
        self.controller.press(select_role_coord)
        self._select_enemy(x, y)
        role_in_behind = (role in self.behind)

        if role_in_behind:
            switch_coord = self.comparator.template_in_picture(
                self.switch_refs, return_center_coord=True)
            if switch_coord:
                self.controller.press(switch_coord)
                self.front[front_role_id], self.behind[front_role_id] = self.behind[front_role_id],  self.front[front_role_id]

        skill_start = [self.skill_coord_x, self.skill_coords_y[skill]]
        skill_end = [self.boost_coords_x[boost], self.skill_coords_y[skill]]
        wait_until(self._in_round, [partial(self.controller.light_swipe, skill_start, skill_end),
                                    partial(self.controller.light_press, self.confirm_coord)], thread=self.globData.thread)

    def cmd_sp(self, role):
        assert self.in_round_ctx == True  # 必须在Round中执行
        assert role > 0 & role <= 8   # 最多有8号位

        start_time = time.time()
        self._log_info(f"执行{role}号位的必杀技能!")

        front_role_id = get_front_front_role_id(role)
        select_role_coord = [self.role_coord_x,
                             self.role_coords_y[front_role_id]]
        self.controller.press(select_role_coord)
        self._log_info(f"进入选技能界面!")
        role_in_behind = (role in self.behind)
        if role_in_behind:
            self._log_info(f"切换人物!")
            switch_coord = self.comparator.template_in_picture(
                self.switch_refs, return_center_coord=True)
            if switch_coord:
                self.controller.press(switch_coord)
                self.front[front_role_id], self.behind[front_role_id] = self.behind[front_role_id],  self.front[front_role_id]

        self._log_info(f"正在选中必杀!")
        self.controller.press(self.sp_coords)
        time.sleep(0.4)
        self.controller.press(self.sp_confirm_coords)
        self._log_info(f"必杀技执行完毕，耗时：{time.time() - start_time:.2f} 秒")

    def cmd_wait(self, time_in_ms):
        time_in_seconds = int(time_in_ms) / 1000.0
        self._log_info(f"等待 {time_in_ms} 毫秒...")
        time.sleep(time_in_seconds)

    def cmd_skip(self, time_in_ms):
        self._log_info(f"跳过 {time_in_ms} 毫秒...")
        self.controller.press(self.confirm_coord, int(time_in_ms))

    def hook_battle_end(self):
        self._log_info(f"战斗结束...")

    def hook_finish(self, finish_hook):
        self.finish_hook = finish_hook

    def btn_start_attack(self):
        attack_coord = self.comparator.template_in_picture(
            self.attack_refs, return_center_coord=True)
        if attack_coord:
            self.controller.press(attack_coord)  # 开始战斗

    def btn_switch_all(self):
        start_time = time.time()
        self.front, self.behind = self.behind, self.front
        all_switch_coord = self.comparator.template_in_picture(
            self.all_switch_refs,  return_center_coord=True)
        if all_switch_coord:
            self.controller.press(all_switch_coord, T=0.5)
        self._log_info(f"前后排切换完成，耗时：{time.time() - start_time:.2f} 秒")

    def btn_all_boost(self):
        start_time = time.time()
        all_boost_coord = self.comparator.template_in_picture(
            self.all_boost_refs,  return_center_coord=True)
        if all_boost_coord:
            self.controller.press(all_boost_coord, T=0.5)
        self._log_info(f"全能量提升完成，耗时：{time.time() - start_time:.2f} 秒")

    def _log_info(self, message):
        loger.log_info(message)
        if self.updateUI:
            self.updateUI(message)
