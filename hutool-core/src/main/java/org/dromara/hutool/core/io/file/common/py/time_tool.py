import time

from datetime import datetime


class Timer:
    def __init__(self):
        self.__start_time = time.time()

    def count_time(self):
        return time.time() - self.__start_time


class time_util:
    @staticmethod
    def get_cur_time_str():
        now = datetime.now()
        return now.strftime("%Y%m%d_%H%M%S")
