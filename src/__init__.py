'''
redis-helpers library

(C) 2018 hCaptcha. Released under the MIT license.
'''
print ("hmtredishelp version 0.21.1")
import os

from redis import StrictRedis
from redis.sentinel import Sentinel
from conn import Conn

SLAVEABLE_FUNCS = [
    "DBSIZE", "DEBUG", "GET", "GETBIT", "GETRANGE", "HGET", "HGETALL", "HKEYS",
    "HLEN", "HMGET", "HVALS", "INFO", "LASTSAVE", "LINDEX", "LLEN", "LRANGE",
    "MGET", "RANDOMKEY", "SCARD", "SMEMBERS", "RANDOMKEY", "SCARD", "SMEMBERS",
    "SRANDMEMBER", "STRLEN", "TTL", "ZCARD", "ZRANGE", "ZRANGEBYSCORE",
    "ZREVRANGE", "ZREVRANGEBYSCORE", "ZSCORE"
]

CONN = Conn()
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
