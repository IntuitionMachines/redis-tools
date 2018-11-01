'''
redis-helpers library

(C) 2018 hCaptcha. Released under the MIT license.
'''

import os

from redis import StrictRedis
from redis.sentinel import Sentinel

SLAVEABLE_FUNCS = [
    "DBSIZE", "DEBUG", "GET", "GETBIT", "GETRANGE", "HGET", "HGETALL", "HKEYS",
    "HLEN", "HMGET", "HVALS", "INFO", "LASTSAVE", "LINDEX", "LLEN", "LRANGE",
    "MGET", "RANDOMKEY", "SCARD", "SMEMBERS", "RANDOMKEY", "SCARD", "SMEMBERS",
    "SRANDMEMBER", "STRLEN", "TTL", "ZCARD", "ZRANGE", "ZRANGEBYSCORE",
    "ZREVRANGE", "ZREVRANGEBYSCORE", "ZSCORE"
]


class RedisConn:
    '''
    simple abstraction class to transparently split redis master/slave read+write operations for scaling out e.g. redis-sentinel clusters.
    '''

    def __init__(self):
        redishost = os.getenv('REDISHOST', 'localhost')
        redisport = int(os.getenv('REDISPORT', '6379'))
        redispassword = os.getenv('REDISPW', None)
        redistimeout = float(os.getenv('REDISTIMEOUT', "1.1"))
        self.sentinelmaster = os.getenv('SENTINELMASTER')

        if redishost is "localhost":
            redissl = "true" in os.getenv('REDIS_SSL', 'False').lower()
        else:
            redissl = "true" in os.getenv('REDIS_SSL', 'True').lower()

        if self.sentinelmaster:
            self.conn = Sentinel([(redishost, redisport)],
                                 password=redispassword,
                                 socket_timeout=redistimeout,
                                 ssl=redissl)
        else:
            self.conn = StrictRedis(
                host=redishost,
                port=redisport,
                password=redispassword,
                db=0,
                decode_responses=False,
                socket_timeout=redistimeout,
                ssl=redissl)

    def get_master(self):
        if self.sentinelmaster:
            return self.conn.master_for(self.sentinelmaster)
        else:
            return self.conn

    def get_slave(self):
        if self.sentinelmaster:
            return self.conn.slave_for(self.sentinelmaster)
        else:
            return self.conn

    def __getattr__(self, name):
        def handlerFunc(*args, **kwargs):
            if name.upper() in SLAVEABLE_FUNCS:
                return getattr(self.get_slave(), name)(*args, **kwargs)
            else:
                return getattr(self.get_master(), name)(*args, **kwargs)

        return handlerFunc


CONN = RedisConn()
# Heat up the redis cache
if "true" in os.getenv("PREPING", 'false').lower():
    CONN.ping()


class RedisUtils:
    def __init__(self):
        self.conn = CONN
        self.ex = 604800

    def keys(self, filter=""):
        if (filter):
            return [k for k in self.conn.keys() if filter(k)]
        else:
            return self.conn.keys()

    def __getitem__(self, key):
        type = self.conn.type(key)
        if (type == b'hash'):
            ret = RedisDict(self.conn, key, ex=self.ex)

        elif (type == b'string'):
            ret = self.conn.get(key)

        else:
            ret = None

        if ret is not None:
            return ret
        return {}

    def __setitem__(self, key, val):
        if (type(val) == dict):
            self.conn.hmset(key, val)
        else:
            self.conn.set(key, val, ex=self.ex)


class RedisDict():
    '''
    python dict-style class that enables transparent fetch and update against a redis hash backing store.
    '''

    def __init__(self, conn, key, ex=604800):
        self.key = key
        self.conn = conn
        self.ex = ex

    def __getitem__(self, item):
        return self.conn.hget(self.key, item)

    def __contains__(self, item):
        return self.conn.hexists(self.key, item)

    def __setitem__(self, item, val):
        self.conn.hset(self.key, item, val)

    def __repr__(self):
        return repr(self.conn.hgetall(self.key))

    def __iter__(self):
        return iter(self.conn.hgetall(self.key))

    def add_items(self, items):
        self.conn.hmset(self.key, items)
