from __future__ import annotations
import time
from global_data import GlobalData
from utils.config_loader import cfg_recollection, cfg_common, cfg_battle
from utils.wait import wait_until


class Recollection:
    def __init__(self, global_data: GlobalData):
        self.set_config()
        self.loop = int(cfg_recollection.get("common.loop"))
        self.thread = global_data.thread
        self.controller = global_data.controller
        self.comparator = global_data.comparator
        self.battle = global_data.battle
        self.update_ui = global_data.update_ui
        self.Timestartup = time.time()  # 程序启动时间
        self.TimeroundStart = time.time()  # 每轮开始时间

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

    def log_time(self, start_time, action_description):
        elapsed_time = time.time() - start_time
        self.update_ui(f"{action_description} 完成，耗时：{elapsed_time:.2f} 秒")

    def on_read(self):
        ui_read = cfg_recollection.get("check.check_read_ui_refs")
        in_read = self.comparator.template_in_picture(
            ui_read, return_center_coord=True)
        if in_read:
            self.controller.press(in_read)
            return True

    def on_confirm_read(self):
        ui_confirm_read = cfg_recollection.get(
            "check.check_confirm_read_ui_refs")
        in_confirm_read = self.comparator.template_in_picture(
            ui_confirm_read, return_center_coord=True)
        if in_confirm_read:
            self.controller.press(in_confirm_read)
            return True

    def on_confirm_award(self):
        ui_confirm_award = cfg_recollection.get(
            "check.check_confirm_award_ui_refs")
        in_confirm_award = self.comparator.template_in_picture(
            ui_confirm_award, return_center_coord=True)
        if in_confirm_award:
            self.controller.press(in_confirm_award)
            print(f"on_confirm_award in_confirm_award True")
            return True
        print(f"on_confirm_award in_confirm_award False")
        return False

    def on_status_close(self):
        ui_status_close = cfg_recollection.get(
            "check.check_status_close_ui_refs")
        in_status_close = self.comparator.template_in_picture(
            ui_status_close, return_center_coord=True)
        if in_status_close:
            self.controller.press(in_status_close)
            print(f"on_status_close in_status_close True")
            return True
        print(f"on_status_close in_status_close True")
        return False

    def start(self):
        self.loopNum = 0
        self.run()

    def run(self):
        debug = False
        # debug = True
        try:
            if not debug:
                self.loop = int(cfg_recollection.get("common.loop"))

                self.update_ui("开始追忆之旅...")

                # 等待读取并确认读取
                self.update_ui(f"开始阅读")
                runState = wait_until(self.on_read,  operate_funcs=[self.on_read], thread=self.thread,
                                      timeout=10, check_interval=1)
                if self.thread.stopped():
                    self.update_ui(f"线程已停止")
                    return
                if not runState:
                    self.update_ui("开始阅读，中止", stats="中断，请重试。")
                    return

                self.update_ui(f"确认阅读内容")
                runState = wait_until(self.on_confirm_read, operate_funcs=[self.on_confirm_read],  thread=self.thread,
                                      timeout=10, check_interval=1)
                if self.thread.stopped():
                    self.update_ui(f"线程已停止")
                    return
                if not runState:
                    self.update_ui("确认失败，中止。", stats="确认失败，请检查。")
                    return

                self.update_ui("跳过开场动画")
                btnSkipTimeout = cfg_recollection.get("common.btn_skip_timeout")
                btnSkip = cfg_recollection.get("coord.btn_skip")
                self.controller.press(btnSkip, btnSkipTimeout)

                if not runState:
                    self.update_ui("跳过动画失败，中止。", stats="跳过动画失败，请重试。")
                    return

            self.update_ui("开始战斗")
            self.battle.run('./battle_script/recollection.txt')
            self.finish()
        except Exception as e:
            self.update_ui(f"发生错误：{e}", stats="发生错误，请检查。")

    def finish(self):
        self.loopNum += 1
        # 计算每轮时间
        current_time = time.time()
        round_time = current_time - self.TimeroundStart
        self.TimeroundStart = current_time  # 更新下一轮的开始时间

        # 计算总时间
        total_time = current_time - self.Timestartup

        # 更新 UI，时间格式为分钟
        self.update_ui(
            f"追忆之书完成次数：{self.loopNum}\n"
            f"本次时间：{round_time/60:.2f} 分钟\n"
            f"总运行时间：{total_time/60:.2f} 分钟",
            stats=f"追忆之书完成次数：{self.loopNum} 次 | 本次耗时：{round_time/60:.2f} 分钟 | 总耗时：{total_time/60:.2f} 分钟"
        )

        # 等待确认奖励
        runStateAward = wait_until(self.on_confirm_award, time_out_operate_funcs=[self.on_confirm_award], thread=self.thread,
                                   timeout=20)
        if self.thread.stopped():
            self.update_ui(f"线程已停止")
            return
        # 输出奖励确认结果
        if not runStateAward:
            self.update_ui(f"奖励确认失败")
            return
        runStateStatus = wait_until(self.on_status_close, time_out_operate_funcs=[self.on_status_close], thread=self.thread,
                                    timeout=20)
        # 输出状态关闭结果
        if not runStateStatus:
            self.update_ui(f"状态关闭失败：{self.loop}")
            return
        if self.loop != 0 and self.loopNum >= self.loop:
            self.update_ui(
                f"追忆之书已达到设定次数：{self.loop}\n"
                f"总运行时间：{total_time/60:.2f} 分钟",
                stats=f"已完成 {self.loopNum} 次 | 本次耗时：{round_time/60:.2f} 分钟 | 总耗时：{total_time/60:.2f} 分钟"
            )
            return
        self.run()
