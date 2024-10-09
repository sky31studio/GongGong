import logging
import time

import pika.channel


class ConsumerWrapper:
    """负责消息队列的监听。监听函数执行时使用该类。"""

    def __init__(self, func):
        self.consume_counter = 0
        """监听计数器，用于存储消息数量"""
        self.func = func

    def _consume_pre_process(self, channel, method, properties, body):
        """前置处理函数，用于在发布函数执行前的处理函数"""
        pass

    def _consume_post_process(self, result, channel, method, properties, body):
        """后置处理函数，用于在发布函数执行后的处理函数"""
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def _exception_handle(self, e, channel, method, properties, body):
        """异常处理函数，用于处理监听函数执行时的异常"""
        channel.basic_nack(delivery_tag=method.delivery_tag)

    def _consume_around_process(self, func, channel, method, properties, body):
        """环绕处理函数，用于执行监听函数并返回执行结果"""
        return func(channel, method, properties, body)

    def __call__(self, channel, method, properties, body):
        try:
            self.consume_counter += 1
            self._consume_pre_process(channel, method, properties, body)
            result = self._consume_around_process(self.func, channel, method, properties, body)
            self._consume_post_process(result, channel, method, properties, body)
            return result
        except Exception as e:
            self._exception_handle(e, channel, method, properties, body)


class MQConsumer:
    """负责消息队列的监听和发布。但是不负责消息队列的连接和关闭。"""

    def __init__(self):
        self.consumers: dict[str, list[ConsumerWrapper]] = {}
        """消费者，用于存储消费者函数。"""

    def _add_consumer(self, queue_name, func_wrapper: ConsumerWrapper):
        """添加监听函数，在初始化监听函数时调用"""
        if queue_name not in self.consumers:
            self.consumers[queue_name] = [func_wrapper]
        else:
            self.consumers[queue_name].append(func_wrapper)

    def _build_consumer_wrapper(self, func, queue_name):
        """构建监听函数，用于执行监听函数并返回执行结果"""
        return ConsumerWrapper(func)

    def listen(self, queue_name: str):
        """
        监听消息队列，不会改变被装饰的函数
        Args:
            queue_name: 消息队列交换机名称
        Returns:

        """

        def decorator(func):
            f = self._build_consumer_wrapper(func, queue_name)
            self._add_consumer(queue_name, f)
            return func

        return decorator


class MQConsumerWrapper(ConsumerWrapper):
    def __init__(self, func, queue_name, channel: pika.channel.Channel, logger=None, tracked=True):
        super().__init__(func)
        self.queue_name = queue_name
        self.channel = channel
        if logger is None:
            logger = logging.getLogger('MQ-CONSUMER')
        self.logger = logger
        channel.queue_declare(queue=queue_name)
        self.tracked = tracked

    def _consume_around_process(self, func, channel, method, properties, body):
        logger = self.logger
        msg_id = self.consume_counter
        logger.info(f"[{self.queue_name}.{self.func.__name__}] Received Msg-{msg_id} from Queue[{self.queue_name}]")
        logger.debug(f"[{self.queue_name}.{self.func.__name__}] Start Msg-{msg_id}: {body}")
        fun = self.func
        if self.tracked:
            start_time = time.time()
            func(channel=channel, method=method, properties=properties, body=body)
            logger.debug(
                f"[{self.queue_name}.{self.func.__name__}] Finish Msg-{msg_id} in [{time.time() - start_time}]")
        else:
            fun(channel=channel, method=method, properties=properties, body=body)

    def _exception_handle(self, e, channel, method, properties, body):
        logger = self.logger
        logger.error(f"[{self.queue_name}.{self.func.__name__}] Exception Msg-{self.consume_counter}: {e}")
        super()._exception_handle(e, channel, method, properties, body)
