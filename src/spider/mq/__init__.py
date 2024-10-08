"""pika 监听装饰器"""
import logging
import threading
import time

from pika.adapters.blocking_connection import BlockingConnection

from spider.mq.consumer import MQConsumer
from spider.mq.publisher import MQPublisher, PublisherWrapper, MQPublisherWrapper


class MQRouter(MQConsumer, MQPublisher):
    def __init__(self, prefetch_count=1, tracked=True):
        super().__init__()
        super(MQConsumer, self).__init__()
        self.prefetch_count = prefetch_count
        """预获取消息数量"""
        self.tracked = tracked
        """是否需要跟踪执行时间"""
        self.channels = {}
        """通道，用于存储MQ连接"""


class MQ(MQRouter):
    def __init__(self, connection: BlockingConnection, prefetch_count=1, tracked=True, exchange=''):
        super().__init__(prefetch_count, tracked)
        self.connection = connection
        """MQ连接"""
        self.logger = logging.getLogger('MQ')
        """日志器"""
        self.listener = {}
        """监听器，用于存储消费者函数和处理线程。二元组（函数，线程）"""
        self.exchange = exchange

    def _get_channel(self, func):
        """获取MQ连接"""
        if func not in self.channels:
            self.channels[func] = self.connection.channel()
        channel = self.channels[func]
        channel.basic_qos(prefetch_count=self.prefetch_count)
        return channel

    def _add_consumer(self, queue_name, func):
        """添加监听函数，在初始化监听函数时调用"""
        super()._add_consumer(queue_name, func)
        channel = self._get_channel(func)
        channel.queue_declare(queue=queue_name)
        channel.basic_consume(queue=queue_name,
                              on_message_callback=func)
        self._run_listener(queue_name, func, channel)

    def _run_listener(self, queue_name, func, channel):
        """运行监听函数"""
        thr = threading.Thread(target=lambda: channel.start_consuming())
        f_t = (func, thr)
        if queue_name not in self.listener:
            self.listener[queue_name] = [f_t]
        else:
            self.listener[queue_name].append(f_t)

        thr.start()

    def _consume_around_process(self, queue_name, fun, channel, method, properties, body):
        msg_id = self.consumers_counter[queue_name]
        logger = self.logger
        msg_id = self.consumers_counter[queue_name]
        logger.info(f"[{queue_name}.{fun.__name__}] Received Msg-{msg_id} from Queue[{queue_name}]")
        logger.debug(f"[{queue_name}.{fun.__name__}] Start Msg-{msg_id}: {body}")
        if self.tracked:
            """跟踪执行时间"""
            start_time = time.time()
            try:
                fun(channel=channel, method=method, properties=properties, body=body)
                logger.debug(
                    f"[{queue_name}.{fun.__name__}] Finish Msg-{msg_id} in [{time.time() - start_time}]")
            except Exception as e:
                logger.error(f"[{queue_name}.{fun.__name__}] Finish Msg-{msg_id} in [{time.time()}]")
                logger.error(f"[{queue_name}.{fun.__name__}] Error Msg-{msg_id}", exc_info=e)
        else:
            fun(channel=channel, method=method, properties=properties, body=body)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def _build_publisher_wrapper(self, func, queue_name, exchange):
        return MQPublisherWrapper(func, queue_name, self._get_channel(func), self.logger, self.exchange)
