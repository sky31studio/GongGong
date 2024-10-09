"""pika 监听装饰器"""
import logging
import threading

from pika.adapters.blocking_connection import BlockingConnection

from spider.mq.consumer import MQConsumer, MQConsumerWrapper
from spider.mq.publisher import MQPublisher, PublisherWrapper, MQPublisherWrapper


class MQRouter(MQConsumer, MQPublisher):
    def __init__(self, prefetch_count=1, tracked=True, exchange=''):
        super().__init__()
        super(MQConsumer, self).__init__()
        self.prefetch_count = prefetch_count
        """预获取消息数量"""
        self.tracked = tracked
        """是否需要跟踪执行时间"""
        self.exchange = exchange
        """交换机名称"""


class MQ(MQRouter):
    def __init__(self, connection: BlockingConnection, prefetch_count=1, tracked=True, exchange=''):
        super().__init__(prefetch_count, tracked, exchange)
        self.connection = connection
        """MQ连接"""
        self.logger = logging.getLogger('MQ')
        """日志器"""
        self.listener = {}
        """监听器，用于存储消费者函数和处理线程。二元组（函数，线程）"""
        self.channels = {}
        """通道，用于存储MQ连接"""

    def _get_channel(self, func):
        """获取MQ连接"""
        if func not in self.channels:
            self.channels[func] = self.connection.channel()
        channel = self.channels[func]
        channel.basic_qos(prefetch_count=self.prefetch_count)
        return channel

    def _add_consumer(self, queue_name, func_wrapper):
        """添加监听函数，在初始化监听函数时调用"""
        super()._add_consumer(queue_name, func_wrapper)
        channel = self._get_channel(func_wrapper.func)
        channel.queue_declare(queue=queue_name)
        channel.basic_consume(queue=queue_name,
                              on_message_callback=func_wrapper)
        self._run_listener(queue_name, func_wrapper, channel)

    def _run_listener(self, queue_name, func, channel):
        """运行监听函数"""
        thr = threading.Thread(target=lambda: channel.start_consuming())
        f_t = (func, thr)
        if queue_name not in self.listener:
            self.listener[queue_name] = [f_t]
        else:
            self.listener[queue_name].append(f_t)
        thr.start()

    def _build_consumer_wrapper(self, func, queue_name, exchange, tracked=None):
        return MQConsumerWrapper(func, queue_name, self._get_channel(func), self.logger, exchange or self.exchange,
                                 tracked or self.tracked)

    def _build_publisher_wrapper(self, func, queue_name, exchange):
        return MQPublisherWrapper(func, queue_name, self._get_channel(func), self.logger, exchange)

    def mount_router(self, router: MQRouter):
        """挂载路由"""
        for queue_name, funcs in router.consumers.items():
            for func in funcs:
                self._add_consumer(queue_name, func)

        for queue_name, funcs in router.publishers.items():
            for func in funcs:
                self._add_publisher(queue_name, exchange=router.exchange or self.exchange, func_wrapper=func)
