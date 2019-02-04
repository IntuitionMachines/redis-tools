import os
from redis import StrictRedis
from redis.sentinel import Sentinel

TRACE = os.getenv('TRACE_REDIS', 'false') == "true"

if TRACE:
    import inspect
    logger_function = print

SLAVEABLE_FUNCS = [
    "DBSIZE", "DEBUG", "GET", "GETBIT", "GETRANGE", "HGET", "HGETALL", "HKEYS",
    "HLEN", "HMGET", "HVALS", "INFO", "LASTSAVE", "LINDEX", "LLEN", "LRANGE",
    "MGET", "RANDOMKEY", "SCARD", "SMEMBERS", "RANDOMKEY", "SCARD", "SMEMBERS",
    "SRANDMEMBER", "STRLEN", "TTL", "ZCARD", "ZRANGE", "ZRANGEBYSCORE",
    "ZREVRANGE", "ZREVRANGEBYSCORE", "ZSCORE"
]


class Conn:
    '''
    simple abstraction class to transparently split redis master/slave read+write operations for scaling out e.g. redis-sentinel clusters.
    '''

    def __init__(self):
        redishost = os.getenv('REDISHOST', 'localhost')
        redisport = int(os.getenv('REDISPORT', '6379'))
        redispassword = os.getenv('REDISPW', None)
        redistimeout = float(os.getenv('REDISTIMEOUT', "5.0"))
        self.slaveonly = "true" in os.getenv("REDIS_SLAVE_ONLY",
                                             "false").lower()
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
                socket_timeout=redistimeout,
                decode_responses=False,
                ssl_cert_reqs=None,
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
            if TRACE:
                stack = inspect.stack()
                logger_function(
                    f'REDIS: file {stack[-1].filename} at line {stack[-1].lineno} called {name} with {args} and {kwargs}'
                )
            if name.upper() in SLAVEABLE_FUNCS:
                return getattr(self.get_slave(), name)(*args, **kwargs)
            else:
                if self.slaveonly:
                    raise ("Unable to run master command in slave only mode")
                else:
                    return getattr(self.get_master(), name)(*args, **kwargs)

        return handlerFunc
