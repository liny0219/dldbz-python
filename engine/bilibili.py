from __future__ import annotations
from typing import TYPE_CHECKING

from app_data import app_data
from engine.u2_device import u2_device
from engine.comparator import comparator


def check_in_bilibili_protocol_0(screenshot):
    if screenshot is None or len(screenshot) == 0:
        return False
    if (app_data.thread_stoped()):
        return False
    app_data.update_ui("check-bilibili_protocol_0", 'debug')
    crood = comparator.template_compare(f"./assets/bili/protocol_accept_0.png",
                                        return_center_coord=True, screenshot=screenshot, match_threshold=0.85)
    if crood is not None and len(crood) > 0:
        u2_device.device.click(crood[0], crood[1])
        app_data.update_ui("点击B服同意协议1")
        return True
    return False


def check_in_bilibili_protocol_1(screenshot):
    if screenshot is None or len(screenshot) == 0:
        return False
    if (app_data.thread_stoped()):
        return False
    app_data.update_ui("check-bilibili_protocol_1", 'debug')
    crood = comparator.template_compare(f"./assets/bili/protocol_accept_1.png",
                                        return_center_coord=True, screenshot=screenshot, match_threshold=0.85)
    if crood is not None and len(crood) > 0:
        u2_device.device.click(crood[0], crood[1])
        app_data.update_ui("点击B服同意协议2")
        return True
    return False
