def conn_try_again(function, wait_time=3):
    """
    重连：用作装饰器
    """
    __retries = 3
    def wrapped(*args, **kwargs):
        nonlocal __retries
        try:
            return function(*args, **kwargs)
        except:
            if __retries > 0:
                __retries -= 1
                time.sleep(wait_time)
                print("程序将在%s秒后重新运行" %(wait_time))
                return wrapped(*args, **kwargs)
            else:
                print("网络状况可能不佳")
                raise Exception
    return wrapped
