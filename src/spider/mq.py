"""pika 监听装饰器"""
import functools
import logging
import threading
import time

from pika.adapters.blocking_connection import BlockingConnection


class MQ:
    def __init__(self, connection: BlockingConnection):
        self.connection = connection
        self.counter = {}
        self.publish_counter = {}
        self.consumers = {}
        self.publisher = {}
        self.logger = logging.getLogger('MQ')
        self.listener = {}

    def listen(self, queue_name: str, tracking=True, prefetch_count=1):
        """
        监听消息队列
        Args:
            queue_name: 消息队列名称
            tracking: 是否需要跟踪执行时间
            prefetch_count: 预获取消息数量，不建议太多，虽然性能上有提升，但是可能会导致消息丢失
        Returns:

        """
        logger = self.logger
        channels = self.connection.channel()
        channels.queue_declare(queue=queue_name)
        channels.basic_qos(prefetch_count=prefetch_count)

        def decorator(func):

            def handler(channel, method, properties, body):
                self.counter[queue_name] += 1
                msg_id = self.counter[queue_name]
                logger.info(f"[{queue_name}.{func.__name__}] Received Msg-{msg_id} from Queue[{queue_name}]")
                logger.debug(f"[{queue_name}.{func.__name__}] Start Msg-{msg_id}: {body}")
                if tracking:
                    """跟踪执行时间"""
                    start_time = time.time()
                    try:
                        func(body=body, channel=channel, method=method, properties=properties)
                        logger.debug(
                            f"[{queue_name}.{func.__name__}] Finish Msg-{msg_id} in [{time.time() - start_time}]")
                    except Exception as e:
                        logger.error(f"[{queue_name}.{func.__name__}] Finish Msg-{msg_id} in [{time.time()}]")
                        logger.error(f"[{queue_name}.{func.__name__}] Error Msg-{msg_id}: {e}")
                else:
                    func(body, channel=channel, method=method, properties=properties)
                channels.basic_ack(delivery_tag=method.delivery_tag)

            if queue_name not in self.counter:
                self.counter[queue_name] = 0
            channels.basic_consume(queue=queue_name,
                                   on_message_callback=handler)
            # channels.start_consuming()
            f = lambda: channels.start_consuming()
            thr = threading.Thread(target=f)
            thr.start()
            f_t = (func, thr)
            if queue_name not in self.consumers:
                self.consumers[queue_name] = [f_t]
            else:
                self.consumers[queue_name].append(f_t)

            return func

        return decorator

    def publish(self, queue_name: str, exchange: str = '', properties=None):
        """
        发布消息，当被装饰的函数执行时，如果结果非空，则同步到消息队列中
        Args:
            exchange:
            queue_name: 消息队列名称
            properties: 消息属性

        Returns:
            返回被装饰的函数执行结果
        """
        logger = self.logger
        channels = self.connection.channel()
        channels.queue_declare(queue=queue_name)

        def decorator(func):
            if queue_name not in self.counter:
                self.publish_counter[queue_name] = 0

            if queue_name not in self.publisher:
                self.publisher[queue_name] = [func]
            else:
                self.publisher[queue_name].append(func)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                body = func(*args, **kwargs)
                if body:
                    self.publish_counter[queue_name] += 1
                    msg_id = self.publish_counter[queue_name]
                    logger.info(
                        f"[{queue_name}.{func.__name__}] Publish Msg-{msg_id} to Queue[{queue_name}]")
                    logger.debug(f"[{queue_name}.{func.__name__}] Start Msg-{msg_id}: {body}")
                    channels.basic_publish(exchange=exchange,
                                           routing_key=queue_name,
                                           body=body,
                                           properties=properties)
                    logger.debug(f"[{queue_name}.{func.__name__}] Finish Msg-{msg_id}")
                return body

            return wrapper

        return decorator
