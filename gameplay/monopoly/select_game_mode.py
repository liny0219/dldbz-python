from app_data import app_data
from engine.u2_device import u2_device
from gameplay.monopoly.config import config, set_config


def select_game_mode():
    set_config()
    init_ticket = 1
    init_lv = 0
    while config.cfg_ticket < init_ticket and not app_data.thread_stoped():
        reduce_ticket()
        init_ticket -= 1
    while config.cfg_ticket > init_ticket and not app_data.thread_stoped():
        add_ticket()
        init_ticket += 1
    while config.cfg_lv > init_lv and not app_data.thread_stoped():
        add_lv()
        init_lv += 1
    while config.cfg_lv < init_lv and not app_data.thread_stoped():
        reduce_lv()
        init_lv -= 1


def add_ticket():
    u2_device.device.click(373, 220)


def reduce_ticket():
    u2_device.device.click(243, 220)


def add_lv():
    u2_device.device.click(715, 220)


def reduce_lv():
    u2_device.device.click(588, 220)
