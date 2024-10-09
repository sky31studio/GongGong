import functools
import logging


class PublisherWrapper:
    """负责消息队列的发布。发布函数执行时使用该类。"""

    def __init__(self, func):
        self.publish_counter = 0
        """发布计数器，用于存储消息数量"""
        self.func = func

    def _publish_pre_process(self, *args, **kwargs):
        """前置处理函数，用于在发布函数执行前的处理函数"""
        pass

    def _publish_post_process(self, result, *args, **kwargs):
        """后置处理函数，用于在发布函数执行后的处理函数"""
        pass

    def _publish_around_process(self, *args, **kwargs):
        """环绕处理函数，用于执行发布函数并返回执行结果"""
        return self.func(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.publish_counter += 1
        self._publish_pre_process(*args, **kwargs)
        result = self._publish_around_process(*args, **kwargs)
        self._publish_post_process(result, *args, **kwargs)
        return result


class MQPublisher:
    """负责消息队列的发布。但是不负责消息队列的连接和关闭。"""

    def __init__(self):
        self.publisher = {}
        """发布者，用于存储发布函数"""

    def _add_publisher(self, queue_name, exchange: str, func):
        """添加发布函数，在初始化发布函数时调用"""
        if queue_name not in self.publisher:
            self.publisher[f'{exchange}.{queue_name}'] = [func]
        else:
            self.publisher[f'{exchange}.{queue_name}'].append(func)

    def _build_publisher_wrapper(self, func, queue_name, exchange):
        """构建发布函数，用于执行发布函数并返回执行结果"""
        return PublisherWrapper(func)

    def publish(self, queue_name: str, exchange: str = ''):
        """
        发布消息，当被装饰的函数执行时，如果结果非空，则同步到消息队列中
        Args:
            exchange: 消息队列交换机名称
            queue_name: 消息队列名称

        Returns:
            返回被装饰的函数执行结果
        """

        def decorator(func):
            wrapper = self._build_publisher_wrapper(func, queue_name, exchange)
            func_wrapper = functools.wraps(func)(wrapper)
            self._add_publisher(queue_name, exchange, func_wrapper)
            return func_wrapper

        return decorator


class MQPublisherWrapper(PublisherWrapper):
    def __init__(self, func, queue_name, channel, logger=None, exchange=''):
        super().__init__(func)
        self.channel = channel
        self.exchange = exchange
        if not logger:
            logger = logging.getLogger('MQ-PUBLISHER')
        self.logger = logger
        channel.queue_declare(queue=queue_name)
        self.queue_name = queue_name

    def _publish_around_process(self, *args, **kwargs):
        body = self.func(*args, **kwargs)
        return body

    def _publish_post_process(self, result, *args, **kwargs):
        logger = self.logger
        channels = self.channel
        msg_id = self.publish_counter
        logger.info(
            f"[{self.queue_name}.{self.func.__name__}] Publish Msg-{msg_id} to Queue[{self.queue_name}]")
        logger.debug(f"[{self.queue_name}.{self.func.__name__}] Publish Msg-{msg_id}: {result}")
        channels.basic_publish(exchange=self.exchange,
                               routing_key=self.queue_name,
                               body=result)
