import functools
import logging
from typing import Tuple

import pika.channel


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

    def publish_result(self, result):
        """发布结果函数，用于发布函数执行后的处理函数"""
        self.publish_counter += 1

    def __call__(self, *args, **kwargs):
        self._publish_pre_process(*args, **kwargs)
        result = self._publish_around_process(*args, **kwargs)
        self._publish_post_process(result, *args, **kwargs)
        self.publish_result(result)
        return result


class MQPublisher:
    """负责消息队列的发布。但是不负责消息队列的连接和关闭。"""

    def __init__(self):
        self.publishers: dict[Tuple[str, str], list[PublisherWrapper]] = {}
        """发布者，用于存储发布函数"""

    def _add_publisher(self, route_key, exchange: str, func_wrapper: PublisherWrapper):
        """添加发布函数，在初始化发布函数时调用"""
        publish_func = self._build_publisher_wrapper(func_wrapper.func, route_key, exchange).publish_result
        func_wrapper.publish_result = publish_func
        if route_key not in self.publishers:
            self.publishers[(exchange, route_key)] = [func_wrapper]
        else:
            self.publishers[(exchange, route_key)].append(func_wrapper)

    def _build_publisher_wrapper(self, func, route_key, exchange):
        """构建发布函数，用于执行发布函数并返回执行结果"""
        return PublisherWrapper(func)

    def publish(self, route_key: str, exchange: str = ''):
        """
        发布消息，当被装饰的函数执行时，如果结果非空，则同步到消息队列中
        Args:
            exchange: 消息队列交换机名称
            route_key: 消息队列名称

        Returns:
            返回被装饰的函数执行结果
        """

        def decorator(func):
            wrapper = self._build_publisher_wrapper(func, route_key, exchange)
            func_wrapper = functools.wraps(func)(wrapper)
            self._add_publisher(route_key, exchange, func_wrapper)
            return func_wrapper

        return decorator


class MQPublisherWrapper(PublisherWrapper):
    def __init__(self, func, route_key, channel: pika.channel.Channel, logger=None, exchange=''):
        super().__init__(func)
        self.channel = channel
        self.exchange = exchange
        if not logger:
            logger = logging.getLogger('MQ-PUBLISHER')
        self.logger = logger
        if exchange != '':
            channel.exchange_declare(exchange)
        self.route_key = route_key

    def _publish_around_process(self, *args, **kwargs):
        body = self.func(*args, **kwargs)
        return body

    def publish_result(self, result):
        super().publish_result(result)
        logger = self.logger
        channels = self.channel
        msg_id = self.publish_counter
        logger.info(
            f"[{self.route_key}.{self.func.__name__}] Publish Msg-{msg_id} to Queue[{self.route_key}]")
        logger.debug(f"[{self.route_key}.{self.func.__name__}] Publish Msg-{msg_id}: {result}")
        channels.basic_publish(exchange=self.exchange,
                               routing_key=self.route_key,
                               body=result)
