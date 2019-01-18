'''
redis-helpers library

(C) 2019 hCaptcha. Released under the MIT license.
'''
import os
from redistools.conn import Conn
from redistools.serde import RedisDict, RedisList, RedisSet
from redistools.dump import load_batch

CONN = Conn()
# Heat up the redis cache
if "true" in os.getenv("PREPING", 'false').lower():
    CONN.ping()