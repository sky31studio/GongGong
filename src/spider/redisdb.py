from typing import Union

from redis import Redis
from redis.asyncio import Redis as AsyncRedis


class RedisDict(dict[str, object]):

    def __init__(self, redis: Union[Redis, AsyncRedis], expiry: int = 3600):

        super().__init__()
        self.redis = redis
        self.expire = expire

    def __iter__(self):
        return iter(self.redis.keys())

    def __repr__(self):
        return f"<RedisDict {self.redis}>"

    def __len__(self):
        return self.redis.dbsize()

    def __getitem__(self, key):
        value = self.redis.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        if self.expire:
            self.redis.set(key, value, ex=self.expire)
        else:
            self.redis.set(key, value)

    def __delitem__(self, key):
        if not self.redis.delete(key):
            raise KeyError(key)

    def __contains__(self, key: str):
        return self.redis.exists(key)

    def __del__(self):
        self.redis.close()
