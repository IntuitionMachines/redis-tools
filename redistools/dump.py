import logging
import os
import json
import datetime

from redistools.conn import Conn
from redistools.serde import RedisDict, RedisList, RedisSet

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10000"))  # size of each key-batch
DELETE_KEYS = "true" in os.getenv(
    "DELETE_KEYS",
    "false").lower()  # if true, keys in batch will be deleted after every run
INDIVIDUAL_FILES = "true" in os.getenv(
    "INDIVIDUAL_FILES", "false").lower()  # export each key to its own file
EXPIRE = int(os.getenv("EXPIRE", "86400"))

LOG = logging.getLogger("redis_dump")
CONN = Conn()

fns = []  # type: ignore
'''
These are tools for dumping Redis to S3/minio or your storage of your choice. 
'''
'''
This is a function that takes in a list of matches and processes the raw matches into 
a json format
'''


def load_batch(write_function,
               matches,
               batch=BATCH_SIZE,
               individual_files=INDIVIDUAL_FILES):
    today = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    for match in matches:
        process_raw(match, today, write_function, individual_files)
    return fns


'''
Helper function that calls the write function passed to it, and 
dumps them to a file with the given name of ${date}_${match}_${chunk}.json
'''


def dump_to_file(data, filename, write_function):
    write_function(filename, json.dumps(data))
    fns.append(filename)


'''
Function that processes the data and makes the file names
'''


def process_raw(match, date, write_function, individual_files):
    count = 0
    cursor = '0'
    while cursor != 0:
        cursor, keys = CONN.scan(
            match=match, cursor=cursor,
            count=BATCH_SIZE)  # match the keys we want to grab
        keys = [key.decode('utf-8') for key in keys
                if not key == None]  # decode keys, throw out blank keys
        if individual_files:
            for key in keys:
                fixed_values = get_data(key)  # get each value
                # dump batch to file and reset dict - expire/delete keys here
                filename = f'{match}_{key}_{date}_{count}.json'
                zip_and_dump(key, fixed_values, filename, write_function)
                if DELETE_KEYS:
                    if CONN.ttl(key) > EXPIRE:
                        CONN.expire(
                            key
                        )  # only set expire if it is greater than the EXPIRE time.
        else:
            fixed_values = get_data(keys)
            filename = f'{match}_{date}_{count}.json'
            zip_and_dump(keys, fixed_values, filename, write_function)
        # delete on flag
        if DELETE_KEYS:
            CONN.delete(*keys)  # delete keys
        count += 1


'''
This function 
'''


def get_data(keys):
    if INDIVIDUAL_FILES:
        key_type = CONN.type(keys).decode('utf-8')

        # switch based on type, utilizing the serde library
        if "hash" in key_type.lower():
            values = RedisDict(CONN, keys).get()
        elif "set" in key_type.lower():
            values = RedisSet(CONN, keys).get()
        elif "list" in key_type():
            values = RedisList(CONN, keys).get()
        else:
            values = CONN.mget(keys)
    else:
        values = CONN.mget(keys)

    return decode_data(values)


'''
helper method for zipping the data, and dumping it to a file. 
'''


def zip_and_dump(keys, values, filename, write_function):
    data = {}
    data.update(dict(zip(keys, values)))
    dump_to_file(data, filename, write_function)


'''
helper method for returning the data not as bytes for strings, dicts, lists, and sets
TODO: implent other functionality for what may be returned from redis
'''


def decode_data(data):
    # if it just a string, map it and decode it
    if isinstance(data, bytes): return data.decode()
    # map it and decode it if it is not just a string
    if isinstance(data, dict): return dict(map(decode_data, data.items()))
    if isinstance(data, list): return list(map(decode_data, data))
    if isinstance(data, set): return set(map(decode_data, data))
