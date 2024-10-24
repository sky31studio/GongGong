import pika
from redis import Redis

from spider.banner import Banner
from spider.config.app_config import ActiveQueueConfig, TaskConf
from spider.config.log_config import logging_config
from spider.config.rabbitmq_config import MQConfig
from spider.config.redis_config import RedisConfig
from spider.consumer import StudentConsumer
from spider.mq import MQ, MQRouter
from spider.redisdb import RedisDict
from xtu_ems.ems.handler import Handler
from xtu_ems.ems.handler.get_student_courses import StudentCourseGetter
from xtu_ems.ems.handler.get_student_exam import StudentExamGetter
from xtu_ems.ems.handler.get_students_transcript import StudentTranscriptGetter

credentials = pika.PlainCredentials(username=MQConfig.MQ_USERNAME, password=MQConfig.MQ_PASSWORD)
param = pika.ConnectionParameters(host=MQConfig.MQ_HOST,
                                  port=MQConfig.MQ_PORT,
                                  virtual_host=MQConfig.MQ_VIRTUAL_HOST,
                                  credentials=credentials)
connection = pika.BlockingConnection(parameters=param)

mq = MQ(connection, prefetch_count=MQConfig.MQ_PREFETCH_COUNT)
publish_channel = connection.channel()


def register_consumer(mq: MQRouter, handler: Handler, config: TaskConf, kb, p_channel=publish_channel):
    consumer = StudentConsumer(config=config, handler=handler, kv_db=kb,
                               publish_channel=p_channel)
    mq.listen(queue_name=consumer.config.queue)(consumer)


if __name__ == '__main__':
    Banner().show()
    logging_config('MQ-CONSUMER')
    logging_config('MQ-PUBLISHER')
    logging_config('MQ')
    handlers = [
        (StudentCourseGetter(), ActiveQueueConfig.COURSE_SCHEDULE),
        (StudentTranscriptGetter(), ActiveQueueConfig.SCORE_SCHEDULE),
        (StudentExamGetter(), ActiveQueueConfig.EXAM_SCHEDULE)
    ]
    client = Redis(host=RedisConfig.REDIS_HOST,
                   port=RedisConfig.REDIS_PORT,
                   password=RedisConfig.REDIS_PASSWORD,
                   db=RedisConfig.REDIS_DB,
                   decode_responses=RedisConfig.REDIS_DECODE_RESPONSES)

    db = RedisDict(redis=client)
    for handler, config in handlers:
        publish_channel.queue_declare(queue=config.queue)
        publish_channel.queue_declare(queue=config.failed_queue)
        logging_config(config.queue)
        register_consumer(mq=mq, handler=handler, config=config, kb=db)
    mq.run()
