import logging
from datetime import datetime

from pydantic import BaseModel

from spider.config.app_config import TaskConf
from xtu_ems.ems.handler import Handler
from xtu_ems.ems.model import InformationPackage
from xtu_ems.ems.session import Session


class FailedInfo(BaseModel):
    """失败信息"""
    student_id: str
    """学号"""
    queue_name: str
    """队列名称"""
    session_id: str
    """数据"""
    error: str
    """错误信息"""


class StudentConsumer:

    def __init__(self, config: TaskConf, handler: Handler, kv_db: dict[str, str], publish_channel):
        """
        学生消费者
        Args:
            config: 消费者配置，包括队列名称、任务执行间隔、任务最大重试次数
            handler: 处理函数
            kv_db: 处理结果的存储
        """
        self.config = config
        self.handler = handler
        self.kv_db = kv_db
        self.publish_channel = publish_channel
        self.__name__ = config.queue

    def __call__(self, channel, method, properties, body):
        info_package = InformationPackage[Session].model_validate_json(body)
        time = info_package.update_time + self.config.interval
        if datetime.now() < time:
            # 通过抛出异常来回退（nack）消息，避免阻塞
            raise Exception('session is not expired')
        try:
            result = self.exec_handler(info=info_package)
            self.save(info_package=info_package, result=result)
            self.recycle(info=info_package)
        except Exception as e:
            self.failed(info=info_package, e=e)

    def recycle(self, info: InformationPackage[Session]):
        """循环队列，将消息重新放入队列"""
        info.update_time = datetime.now()
        self.publish_channel.basic_publish(exchange='', routing_key=self.config.queue,
                                           body=info.model_dump_json())

    def save(self, info_package: InformationPackage[Session], result):
        """数据保存"""
        key = f"{self.config.key}.{info_package.student_id}"
        logging.getLogger(self.config.queue).info(f'{info_package.student_id} saved to db: {result}')
        if isinstance(result, BaseModel):
            self.kv_db[key] = result.model_dump_json()
        else:
            self.kv_db[key] = result.__str__()

    def failed(self, info: InformationPackage[Session], e: Exception):
        """执行失败的处理"""
        logging.getLogger(self.config.queue).error(f'{info.student_id} failed', exc_info=e)
        failed = FailedInfo(student_id=info.student_id, queue_name=self.config.queue, session_id=info.data.session_id,
                            error=str(e))
        failed_info = InformationPackage[FailedInfo](student_id=info.student_id, data=failed,
                                                     update_time=datetime.now())
        self.publish_channel.basic_publish(exchange='', routing_key=self.config.failed_queue,
                                           body=failed_info.model_dump_json())

    def exec_handler(self, info: InformationPackage[Session]):
        """执行处理"""
        retry = self.config.retry
        exc = None
        session = info.data
        for i in range(retry):
            try:
                return self.handler.handler(session=session)
            except Exception as e:
                exc = e
                logging.getLogger(self.config.queue).debug(f'{info.student_id} failed，retry {i + 1} times')
        raise exc
