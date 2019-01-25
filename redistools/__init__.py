'''
redis-helpers library

(C) 2019 hCaptcha. Released under the MIT license.
'''
import os
from redistools.conn import Conn
from redistools.serde import RedisDict, RedisList, RedisSet

CONN = Conn()
# Heat up the redis cache
if "true" in os.getenv("PREPING", 'false').lower():
    CONN.ping()
