from conn import Conn
import time
import sys, logging
import unittest


class HMTRedisHelpTests(unittest.TestCase):
    def test_redis_connection(self):
        '''
        Tests to see if there is in fact a redis connection available
        '''
        conn = Conn()
        self.assertEqual(conn.ping(), True, "should be pong")


if __name__ == '__main__':
    unittest.main()
