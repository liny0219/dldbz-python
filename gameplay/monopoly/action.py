import time
from engine.u2_device import u2_device


def btn_center_confirm():
    u2_device.device.click(480, 254)


def btn_menu_monopoly():
    u2_device.device.click(356, 460)
    time.sleep(1)
    u2_device.device.click(196, 453)


def btn_setting_monopoly():
    u2_device.device.click(843, 448)


def btn_play_monopoly():
    u2_device.device.click(600, 430)
