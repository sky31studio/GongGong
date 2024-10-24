from datetime import timedelta

from xtu_ems.basic import BaseConfig


class TaskConf:
    def __init__(self, queue: str, interval_s: timedelta, key: str, retry_time: int = 2, failed_queue: str = "failed"):
        self.queue = queue
        """队列名称"""
        self.interval = interval_s
        """任务执行间隔"""
        self.retry = retry_time
        """任务最大重试次数"""
        self.key = key
        """任务键"""
        self.failed_queue = failed_queue
        """失败队列名称"""


class TaskTime(metaclass=BaseConfig):
    """任务间隔时间，可以通过环境变量覆盖"""

    EXAM_SCHEDULE: str = "10h"
    """考试安排查询时间间隔"""

    SCORE_SCHEDULE: str = "10h"
    """成绩查询时间间隔"""

    COURSE_SCHEDULE: str = "10h"
    """课程表查询时间间隔"""

    @staticmethod
    def parse_time(time_str: str) -> timedelta:
        """解析时间字符串"""
        time_str = time_str.strip()
        if time_str.endswith("s"):
            return timedelta(seconds=int(time_str[:-1]))
        elif time_str.endswith("m"):
            return timedelta(minutes=int(time_str[:-1]))
        elif time_str.endswith("h"):
            return timedelta(hours=int(time_str[:-1]))


class ActiveQueueConfig:
    """活动队列配置"""

    EXAM_SCHEDULE = TaskConf(
        queue="active.exam",
        key="exam",
        interval_s=TaskTime.parse_time(TaskTime.EXAM_SCHEDULE),
    )
    """考试安排查询"""

    SCORE_SCHEDULE = TaskConf(
        queue="active.score",
        key="score",
        interval_s=TaskTime.parse_time(TaskTime.SCORE_SCHEDULE),
    )
    """成绩查询"""

    COURSE_SCHEDULE = TaskConf(
        queue="active.course",
        key="course",
        interval_s=TaskTime.parse_time(TaskTime.COURSE_SCHEDULE),
    )
    """课程表查询"""
