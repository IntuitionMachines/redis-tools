'''
redis-helpers library

(C) 2018 hCaptcha. Released under the MIT license.
'''
print ("hmtredishelp version 0.21.1")
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
        self.slaveonly = "true" in os.getenv("REDIS_SLAVE_ONLY", "false").lower()
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
            if name.upper() in SLAVEABLE_FUNCS:
                return getattr(self.get_slave(), name)(*args, **kwargs)
            else:
                if self.slaveonly:
                    raise ("Unable to run master command in slave only mode")
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
            if (type(filter) == type("")):
                return self.conn.keys(filter)        
            elif (type(filter) == type(lambda x:x)):
                return [k for k in self.conn.keys() if filter(k)]
        else:
            return self.conn.keys()    
    
    def scan(self, cursor, pattern, count):
        return self.conn.scan(cursor, pattern, count)
    
    def scan_iter(self, pattern):
        return self.conn.scan_iter(pattern)
    
    def __getitem__(self, key):
        type = self.conn.type(key)
        if (type == b'hash'):
            ret = RedisDict(self.conn, key, ex=self.ex)

        elif (type == b'string'):
            ret = self.conn.get(key)
        elif (type == b'list'):
            ret = RedisList(self.conn, key, ex=self.ex)
        elif (type == b'set'):
            ret = RedisSet(self.conn, key, ex=self.ex)
        else:
            ret = None

        if ret is not None:
            return ret
        return {}

    def __setitem__(self, key, val):
        if (type(val) == dict):
            val = {str(k): str(v) for k, v in val.items()}
            self.conn.hmset(key, val)
        elif (type(val) == list):
            self.conn.rpush(key, *val)
        elif (type(val) == tuple):
            self.conn.sadd(key, *val)
        else:
            self.conn.set(key, val, ex=self.ex)
            
    def __contains__(self, key):
        return self.conn.exists(key)
        
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

    def get(self):
        return self.conn.hgetall(self.key)

    def __iter__(self):
        return iter(self.conn.hgetall(self.key))

    def add_items(self, items):
        self.conn.hmset(self.key, items)

class RedisList():
    '''
    python array-style class that enables transparent fetch and update against a redis list.
    '''
    def __init__(self, conn, key, ex=604800):
        self.key = key
        self.conn = conn
        self.ex = ex

    def lpush(self, value):
        return self.conn.lpush(self.key, value)

    def lpop(self, value):
        return self.conn.lpop(self.key, value)

    def rpush(self, value):
        return self.conn.rpush(self.key, value)

    def rpop(self, value):
        return self.conn.rpop(self.key, value)

    def get(self):
        return self.conn.lrange(self.key, 0, -1)

    def __contains__(self, item):
        return item in self.conn.lrange(self.key, 0, -1)
    def trim(self, start, stop):
        return self.conn.ltrim(self.key, start, stop)

    def __repr__(self):
        return repr(self.conn.lrange(self.key, 0, -1))

    def __getitem__(self, id):    
        if isinstance(id, slice):
            return  self.conn.lrange(self.key, id.start, id.stop) 
        return self.conn.lindex(self.key, id)

    def __setitem__(self, id, value):
        return self.conn.lset(self.key, id)

    def __len__(self):
        return self.conn.llen(self.key)

class RedisSet():
    '''
    python array-style class that enables transparent fetch and update against a redis set
    '''
    def __init__(self, conn, key, ex=604800):
        self.key = key
        self.conn = conn
        self.ex = ex

    def get(self):
        return self.conn.smembers(self.key)

    def __repr__(self):
        return repr(self.conn.smembers(self.key))

    def __contains__(self, item):
        return self.conn.sismember(self.key, item)

    def add(self, item):
        return self.conn.sadd(self.key, item)

    def rem(self, item):
        return self.conn.srem(self.key, item)

    def __len__(self):
        return self.conn.scard(self.key)
