# redis-tools
A set of Redis wrappers for transparent cluster scale-out and backing store abstraction.

Install the latest version of redis-tools like so:
```bash
pip install git++https://github.com/IntuitionMachines/redis-tools.git#egg=redistools
```
or add it to your requirements.txt

## Legacy
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
INDIVIDUAL_FILES (str == 'True' or 'False')
```

## RedisDict
Python Dict-style abstraction class that enables transparent fetch and update against a redis hash backing store.

## Testing
In order to run the tests, make sure you have a local Redis running.
From there, run ```python3 ./tests/tests.py```

## Docker
To develop locally:
Add a folder in the root directory named `redis` and place in a .rdb file.
From there, simply `docker-compose build`
Then `docker-compose run -d redis`
Then export your env vars, and `docker-compose up` to get a shell in the container.

Authors:

posix4e, tinkerer, and alikoneko.

(C) 2018 hCaptcha.

    * Not our terminology of choice, but keeping here to remain consistent with redis usage.
