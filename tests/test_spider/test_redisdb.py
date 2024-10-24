from unittest import TestCase

from redis.asyncio import Redis

from spider.redisdb import RedisDict


class TestRedisDict(TestCase):
    def test_redis_dict(self):
        d = RedisDict(Redis())
        d['Hello'] = 'World'
