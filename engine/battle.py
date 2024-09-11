from __future__ import annotations
from functools import partial
from typing import TYPE_CHECKING
from engine.battle_hook import BattleHook
from engine.engine import engine
from engine.comparator import comparator
from utils.singleton import singleton
import time

from utils.wait import wait_either, wait_until, wait_until_not

if TYPE_CHECKING:
    from app_data import AppData


@singleton
class Battle:
    def __init__(self):
        self.app_data = None
        self.debug = False
        self.hook_manager = BattleHook()

        self.instructions = []  # 用于存储预读取的指令列表
        self.front = [1, 2, 3, 4]
        self.behind = [5, 6, 7, 8]
        self.role_coords_y = [60, 162, 270, 378]    # 角色y坐标
        self.role_coord_x = 816    # 角色x坐标
        self.skill_coords_y = [151, 232, 313, 394, 475]    # 技能y坐标
        self.skill_coord_x = 580    # 技能x坐标
        self.boost_coords_x = [600, 787, 854, 921]   # boost终点x坐标
        self.confirm_coord = [702, 348]   # 额外点击
        self.sp_coords = [525, 68]      # sp坐标
        self.sp_confirm_coords = [702, 348]  # sp确认坐标
        self.finish_hook = None
        self.in_round_ctx = False
        self.round_number = 0
        self.cfg_attack = './assets/battle/attack.png'
        self.cfg_switch = './assets/battle/switch.png'
        self.cfg_round_ui = './assets/battle/round_ui.png'
        self.cfg_battle_ui = './assets/battle/battle_ui.png'
        self.cfg_skill_ui = './assets/battle/skill_ui.png'
        self.cfg_allswitch = './assets/battle/allswitch.png'
        self.cfg_allboost = './assets/battle/allboost.png'

    def set(self, app_data: AppData):
        self.app_data = app_data
        self.set_hook()

    def reset(self):
        self.in_round_ctx = False
        self.round_number = 0

    def set_hook(self):
        # 设置 Hook 函数，返回值为 bool 类型，表示是否继续执行
        battle_hook = self.hook_manager
        battle_hook.set(
            'Finish', lambda: self.finish_hook and self.finish_hook())
        battle_hook.set('CmdStart', lambda: not self.thread_stoped())
        battle_hook.set('BattleStart', lambda: (self._wait_round(True)))
        battle_hook.set('BattleEnd', lambda: self.hook_battle_end())
        battle_hook.set('Role', lambda role_id, skill_id, energy_level, x=None, y=None: self.cmd_role(
            int(role_id), int(skill_id), int(energy_level), x, y))
        battle_hook.set('XRole', lambda role_id, skill_id, energy_level, x=None, y=None: self.cmd_role(
            int(role_id) + 4, int(skill_id), int(energy_level), x, y))
        battle_hook.set('Attack', lambda: self.cmd_start_attack(
            lambda: self._wait_round()))
        battle_hook.set('SwitchAll', lambda: self.btn_all_switch())
        battle_hook.set('Boost', lambda: self.btn_all_bp())
        battle_hook.set('SP', lambda role_id: self.cmd_sp(int(role_id)))
        battle_hook.set('Wait', lambda time: self.cmd_wait(time))
        battle_hook.set('Skip', lambda time: self.cmd_skip(time))
        battle_hook.set('Click', lambda x, y: self.cmd_click(x, y))

    def thread_stoped(self) -> bool:
        return self.app_data and self.app_data.thread_stoped()

    def update_ui(self, msg: str, type='info'):
        self.app_data and self.app_data.update_ui(msg, type)

    def run(self, path):
        self._load_instructions(path)
        self._run_script()

    def btn_auto_battle(self):
        engine.device.click(368, 482)
        time.sleep(0.4)
        engine.device.click(825, 482)
        self.update_ui("自动战斗")

    def btn_quit_battle(self):
        engine.device.click(440, 482)
        self.update_ui("退出战斗")

    def btn_switch(self):
        self.front, self.behind = self.behind, self.front
        all_switch_coord = comparator.template_in_picture(
            self.cfg_allswitch,  return_center_coord=True)
        if all_switch_coord:
            engine.press(all_switch_coord, T=0.5)
        self.update_ui(f"前后排切换完成")

    def btn_all_switch(self):
        engine.device.click(577, 482)
        self.update_ui("全体切换")

    def btn_all_bp(self):
        all_boost_coord = comparator.template_in_picture(
            self.cfg_allboost,  return_center_coord=True)
        if all_boost_coord:
            engine.press(all_boost_coord, T=0.5)
        self.update_ui(f"全能量提升完成")

    def btn_attack(self):
        attack_coord = comparator.template_in_picture(
            self.cfg_attack, return_center_coord=True)
        if attack_coord:
            engine.press(attack_coord)
            self.update_ui("开始攻击")

    def cmd_click(self, x, y):
        engine.press([int(x), int(y)])
        self.update_ui(f"点击坐标{x}, {y}")

    def cmd_start_attack(self, cb=None):
        self.btn_attack()
        wait_until_not(self._in_round, thread=self.app_data.thread)
        end_condition = wait_either(
            self._in_round, self._not_in_battle, thread=self.app_data.thread)
        if end_condition == 2:
            self.battle_end = True
        self.in_round_ctx = False
        if cb:
            cb()

    def cmd_skip(self, duration=2):
        engine.device.long_click(480, 254, duration)
        self.update_ui(f"跳过 {duration} 秒")

    def cmd_role(self, role, skill, boost=0, x=None, y=None):
        assert self.in_round_ctx == True  # 必须在Round中执行
        assert role > 0 & role <= 8   # 最多有8号位
        assert skill >= 0 & skill <= 4  # 最多有4个技能(战斗为0)
        assert boost >= 0 & boost <= 3  # 最多boost三个豆

        self.update_ui(f"执行{role}号位的{skill}技能, 加成{boost} ")

        front_role_id = get_front_front_role_id(role)
        select_role_coord = [self.role_coord_x,
                             self.role_coords_y[front_role_id]]
        engine.press(select_role_coord)
        self._select_enemy(x, y)
        role_in_behind = (role in self.behind)

        if role_in_behind:
            switch_coord = comparator.template_in_picture(
                self.cfg_switch, return_center_coord=True)
            if switch_coord:
                engine.press(switch_coord)
                self.front[front_role_id], self.behind[front_role_id] = self.behind[front_role_id],  self.front[front_role_id]

        skill_start = [self.skill_coord_x, self.skill_coords_y[skill]]
        skill_end = [self.boost_coords_x[boost], self.skill_coords_y[skill]]
        wait_until(self._in_round, [partial(engine.light_swipe, skill_start, skill_end),
                                    partial(engine.light_press, self.confirm_coord)], thread=self.app_data.thread)

    def cmd_sp(self, role):
        assert self.in_round_ctx == True  # 必须在Round中执行
        assert role > 0 & role <= 8   # 最多有8号位

        start_time = time.time()
        self.update_ui(f"执行{role}号位的必杀技能!")

        front_role_id = get_front_front_role_id(role)
        select_role_coord = [self.role_coord_x,
                             self.role_coords_y[front_role_id]]
        engine.press(select_role_coord)
        self.update_ui(f"进入选技能界面!")
        role_in_behind = (role in self.behind)
        if role_in_behind:
            self.update_ui(f"切换人物!")
            switch_coord = comparator.template_in_picture(
                self.cfg_switch, return_center_coord=True)
            if switch_coord:
                engine.press(switch_coord)
                self.front[front_role_id], self.behind[front_role_id] = self.behind[front_role_id],  self.front[front_role_id]

        self.update_ui(f"正在选中必杀!")
        engine.press(self.sp_coords)
        time.sleep(0.4)
        engine.press(self.sp_confirm_coords)
        self.update_ui(f"必杀技执行完毕，耗时：{time.time() - start_time:.2f} 秒")

    def cmd_wait(self, time_in_ms):
        time_in_seconds = int(time_in_ms) / 1000.0
        self.update_ui(f"等待 {time_in_ms} 毫秒...")
        time.sleep(time_in_seconds)

    def cmd_skip(self, time_in_ms):
        self.update_ui(f"跳过 {time_in_ms} 毫秒...")
        engine.press(self.confirm_coord, int(time_in_ms))

    def hook_battle_end(self):
        self.update_ui(f"战斗结束...")

    def hook_finish(self, finish_hook):
        self.finish_hook = finish_hook

    def _in_round(self):
        in_round = self._in_battle() and comparator.template_in_picture(
            self.cfg_round_ui)
        return in_round

    def _in_battle(self):
        return comparator.template_in_picture(self.cfg_battle_ui)

    def _not_in_battle(self):
        return not self._in_battle()

    def _attack_end(self):
        attack_end = self._in_round() or (not self._in_battle())
        return attack_end

    def _in_select_skill(self):
        in_select_skill = self._in_battle() and comparator.template_in_picture(
            self.cfg_skill_ui)
        return in_select_skill

    def _select_enemy(self, x=None, y=None):
        if (not x or not y):
            return
        engine.press([int(x), int(y)])
        self.update_ui(f"选择敌人{x}, {y}")
        time.sleep(0.2)

    def _wait_round(self, resetRound=False, newRound=True):
        inRound = wait_until(self._in_round, [partial(
            engine.press, self.confirm_coord, press_duration=10, operate_latency=10)], thread=self.app_data.thread)
        if inRound and newRound:
            if resetRound == True:
                self.round_number = 0
            self.round_number += 1
            self.in_round_ctx = True
            self.update_ui(f"进入回合{self.round_number}")
        else:
            inBattle = self._in_battle()
            if not inBattle:
                self.cmd_skip(2000)
            else:
                if self.thread_stoped():
                    return False
            return True

    def _load_instructions(self, filename):
        """ 从文件中预读取指令并存储 """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.instructions = [line.strip() for line in file if line.strip() and not line.startswith('#')]
            if self.update_ui:
                self.update_ui("指令加载成功。")
        except Exception as e:
            if self.update_ui:
                self.update_ui(f"读取指令出错 {filename}. {e}")

    def _execute_instruction(self, instruction):
        hook_func_cmd_start = self.hook_manager.get('CmdStart')  # 获取对应指令的 hook 函数
        if hook_func_cmd_start is not None and not hook_func_cmd_start():
            return False

        """ 解析并执行指令 """
        parts = instruction.split(',')
        command = parts[0]  # 获取指令名称
        hook_func = self.hook_manager.get(command)

        if hook_func is not None:
            # 执行对应的 hook 函数，并传递参数
            hook_func(*parts[1:])
        else:
            # 更新 UI
            if self.update_ui:
                self.update_ui(f"找不到对应战斗指令 '{command}'.")
        return True

    def _run_script(self):
        """ 执行预加载的指令 """
        for instruction in self.instructions:
            is_continue = self._execute_instruction(instruction)
            if not is_continue:
                break
        # 文件读取完毕，执行 Finish Hook
        finish_hook = self.hook_manager.get('Finish')
        if finish_hook:
            finish_hook()


def get_front_front_role_id(role):    # 获某号位站到前排的index
    assert role > 0 & role <= 8   # 最多有8号位
    return (role - 1) % 4


def get_front_role_order(role):  # 获得n号位的前排序号
    return get_front_front_role_id(role) + 1


battle = Battle()
