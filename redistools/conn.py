import os
from redis import StrictRedis
from redis.sentinel import Sentinel

TRACE = os.getenv('TRACE_REDIS', 'false').lower() == "true"

if TRACE:
    import inspect
    import logging
    import json
    logger = logging.getLogger('redisutils')
    logger.setLevel(logging.DEBUG)
    logger_function = logger.debug

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
                frame_index = 0
                if len(stack) > 1:
                    frame_index += 1
                frame = stack[frame_index]
                while 'redistools' in stack[frame_index].filename:
                    if frame_index < len(stack):
                        frame_index += 1
                        frame = stack[frame_index]
                    else:
                        break
                if frame.code_context and len(frame.code_context):
                    context = frame.code_context[0].strip()
                else:
                    context = None
                machine_readable_stack_frame = dict(
                    filename=frame.filename,
                    lineno=frame.lineno,
                    function=frame.function,
                    redis_verb=name,
                    args=args,
                    kwargs=kwargs,
                    context=context)
                logger_function(json.dumps(machine_readable_stack_frame))
            if name.upper() in SLAVEABLE_FUNCS:
                return getattr(self.get_slave(), name)(*args, **kwargs)
            else:
                if self.slaveonly:
                    raise ("Unable to run master command in slave only mode")
                else:
                    return getattr(self.get_master(), name)(*args, **kwargs)

        return handlerFunc
