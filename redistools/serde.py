'''
Classes for serializing and deserializing redis data into json
'''
import redistools
from redistools.conn import Conn


class RedisUtils:
    def __init__(self, **kwargs):
        self.conn = Conn(**kwargs)
        self.ex = 604800

    def keys(self, filter=""):
        if (filter):
            if (type(filter) == type("")):
                return self.conn.keys(filter)
            elif (type(filter) == type(lambda x: x)):
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

    def __iter__(self):
        return iter(self.conn.lrange(self.key, 0, -1))

    def __getitem__(self, id):
        if isinstance(id, slice):
            return self.conn.lrange(self.key, id.start, id.stop)
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
