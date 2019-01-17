'''
Classes for serializing and deserializing redis data into json
'''


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
