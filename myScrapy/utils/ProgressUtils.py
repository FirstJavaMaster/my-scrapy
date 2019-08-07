from datetime import datetime, timedelta


class ProgressUtils:

    def __init__(self):
        self.number_total = 0
        self.number_complete = 0
        self.start_time = datetime.now()

    def add_task(self, number=1):
        self.number_total += number

    def task_complete(self, msg=''):
        self.number_complete += 1
        now = datetime.now()
        used_seconds = (now - self.start_time).total_seconds()
        total_seconds = used_seconds * self.number_total / self.number_complete
        left_seconds = total_seconds - used_seconds

        print_msg = '进度更新(%s/%s)-> 已用/剩余时间:[ %s / %s ] %s' % (self.number_complete, self.number_total,
                                                              ProgressUtils.seconds_to_humane(used_seconds),
                                                              ProgressUtils.seconds_to_humane(left_seconds), msg)
        print(print_msg)

    # 将秒数转化为可视化
    @staticmethod
    def seconds_to_humane(seconds):
        # 转换为整数,+1是为了防止0的出现,更美观
        seconds = int(seconds) + 1
        return str(timedelta(seconds=seconds))
