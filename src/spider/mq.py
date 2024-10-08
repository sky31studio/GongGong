"""pika 监听装饰器"""
import functools
import logging
import threading
import time

from pika.adapters.blocking_connection import BlockingConnection


class MQPublisher:
    """负责消息队列的发布。但是不负责消息队列的连接和关闭。"""

    def __init__(self):
        self.publisher = {}
        """发布者，用于存储发布函数"""
        self.publish_counter = {}
        """发布计数器，用于存储消息数量"""

    def _publish_pre_process(self, queue_name, *args, **kwargs):
        """前置处理函数，用于在发布函数执行前的处理函数"""
        if queue_name not in self.publish_counter:
            self.publish_counter[queue_name] = 0
        self.publish_counter[queue_name] += 1

    def _publish_post_process(self, queue_name, result, *args, **kwargs):
        """后置处理函数，用于在发布函数执行后的处理函数"""
        pass

    def _publish_around_process(self, queue_name, fun, *args, **kwargs):
        """环绕处理函数，用于执行发布函数并返回执行结果"""
        return fun(*args, **kwargs)

    def _add_publisher(self, queue_name, exchange: str, func):
        """添加发布函数，在初始化发布函数时调用"""
        if queue_name not in self.publisher:
            self.publish_counter[f'{exchange}.{queue_name}'] = 0
            self.publisher[f'{exchange}.{queue_name}'] = [func]
        else:
            self.publisher[f'{exchange}.{queue_name}'].append(func)

    def publish(self, queue_name: str, exchange: str = ''):
        """
        发布消息，当被装饰的函数执行时，如果结果非空，则同步到消息队列中
        Args:
            exchange:
            queue_name: 消息队列名称

        Returns:
            返回被装饰的函数执行结果
        """

        def decorator(func):
            self._add_publisher(queue_name, exchange, func)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                self._publish_pre_process(queue_name, *args, **kwargs)
                result = self._publish_around_process(queue_name, func, *args, **kwargs)
                self._publish_post_process(queue_name, result, *args, **kwargs)
                return result

            return wrapper

        return decorator


class MQConsumer:
    """负责消息队列的监听和发布。但是不负责消息队列的连接和关闭。"""

    def __init__(self):
        self.consumers = {}
        """消费者，用于存储消费者函数。"""
        self.consumers_counter = {}
        """计数器，用于存储消息数量"""

    def _add_consumer(self, queue_name, func):
        """添加监听函数，在初始化监听函数时调用"""
        if queue_name not in self.consumers:
            self.consumers_counter[queue_name] = 0
            self.consumers[queue_name] = [func]
        else:
            self.consumers[queue_name].append(func)

    def _consume_pre_process(self, queue_name, channel, method, properties, body):
        """前置处理函数，用于在发布函数执行前的处理函数"""
        if queue_name not in self.consumers_counter:
            self.consumers_counter[queue_name] = 0
        self.consumers_counter[queue_name] += 1

    def _consume_post_process(self, queue_name, result, channel, method, properties, body):
        """后置处理函数，用于在发布函数执行后的处理函数"""
        pass

    def _consume_around_process(self, queue_name, fun, channel, method, properties, body):
        """环绕处理函数，用于执行监听函数并返回执行结果"""
        return fun(channel, method, properties, body)

    def build_wrapper(self, queue_name: str, func):
        """构建监听函数，用于执行监听函数并返回执行结果"""

        @functools.wraps(func)
        def decorator(channel, method, properties, body):
            self._consume_pre_process(queue_name, channel, method, properties, body)
            result = self._consume_around_process(queue_name, func, channel, method, properties, body)
            self._consume_post_process(queue_name, result, channel, method, properties, body)
            return result

        return decorator

    def listen(self, queue_name: str, *args, **kwargs):
        """
        监听消息队列
        Args:
            queue_name: 消息队列名称
        Returns:

        """

        def decorator(func):
            f = self.build_wrapper(queue_name, func)
            self._add_consumer(queue_name, f)
            return func

        return decorator


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

    def _publish_around_process(self, queue_name, func, *args, **kwargs):
        """
        发布消息，当被装饰的函数执行时，如果结果非空，则同步到消息队列中
        Args:
            queue_name: 消息队列名称
            func: 发布函数

        Returns:
            返回被装饰的函数执行结果
        """
        msg_id = self.publish_counter[queue_name]
        logger = self.logger
        channels = self._get_channel(func)
        channels.queue_declare(queue=queue_name)
        body = func(*args, **kwargs)
        if body:
            self.publish_counter[queue_name] += 1
            msg_id = self.publish_counter[queue_name]
            logger.info(
                f"[{queue_name}.{func.__name__}] Publish Msg-{msg_id} to Queue[{queue_name}]")
            logger.debug(f"[{queue_name}.{func.__name__}] Publish Msg-{msg_id}: {body}")
            channels.basic_publish(exchange=self.exchange,
                                   routing_key=queue_name,
                                   body=body)
        return body
