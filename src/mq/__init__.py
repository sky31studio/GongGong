"""pika 监听装饰器"""

from pika.adapters.blocking_connection import BlockingConnection

from mq.consumer import MQConsumer, MQConsumerWrapper
from mq.publisher import MQPublisher, PublisherWrapper, MQPublisherWrapper


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
    def __init__(self, connection: BlockingConnection, prefetch_count=1, tracked=True, exchange='', logger=None):
        super().__init__(prefetch_count, tracked, exchange)
        self.connection = connection
        """MQ连接"""
        self.logger = logger
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

    def _get_consumer_channel(self, func):
        """获取消费者MQ连接"""
        return self._get_channel(self._get_consumer_channel)

    def _add_consumer(self, queue_name, func_wrapper):
        """添加监听函数，在初始化监听函数时调用"""
        if queue_name in self.consumers:
            self.consumers[queue_name].append(func_wrapper)
        func_wrapper = self._build_consumer_wrapper(func_wrapper.func, queue_name)
        super()._add_consumer(queue_name, func_wrapper)
        channel = self._get_consumer_channel(func_wrapper.func)
        channel.basic_consume(queue=queue_name,
                              on_message_callback=func_wrapper)

    def _run_listener(self, channel):
        """运行监听函数"""
        channel.start_consuming()

    def run(self):
        """运行MQ"""
        self._run_listener(self._get_consumer_channel(None))

    def _build_consumer_wrapper(self, func, queue_name, tracked=None):
        return MQConsumerWrapper(func, queue_name, self._get_consumer_channel(func), self.logger,
                                 tracked or self.tracked)

    def _build_publisher_wrapper(self, func, route_key, exchange):
        return MQPublisherWrapper(func, route_key, self._get_channel(func), self.logger, exchange)

    def mount_router(self, router: MQRouter):
        """
        挂载路由，会将路由中的所有消费者和发布者挂载到当前MQ中。
        生产者的发布动作会由当前MQ接管
        """

        for ex_route, funcs in router.publishers.items():
            for func in funcs:
                route_key = ex_route[1]
                exchange = ex_route[0] or router.exchange or self.exchange
                self._add_publisher(route_key, exchange=exchange, func_wrapper=func)
        for queue_name, funcs in router.consumers.items():
            for func in funcs:
                self._add_consumer(queue_name, func)
