
from app_data import app_data
from engine.u2_device import u2_device
from engine.comparator import comparator


def check_in_ads_modal(screenshot=None):
    """检查广告弹窗"""
    if (app_data.thread_stoped()):
        return False
    app_data.update_ui("check-广告弹窗", 'debug')
    if comparator.template_compare(f"assets/ads/ads_btn_watch_tag.png", screenshot=screenshot):
        app_data.update_ui("find-在广告弹窗", 'debug')
        return True
    else:
        return


def check_in_ads_watch(screenshot=None):
    """检查广告观看界面"""
    if (app_data.thread_stoped()):
        return False
    app_data.update_ui("check-广告观看界面", 'debug')
    if comparator.template_compare(f"assets/ads/ads_btn_watch_cancel.png", screenshot=screenshot):
        app_data.update_ui("find-在广告观看界面", 'debug')
        return True
    else:
        return False


def check_in_ads_playing(screenshot=None):
    """检查广告播放中"""
    if (app_data.thread_stoped()):
        return False
    app_data.update_ui("check-广告播放中", 'debug')
    if comparator.template_compare(f"assets/ads/ads_btn_playing.png", screenshot=screenshot):
        app_data.update_ui("find-在广告播放中", 'debug')
        return True
    else:
        return False


def check_in_ads_award_confirm(screenshot=None):
    """检查广告奖励确认"""
    if (app_data.thread_stoped()):
        return None
    app_data.update_ui("check-广告奖励确认", 'debug')
    crood = comparator.template_compare(f"assets/ads/ads_btn_award_confirm.png",
                                        return_center_coord=True, screenshot=screenshot)
    if crood is not None:
        app_data.update_ui("find-在广告奖励确认", 'debug')
        return crood
    else:
        return None


def check_in_ads_type_1(screenshot=None):
    """检查广告类型1"""
    if (app_data.thread_stoped()):
        return False
    app_data.update_ui("check-广告类型1", 'debug')
    crood = comparator.template_compare(f"assets/ads/type_1.png",
                                        return_center_coord=True, screenshot=screenshot)
    if crood is not None:
        app_data.update_ui("find-广告类型1", 'debug')
        return crood
    else:
        return None


def check_ads_finish(screenshot=None):
    """检查广告结束"""
    if (app_data.thread_stoped()):
        return False
    app_data.update_ui("check-广告结束", 'debug')
    if comparator.template_compare(f"assets/ads/finish.png", screenshot=screenshot):
        app_data.update_ui("find-广告结束", 'debug')
        return True
    if comparator.template_compare(f"assets/ads/finish_vip.png", screenshot=screenshot):
        app_data.update_ui("find-你是高贵的会员不需要看广告")
        return True
    else:
        return False


def btn_menu_ads_tag():
    u2_device.device.click(94, 395)


def btn_menu_ads_watch():
    u2_device.device.click(603, 481)


def btn_menu_ads_watch_cancel():
    u2_device.device.click(918, 42)


def btn_ads_award_confirm():
    u2_device.device.click(482, 325)
