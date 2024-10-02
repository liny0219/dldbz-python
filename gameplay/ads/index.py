
from datetime import datetime
import gc
import os
import time

import cv2
from app_data import app_data
from engine.world import world
from engine.u2_device import u2_device
from gameplay.ads.check import check_ads_finish, check_in_ads_award_confirm, check_in_ads_modal, check_in_ads_playing, check_in_ads_type_1, check_in_ads_watch
from gameplay.ads.constants import State


class Ads():
    def __init__(self):
        self.debug = True
        self.screenshot = None

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

    def start(self):
        pre_state = State.Unknow
        state = State.Unknow
        statr_time = time.time()
        wait_time = 0.2
        wait_time_count = 0
        while not app_data.thread_stoped():
            if wait_time_count > 5:
                write_log(self.screenshot, 'ads')
                wait_time_count = 0
            if time.time() - statr_time > 180:
                app_data.update_ui("出现异常超时停止看广告")
                pre_state = State.Unknow
                wait_time_count = 0
                break
            if state != State.Unknow and state is not None and state != pre_state:
                statr_time = time.time()
                app_data.update_ui(f"状态变化{state}")
                pre_state = state
                wait_time_count = 0
            else:
                wait_time_count += 1
            state = State.Unknow

            try:
                self.shot()
                if not u2_device.check_in_app():
                    app_data.update_ui("当前不在应用内", 'debug')
                    time.sleep(3)
                    continue
                in_world = world.check_in_world(self.screenshot)
                if in_world:
                    app_data.update_ui("当前在世界地图", 'debug')
                    world.btn_menu_click()
                    state = State.World
                    time.sleep(wait_time)

                in_achievement_menu = world.check_in_achievement_menu(self.screenshot)
                if in_achievement_menu:
                    app_data.update_ui("当前在成就界面", 'debug')
                    world.btn_menu_achievement_click()
                    state = State.AchievementMenu
                    time.sleep(wait_time)

                in_achievement_page = world.check_in_achievement_page(self.screenshot)
                if in_achievement_page:
                    app_data.update_ui("当前在广告界面", 'debug')
                    state = State.AchievementPage
                    u2_device.device.click(in_achievement_page[0], in_achievement_page[1])
                    time.sleep(wait_time)
                in_ads_modal = check_in_ads_modal(self.screenshot)
                if in_ads_modal is not None:
                    app_data.update_ui("当前在广告弹窗", 'debug')
                    state = State.AdsModal
                    u2_device.device.click(in_ads_modal[0], in_ads_modal[1])
                    time.sleep(wait_time)
                in_ads_watch = check_in_ads_watch(self.screenshot)
                if in_ads_watch is not None:
                    app_data.update_ui("当前在广告播放页面", 'debug')
                    while check_in_ads_playing(self.screenshot):
                        self.shot()
                        app_data.update_ui("广告播放中", 'debug')
                        state = State.AdsPlaying
                        time.sleep(wait_time)
                    app_data.update_ui("广告播放结束", 'debug')
                    in_ads_watch = check_in_ads_watch(self.screenshot)
                    u2_device.device.click(in_ads_watch[0], in_ads_watch[1])
                    state = State.AdsWatchEnd
                    time.sleep(wait_time)
                btn_award_crood = check_in_ads_award_confirm(self.screenshot)
                if btn_award_crood is not None:
                    app_data.update_ui("广告奖励确认", 'debug')
                    state = State.AdsAwardConfirm
                    u2_device.device.click(btn_award_crood[0], btn_award_crood[1])
                    time.sleep(wait_time)
                btn_type_1_crood = check_in_ads_type_1(self.screenshot)
                if btn_type_1_crood is not None:
                    app_data.update_ui("广告类型1", 'debug')
                    state = State.AdsType1
                    u2_device.device.click(btn_type_1_crood[0], btn_type_1_crood[1])
                    time.sleep(wait_time)
                if check_ads_finish(self.screenshot):
                    app_data.update_ui("所有广告已完成", 'debug')
                    state = State.AdsFinish
                    break
                app_data.update_ui(f"状态变化{state}", 'debug')
                time.sleep(wait_time)
            except Exception as e:
                app_data.update_ui(f"广告异常{e}")


def write_log(current_image, type):
    if current_image is None or len(current_image) == 0:
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_path = 'debug_images_ads'
    file_name = f'current_image_{timestamp}_{type}.png'
    os.makedirs(debug_path, exist_ok=True)  # 确保目录存在
    u2_device.cleanup_large_files(debug_path, 10)  # 清理大于 10 MB 的文件
    cv2.imwrite(os.path.join(debug_path, file_name), current_image)
    return file_name
