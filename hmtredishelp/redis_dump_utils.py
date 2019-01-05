import logging
import os
import json
import datetime
from hmtredishelp import RedisConn

EXPIRE = int(os.getenv("EXPIRE", "86400"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10000"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "10000"))
DELETE_KEYS = "true" in os.getenv("DELETE_KEYS", "false")).lower()
LOG = logging.getLogger("redis_dump")
CONN = RedisConn()

fns = []  # type: ignore

def load_batch(write_function, matches, batch=BATCH_SIZE):
    today = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    for match in matches: 
        process_raw(match, today, write_function)

def dump_to_file(data, filename, write_function):
    write_function(filename, json.dumps(data))
    fns.append(filename)

def process_raw(match, date, write_function):
    cursor = '0'
    data = {}
    count = 0
    while cursor != 0:
        cursor, keys = CONN.scan(match=f'{match}_*', cursor=cursor, count=BATCH_SIZE) # match the keys we want to grab
        keys = [key.decode('utf-8') for key in keys if not key == None] # decode keys, throw out blank keys
        values = CONN.mget(keys) # grab the formatted keys
        fixed_values = [] #
        # fix values for output, set blank values to an empty dict
        for value in values:
            if not value:
                value = b'{}'
            fixed_values.append(value.decode('utf-8'))
        data.update(dict(zip(keys, fixed_values))) # map the values to the keys, and put in dict
        
        # dump batch to file and reset dict - expire/delete keys here
        filename = f'{match}_{date}_{count}.json'
        dump_to_file(data, filename, write_function)
        # delete on flag
        if DELETE_KEYS:
            CONN.delete(*keys) # delete keys
        # data.clear() # free memory
        count += 1
