import functools


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
