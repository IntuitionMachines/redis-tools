'''
redis-helpers library

(C) 2018 hCaptcha. Released under the MIT license.
'''
import os
from conn import Conn
from serde import *
from dump import *

CONN = Conn()
# Heat up the redis cache
if "true" in os.getenv("PREPING", 'false').lower():
    CONN.ping()