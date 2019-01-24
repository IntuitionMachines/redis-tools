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

## Redis Dump Utils
A simple dump tool that dumps to the storage solution of your choice.

### Usage
To use the dump, simply pass it a write function, and a list of the keys you wish to match.

```python
from redistools.dump import dump

load_batch(file_dump.write, matches)
```

Uses the following enviroment variables:
```
EXPIRE_TIME (int)
BATCH_SIZE (int)
DELETE_KEYS (str == 'True' or 'False')
INDIVIDUAL_FILES (str == 'True' or 'False')
DECODE_RESPONSES (str == 'True' or 'False')
```
INDIVIDUAL_FILES is a flag for whether or not you want each key to (and its values) to an individual file.

DELETE_KEYS is flag for whether or not you want to delete the keys after each batch is done being processed. Delete is faster than expire, as you have to expire keys individually. If DELETE_KEYS is set, and you are looping through each key to output to individual files, keys will be expired instead. ***CAUTION: IF YOU ARE USING THIS, AND YOU ARE NOT LOOPING THROUGH THE KEYS, YOUR KEYS WILL BE DELETED.*** With the most up-to-date version of Redis, there is no way to expire keys in a batch. You must loop through, and expire individually.

BATCH_SIZE is how many keys to get at once, this is equivalent to COUNT when you set count in a cursor, in redis.py.

EXPIRE is the TTL for each key (in seconds). This is only used when you want to loop through and output to individual files. The default is set to one day.  

DECODE_RESPONSES is a flag set for human readable JSON over bytes. This is set to True by default.

The output files are `${match}_${key}_${date}.json`. As of right now, the only format outputted is JSON. 

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
