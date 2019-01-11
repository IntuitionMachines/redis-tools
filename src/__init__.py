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