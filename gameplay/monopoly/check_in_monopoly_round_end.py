from __future__ import annotations
import time
from typing import TYPE_CHECKING

from gameplay.monopoly.config import config
from gameplay.monopoly.constants import State

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def check_in_monopoly_round_end(monopoly: Monopoly, round_state):
    if time.time() - monopoly.round_time_start > config.cfg_round_time:
        return True
    if round_state == State.Finised:
        return True
    return False
