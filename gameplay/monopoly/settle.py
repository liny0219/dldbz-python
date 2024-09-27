from __future__ import annotations
import time
from app_data import app_data
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gameplay.monopoly.index import Monopoly


def report_end(monopoly: Monopoly):
    if not monopoly.reported_finish:
        monopoly.finished_count += 1
        monopoly.reported_finish = True
        app_data.update_ui(f"find-完成一局")


def report_finish(monopoly: Monopoly):
    if not monopoly.reported_end:
        now = time.time()
        turn_duration = (now - monopoly.begin_turn) / 60
        if monopoly.started_count == 0:
            monopoly.finished_count = 0
            turn_duration = 0

        failed_count = monopoly.started_count - monopoly.finished_count
        if failed_count > monopoly.pre_failed_count:
            monopoly.total_failed_time += turn_duration
        else:
            monopoly.total_finish_time += turn_duration

        monopoly.pre_failed_count = failed_count

        if failed_count < 0:
            failed_count = 0
            monopoly.total_failed_time = 0
            monopoly.total_finish_time = 0

        avg_finish_duration = monopoly.total_finish_time / monopoly.finished_count if monopoly.finished_count > 0 else 0
        avg_failed_duration = monopoly.total_failed_time / failed_count if failed_count > 0 else 0

        total_duration = (monopoly.total_finish_time + monopoly.total_failed_time)

        msg1 = f"成功{monopoly.finished_count}次, 翻车{failed_count}次, 重启{monopoly.restart}次"
        msg2 = f"本轮{turn_duration:.1f}分钟,成功平均{avg_finish_duration:.1f}分钟,翻车平均{avg_failed_duration:.1f}分钟"
        msg3 = f"扔骰子{monopoly.roll_time}次, 总耗时{total_duration:.1f}分钟"
        app_data.update_ui(f"{msg1},{msg2},{msg3}", 'stats')
        monopoly.reported_end = True
