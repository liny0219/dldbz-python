from app_data import app_data
from engine.engine import engine
from gameplay.monopoly.config import config


def select_game_mode():
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
    engine.device.click(373, 220)


def reduce_ticket():
    engine.device.click(243, 220)


def add_lv():
    engine.device.click(715, 220)


def reduce_lv():
    engine.device.click(588, 220)
