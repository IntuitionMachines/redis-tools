# redis-tools
A set of Redis wrappers for transparent cluster scale-out and backing store abstraction.

You can install this package like so:

```bash
pip install hmtredishelp
```

# Provided tools

## RedisConn
Simple Redis connection abstraction class that transparently splits master/slave* read+write operations for scaling out e.g. redis-sentinel clusters.

Uses the following environment variables:

```
REDISHOST (str)
REDISPORT (int)
REDISPW (str)
REDISTIMEOUT (float: seconds)
SENTINELMASTER (str)
REDIS_SSL (str == 'True' or 'False')
```

## RedisDict
Python Dict-style abstraction class that enables transparent fetch and update against a redis hash backing store.


Authors:

posix4e and tinkerer.

(C) 2018 hCaptcha.

    * Not our terminology of choice, but keeping here to remain consistent with redis usage.
