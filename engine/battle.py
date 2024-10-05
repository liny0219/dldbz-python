from functools import partial
import gc
from engine.world import world
from engine.battle_hook import BattleHook
from engine.u2_device import u2_device
from engine.comparator import comparator
from utils.singleton import singleton
from utils.config_loader import cfg_engine
import time

from utils.wait import wait_either, wait_until
from app_data import app_data


@singleton
class Battle:
    def __init__(self):
        self.debug = False
        self.hook_manager = BattleHook()
        self.wait_interval = 0.2
        self.wait_interval = 0.5
        self.instructions = []  # 用于存储预读取的指令列表
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
        self.screenshot = None
        self.round_number = 0
        self.cfg_attack = './assets/battle/attack.png'
        self.cfg_switch = './assets/battle/switch.png'
        self.cfg_round_ui = './assets/battle/round_ui.png'
        self.cfg_battle_ui = './assets/battle/battle_ui.png'
        self.cfg_skill_ui = './assets/battle/skill_ui.png'
        self.cfg_allswitch = './assets/battle/allswitch.png'
        self.cfg_allboost = './assets/battle/allboost.png'

    def set(self):
        self.set_hook()

    def reset(self):
        self.in_round_ctx = False
        self.round_number = 0
        cfg_engine.reload()
        self.wait_interval = float(cfg_engine.get('common.wait_interval'))
        self.cmd_interval = float(cfg_engine.get('common.cmd_interval'))

    def set_hook(self):
        # 设置 Hook 函数，返回值为 bool 类型，表示是否继续执行
        battle_hook = self.hook_manager
        battle_hook.set(
            'Finish', lambda: self.finish_hook and self.finish_hook())
        battle_hook.set('CmdStart', lambda: not app_data.thread_stoped())
        battle_hook.set('BattleStart', lambda: (self._wait_round(resetRound=True, return_end=False)))
        battle_hook.set('BattleEnd', lambda: self.hook_battle_end())
        battle_hook.set('Role', lambda role_id, skill_id, energy_level, x=None, y=None: self.cmd_role(
            int(role_id), int(skill_id), int(energy_level), x, y))
        battle_hook.set('XRole', lambda role_id, skill_id, energy_level, x=None, y=None: self.cmd_role(
            int(role_id) + 4, int(skill_id), int(energy_level), x, y))
        battle_hook.set('Attack', lambda: self.cmd_start_attack())
        battle_hook.set('SwitchAll', lambda: self.btn_all_switch())
        battle_hook.set('Boost', lambda: self.btn_all_bp())
        battle_hook.set('SP', lambda role_id: self.cmd_sp(int(role_id)))
        battle_hook.set('XSP', lambda role_id: self.cmd_sp(int(role_id) + 4))
        battle_hook.set('Wait', lambda time: self.cmd_wait(time))
        battle_hook.set('Skip', lambda time: self.cmd_skip(time))
        battle_hook.set('Click', lambda x, y: self.cmd_click(x, y))
        battle_hook.set('Auto', lambda: self.btn_auto_battle())

    def run(self, path):
        self._load_instructions(path)
        self._run_script()

    def btn_auto_battle(self):
        wait_until(self._in_round, thread=app_data.thread,
                   time_out_operate_funcs=lambda: app_data.update_ui(f"Auto指令等待回合超时"))
        u2_device.device.click(368, 482)
        time.sleep(self.wait_interval)
        u2_device.device.click(825, 482)
        app_data.update_ui("自动战斗")

    def btn_quit_battle(self):
        wait_until(self._in_round, thread=app_data.thread,
                   time_out_operate_funcs=lambda: app_data.update_ui(f"退出指令等待回合超时"))
        u2_device.device.click(440, 482)
        app_data.update_ui("退出战斗")

    def btn_all_switch(self):
        wait_until(self._in_round, thread=app_data.thread,
                   time_out_operate_funcs=lambda: app_data.update_ui(f"Switch指令等待回合超时"))
        u2_device.device.click(577, 482)
        app_data.update_ui("全体切换")

    def btn_all_bp(self):
        wait_until(self._in_round, thread=app_data.thread,
                   time_out_operate_funcs=lambda: app_data.update_ui(f"Boost指令等待回合超时"))
        all_boost_coord = comparator.template_in_picture(
            self.cfg_allboost,  return_center_coord=True)
        if all_boost_coord:
            u2_device.device.click(all_boost_coord[0], all_boost_coord[1])
        app_data.update_ui(f"全能量提升完成")

    def btn_attack(self):
        attack_coord = comparator.template_in_picture(
            self.cfg_attack, return_center_coord=True)
        if attack_coord:
            u2_device.device.click(attack_coord[0], attack_coord[1])
            app_data.update_ui("开始攻击")

    def cmd_click(self, x, y):
        u2_device.device.click(int(x), int(y))
        app_data.update_ui(f"点击坐标{x}, {y}")

    def cmd_start_attack(self):
        try:
            wait_until(self._in_round, thread=app_data.thread,
                       time_out_operate_funcs=lambda: app_data.update_ui(f"Attack指令等待回合超时"))
            self.btn_attack()
            time.sleep(self.wait_interval)
            self._wait_round()
        except Exception as e:
            app_data.update_ui(f"攻击异常{e}")

    def _wait_round(self, resetRound=False, return_end=True, timeout=180):
        try:
            while not app_data.thread_stoped():  # 使用循环代替递归
                wait_result = wait_either(
                    self._in_round, self._not_in_battle, timeout=timeout, thread=app_data.thread)

                if wait_result == 2:  # 检查是否是战斗结束
                    self.battle_end = True
                    if return_end:
                        return

                if wait_result == 1:  # 进入回合
                    self.in_round_ctx = True
                    if resetRound:
                        self.round_number = 0  # 重置回合计数
                    self.round_number += 1  # 进入下一回合
                    app_data.update_ui(f"进入回合{self.round_number}")
                    break  # 跳出循环

                else:  # 如果没有进入回合，等待继续
                    self.in_round_ctx = False
                    if resetRound:
                        self.cmd_skip(2000)  # 跳过一定时间后继续等待

            # 循环结束后，回合处理结束，退出函数

        except Exception as e:
            app_data.update_ui(f"攻击异常: {e}")

    def cmd_role(self, role, skill, boost=0, x=None, y=None):
        try:
            wait_until(self._in_round, thread=app_data.thread,
                       time_out_operate_funcs=lambda: app_data.update_ui(f"Role指令等待回合超时"))
            if self.in_round_ctx != True:
                raise Exception(f"执行Role指令{role},{skill},{boost}不在回合中")
            if role < 1 or role > 8:
                raise Exception(f"执行Role指令{role},{skill},{boost}角色号错误")
            if skill < 0 or skill > 4:
                raise Exception(f"执行Role指令{role},{skill},{boost}技能号错误")
            if boost < 0 or boost > 3:
                raise Exception(f"执行Role指令{role},{skill},{boost}boost号错误")
            role_in_behind = role > 4
            behide = '前排'
            role_number = role
            if role_in_behind:
                behide = '后排'
                role_number = role - 4
            app_data.update_ui(f"执行{behide}{role_number}号位的{skill}技能, 加成{boost} ")

            front_role_id = get_front_front_role_id(role)
            u2_device.device.click(self.role_coord_x, self.role_coords_y[front_role_id])
            wait_until(self._in_select_skill, thread=app_data.thread,
                       time_out_operate_funcs=lambda: app_data.update_ui(f"Role指令等待选技能超时"))
            app_data.update_ui(f"进入选技能界面!")
            if role_in_behind:
                app_data.update_ui(f"开始切换人物!")
                wait_until(self._in_select_switch, thread=app_data.thread,
                           time_out_operate_funcs=lambda: app_data.update_ui(f"Role指令等待切换后排超时"))
                switch_coord = comparator.template_in_picture(
                    self.cfg_switch, return_center_coord=True)
                if switch_coord:
                    u2_device.device.click(switch_coord[0], switch_coord[1])
                    wait_until(self._in_select_skill, thread=app_data.thread,
                               time_out_operate_funcs=lambda: app_data.update_ui(f"Role指令等待切换后排选中技能超时"))
                else:
                    app_data.update_ui(f"未找到切换按钮")
            if boost > 0:
                skill_start = [self.skill_coord_x, self.skill_coords_y[skill]]
                skill_end = [self.boost_coords_x[boost], self.skill_coords_y[skill]]
                wait_until(self._in_round, [partial(u2_device.light_swipe, skill_start, skill_end),
                                            partial(u2_device.light_press, self.confirm_coord)], thread=app_data.thread)
            else:
                u2_device.device.click(self.skill_coord_x, self.skill_coords_y[skill])
            app_data.update_ui(f"选中技能{skill}")
        except Exception as e:
            app_data.update_ui(f"执行技能异常{e}")

    def cmd_sp(self, role):
        try:
            wait_until(self._in_round, thread=app_data.thread,
                       time_out_operate_funcs=lambda: app_data.update_ui(f"SP指令等待回合超时"))
            if self.in_round_ctx != True:
                raise Exception(f"执行SP指令{role},不在回合中")
            if role < 1 or role > 8:
                raise Exception(f"执行SP指令{role},角色号错误")

            role_in_behind = role > 4
            behide = '前排'
            role_number = role
            if role_in_behind:
                behide = '后排'
                role_number = role - 4
            app_data.update_ui(f"执行{behide}{role_number}号位的必杀技能!")

            front_role_id = get_front_front_role_id(role)
            u2_device.device.click(self.role_coord_x, self.role_coords_y[front_role_id])
            app_data.update_ui(f"进入选技能界面!")
            wait_until(self._in_select_skill, thread=app_data.thread,
                       time_out_operate_funcs=lambda: app_data.update_ui(f"SP指令等待选技能超时"))
            role_in_behind = role > 4
            if role_in_behind:
                app_data.update_ui(f"切换人物!")
                wait_until(self._in_select_switch, thread=app_data.thread,
                           time_out_operate_funcs=lambda: app_data.update_ui(f"SP指令等待切换后排超时"))
                switch_coord = comparator.template_in_picture(
                    self.cfg_switch, return_center_coord=True)
                if switch_coord:
                    u2_device.device.click(switch_coord[0], switch_coord[1])
                    wait_until(self._in_select_skill, thread=app_data.thread,
                               time_out_operate_funcs=lambda: app_data.update_ui(f"SP指令等待切换后排选中技能超时"))
                else:
                    app_data.update_ui(f"未找到切换按钮")
            app_data.update_ui(f"正在选中必杀!")
            u2_device.device.click(self.sp_coords[0], self.sp_coords[1])
            time.sleep(self.wait_interval)
            u2_device.device.click(self.sp_confirm_coords[0], self.sp_confirm_coords[1])
            app_data.update_ui(f"选中必杀技")
            time.sleep(self.wait_interval)
        except Exception as e:
            app_data.update_ui(f"执行必杀技能异常{e}")

    def cmd_wait(self, time_in_ms):
        time_in_seconds = int(time_in_ms) / 1000.0
        app_data.update_ui(f"等待 {time_in_ms} 毫秒...")
        time.sleep(time_in_seconds)

    def cmd_skip(self, time_in_ms):
        app_data.update_ui(f"跳过 {time_in_ms} 毫秒...")
        u2_device.device.long_click(self.confirm_coord[0], self.confirm_coord[1], int(time_in_ms)/1000)

    def hook_battle_end(self):
        app_data.update_ui(f"战斗结束...")

    def hook_finish(self, finish_hook):
        self.finish_hook = finish_hook

    def _in_round(self):
        in_round = self._in_battle() and comparator.template_in_picture(
            self.cfg_round_ui)
        return in_round

    def _in_battle(self):
        return comparator.template_in_picture(self.cfg_battle_ui)

    def _not_in_battle(self):
        return not self._in_battle() and not self._in_round()

    def _attack_end(self):
        attack_end = self._in_round() or (not self._in_battle())
        return attack_end

    def _in_select_skill(self):
        in_select_skill = self._in_battle() and comparator.template_in_picture(
            self.cfg_skill_ui)
        return in_select_skill

    def _in_select_switch(self):
        in_select_switch = self._in_battle() and comparator.template_in_picture(
            self.cfg_switch)
        return in_select_switch

    def _select_enemy(self, x=None, y=None):
        try:
            if (not x or not y):
                return
            u2_device.device.click(int(x), int(y))
            app_data.update_ui(f"选择敌人{x}, {y}")
            time.sleep(self.wait_interval)
        except Exception as e:
            app_data.update_ui(f"选择敌人异常{e}")

    def _load_instructions(self, filename):
        """ 从文件中预读取指令并存储 """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.instructions = [line.strip() for line in file if line.strip() and not line.startswith('#')]
            if app_data.update_ui:
                app_data.update_ui("指令加载成功。")
        except Exception as e:
            if app_data.update_ui:
                app_data.update_ui(f"读取指令出错 {filename}. {e}")

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
            if app_data.update_ui:
                app_data.update_ui(f"找不到对应战斗指令 '{command}'.")
        return True

    def _run_script(self):
        """ 执行预加载的指令 """
        for instruction in self.instructions:
            if self.is_dead():
                raise Exception("有人阵亡，中止")
            is_continue = self._execute_instruction(instruction)
            if app_data.thread_stoped():
                break
            if not is_continue:
                break
        # 文件读取完毕，执行 Finish Hook
        finish_hook = self.hook_manager.get('Finish')
        if finish_hook:
            finish_hook()

    def shot(self):
        try:
            app_data.update_ui("-----------开始截图", 'debug')
            if self.screenshot is not None:
                del self.screenshot
                self.screenshot = None
                gc.collect()
            self.screenshot = u2_device.device.screenshot(format='opencv')
            app_data.update_ui("-----------截图完成", 'debug')
            return self.screenshot
        except Exception as e:
            app_data.update_ui(f"截图异常{e}")
            return None

    def check_quit_battle(self, screenshot=None):
        app_data.update_ui("check-是否退出战斗", 'debug')
        result = comparator.template_compare('./assets/battle/quit_0.png', [(
            177, 462), (676, 509)], screenshot=screenshot, return_center_coord=True)
        if result:
            app_data.update_ui("find-退出战斗", 'debug')
        return result

    def check_finish(self):
        try:
            world.btn_trim_click()
            time.sleep(1)
            screenshot = self.shot()
            if self._in_battle():
                croods = self.check_quit_battle(screenshot=screenshot)
                if croods:
                    u2_device.device.click(croods[0], croods[1])
                    app_data.update_ui("点击退出战斗")
                    time.sleep(1)
                    screenshot = self.shot()
                    croods = self.check_confirm_quit_battle(screenshot=screenshot)
                    if croods:
                        u2_device.device.click(croods[0], croods[1])
                        app_data.update_ui("点击确认退出战斗")
                else:
                    app_data.update_ui("未找到退出战斗按钮")
                return False
            return True
        except Exception as e:
            app_data.update_ui(f"检查战斗结束异常{e}")
            return False
        finally:
            del screenshot
            gc.collect()

    def check_confirm_quit_battle(self, screenshot=None):
        app_data.update_ui("check-是否确认退出战斗", 'debug')
        result = comparator.template_compare('./assets/battle/quit_confirm.png', [(
            510, 329), (692, 395)], screenshot=screenshot, return_center_coord=True)
        if result:
            app_data.update_ui("find-确认退出战斗", 'debug')
        return result

    def is_dead(self):
        screenshot = self.shot()
        try:
            app_data.update_ui("check-是否有人阵亡", 'debug')
            result = comparator.template_compare('./assets/battle/dead_tag.png', [(
                759, 5), (951, 440)], screenshot=screenshot, gray=False)
            if result:
                app_data.update_ui("find-有人阵亡", 'debug')
            return result
        except Exception as e:
            app_data.update_ui(f"检查是否有人阵亡异常{e}")
            return False
        finally:
            del screenshot
            gc.collect()


def get_front_front_role_id(role):    # 获某号位站到前排的index
    assert role > 0 & role <= 8   # 最多有8号位
    return (role - 1) % 4


def get_front_role_order(role):  # 获得n号位的前排序号
    return get_front_front_role_id(role) + 1


battle = Battle()
