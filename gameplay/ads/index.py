
from datetime import datetime
import gc
import os
import time

import cv2
from app_data import app_data
from engine.world import world
from engine.u2_device import u2_device
from gameplay.ads.check import check_ads_finish, check_catch_awards, check_finish_ads, check_in_ads_award_confirm, check_in_ads_modal, check_in_ads_playing, check_in_ads_type_1, check_in_ads_watch
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
        world.btn_trim_click()
        while not app_data.thread_stoped():
            if time.time() - statr_time > 180:
                app_data.update_ui("出现异常超时停止看广告")
                write_log(self.screenshot, 'image_ads_debug')
                pre_state = State.Unknow
                wait_time_count = 0
                break
            if state != State.Unknow and state is not None and state != pre_state:
                statr_time = time.time()
                app_data.update_ui(f"状态变化{state}", 'debug')
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
                    app_data.update_ui("当前在世界地图")
                    app_data.update_ui("点击菜单")
                    world.btn_menu_click()
                    state = State.World
                    time.sleep(2)
                    app_data.update_ui("点击成就按钮")
                    world.btn_menu_achievement_click()
                    state = State.AchievementMenu

                in_achievement_page = world.check_in_achievement_page(self.screenshot)
                if in_achievement_page:
                    app_data.update_ui("当前在广告界面")
                    state = State.AchievementPage
                    app_data.update_ui("点击增长见闻按钮")
                    u2_device.device.click(in_achievement_page[0], in_achievement_page[1])
                    time.sleep(wait_time)
                in_ads_modal = check_in_ads_modal(self.screenshot)
                if in_ads_modal is not None:
                    app_data.update_ui("当前在广告弹窗")
                    state = State.AdsModal
                    app_data.update_ui("点击观看开宝箱")
                    u2_device.device.click(in_ads_modal[0], in_ads_modal[1])
                    time.sleep(3)
                in_ads_watch = check_in_ads_watch(self.screenshot)
                if in_ads_watch is not None and pre_state != State.AdsWatchEnd:
                    app_data.update_ui("当前在广告播放页面")
                    i = 0
                    while check_in_ads_playing(self.screenshot):
                        self.shot()
                        i += 1
                        app_data.update_ui("广告播放中")
                        state = State.AdsPlaying
                        time.sleep(wait_time)
                    if i == 0:
                        for i in range(30):
                            self.shot()
                            if check_finish_ads(self.screenshot):
                                app_data.update_ui("广告播放结束")
                                break
                            if check_in_ads_modal(self.screenshot):
                                app_data.update_ui("没有成功播放广告")
                                break
                            if (app_data.thread_stoped()):
                                return False
                            state = State.AdsPlaying
                            app_data.update_ui(f"匹配不播放标识,等待{30 - i}秒")
                    else:
                        app_data.update_ui("广告播放结束")
                    time.sleep(2)
                    in_ads_watch = check_in_ads_watch(self.screenshot)
                    if in_ads_watch is not None:
                        app_data.update_ui(f"点击关闭广告0坐标{in_ads_watch}")
                        u2_device.device.click(in_ads_watch[0], in_ads_watch[1])
                    else:
                        app_data.update_ui("未找到关闭广告按钮")
                        default_crood = (918, 41)
                        app_data.update_ui("点击屏幕")
                        u2_device.device.click(default_crood[0], default_crood[1])
                    state = State.AdsWatchEnd
                    time.sleep(wait_time)
                self.shot()
                btn_award_crood = check_in_ads_award_confirm(self.screenshot)
                if btn_award_crood is not None:
                    app_data.update_ui("广告奖励确认")
                    state = State.AdsAwardConfirm
                    app_data.update_ui("奖励截图")
                    write_log(self.screenshot, 'image_ads_award')
                    app_data.update_ui("点击领取奖励")
                    u2_device.device.click(btn_award_crood[0], btn_award_crood[1])
                    time.sleep(wait_time)
                btn_type_1_crood = check_in_ads_type_1(self.screenshot)
                if btn_type_1_crood is not None:
                    app_data.update_ui("广告类型1")
                    state = State.AdsType1
                    app_data.update_ui(f"点击关闭广告类型1{btn_type_1_crood}")
                    u2_device.device.click(btn_type_1_crood[0], btn_type_1_crood[1])
                    time.sleep(wait_time)
                if catch_awards_crood := check_catch_awards(self.screenshot):
                    app_data.update_ui("抓住奖励机会")
                    state = State.CatchAwards
                    app_data.update_ui(f"点击抓住奖励机会{catch_awards_crood}")
                    u2_device.device.click(catch_awards_crood[0], catch_awards_crood[1])
                    time.sleep(wait_time)
                if check_ads_finish(self.screenshot):
                    app_data.update_ui("所有广告已完成")
                    state = State.AdsFinish
                    break
                app_data.update_ui(f"状态变化{state}")
                time.sleep(wait_time)
            except Exception as e:
                app_data.update_ui(f"广告异常{e}")


def write_log(current_image, debug_path='images_ads', type='ads'):
    if current_image is None or len(current_image) == 0:
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f'current_image_{timestamp}_{type}.png'
    os.makedirs(debug_path, exist_ok=True)  # 确保目录存在
    u2_device.cleanup_large_files(debug_path, 10)  # 清理大于 10 MB 的文件
    cv2.imwrite(os.path.join(debug_path, file_name), current_image)
    return file_name
