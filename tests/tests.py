from redistools.conn import Conn
from redistools.serde import RedisUtils
import redistools
import time
import sys, logging
import unittest


class TestConn(unittest.TestCase):
    def test_redis_connection(self):
        '''
        Tests to see if there is in fact a redis connection available
        '''
        conn = Conn()
        self.assertEqual(conn.ping(), True, "should be pong")


class TestUtils(unittest.TestCase):
    def test_redis_connection(self):
        '''
        Tests  to see if we can use a redisutils
        '''
        ru = RedisUtils()
        ru['f'] = 'a'
        assert ru['f'] == b'a'


if __name__ == '__main__':
    unittest.main()
