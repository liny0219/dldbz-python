import time


def wait_until(condition_func, operate_funcs=None, timeout=10, check_interval=0.1, time_out_operate_funcs=None, thread=None):
    """
    等待直到条件函数返回 True 或超时。

    :param condition_func: 一个返回布尔值的函数，检查是否满足条件。
    :param operate_func: 如果存在该参数,则在等待过程中按照顺序执行
    :param timeout: 最大等待时间（秒）。
    :param check_interval: 每次检查条件之间的间隔时间（秒）。
    :return: 如果条件在超时时间内满足，返回 True；否则返回 False。
    """
    assert callable(condition_func), "wait_until传入的第一个参数必须是函数"
    start_time = time.time()
    time_elapsed = 0
    while True:
        if condition_func():
            return True
        if thread is not None and thread.stopped():
            print("Thread has ended.")
            return False
        if operate_funcs and type(operate_funcs) == list:
            try:
                for operate_func in operate_funcs:
                    operate_func()
            except Exception as e:
                print(f"operate_funcs error: {e}")
        if check_interval != 0:
            time.sleep(check_interval)
        time_elapsed = time.time() - start_time
        if time_elapsed >= timeout:
            if time_out_operate_funcs and type(time_out_operate_funcs) == list:
                try:
                    for time_out_operate_func in time_out_operate_funcs:
                        time_out_operate_func()
                except Exception as e:
                    print(f"time_out_operate_func error: {e}")
            break
    return False


def wait_until_list(condition_func, operate_funcs=None, timeout=10, check_interval=0.1, time_out_operate_funcs=None, thread=None):
    """
    等待直到条件函数返回 True 或超时。

    :param condition_func: 一个返回布尔值的函数，检查是否满足条件。
    :param operate_func: 如果存在该参数,则在等待过程中按照顺序执行
    :param timeout: 最大等待时间（秒）。
    :param check_interval: 每次检查条件之间的间隔时间（秒）。
    :return: 如果条件在超时时间内满足，返回 True；否则返回 False。
    """
    assert callable(condition_func), "wait_until传入的第一个参数必须是函数"
    start_time = time.time()
    time_elapsed = 0
    while True:
        for i in range(len(condition_func)):
            if condition_func[i]():
                return i
        if thread is not None and thread.stopped():
            print("Thread has ended.")
            return -1
        if operate_funcs and type(operate_funcs) == list:
            try:
                for operate_func in operate_funcs:
                    operate_func()
            except:
                pass
        time.sleep(check_interval)
        time_elapsed = time.time() - start_time
        if time_elapsed >= timeout:
            if time_out_operate_funcs and type(time_out_operate_funcs) == list:
                try:
                    for time_out_operate_func in time_out_operate_funcs:
                        time_out_operate_func()
                except:
                    pass
            break
    return -1


def wait_either(condition_func1, condition_func2,
                operate_funcs=None, timeout=10, check_interval=0.1, thread=None):
    start_time = time.time()
    while True:
        duration = time.time() - start_time
        if duration > timeout:
            return -10
        if thread is not None and thread.stopped():
            print("Thread has ended.")
            return -1
        if condition_func1():
            return 1
        if condition_func2():
            return 2
        if operate_funcs and type(operate_funcs) == list:
            try:
                for operate_func in operate_funcs:
                    operate_func()
            except:
                pass
        if check_interval != 0:
            time.sleep(check_interval)


def wait_until_not(condition_func, operate_funcs=None, timeout=10, check_interval=0.1, thread=None):
    """
    等待直到条件函数返回 False 或超时。

    :param condition_func: 一个返回布尔值的函数，检查是否满足条件。
    :param operate_funcs: 等待中途做的操作比如点击屏幕,点击撤退等。
    :param timeout: 最大等待时间（秒）。
    :param check_interval: 每次检查条件之间的间隔时间（秒）。
    :return: 如果条件在超时时间内满足，返回 True；否则返回 False。
    """
    assert callable(condition_func), "wait_until_not传入的第一个参数必须是函数"
    start_time = time.time()

    while time.time() - start_time < timeout:
        if thread is not None and thread.stopped():
            print("Thread has ended.")
            return False
        if not condition_func():
            return True
        if operate_funcs and type(operate_funcs) == list:
            try:
                for operate_func in operate_funcs:
                    operate_func()
            except:
                pass
        time.sleep(check_interval)

    return False
