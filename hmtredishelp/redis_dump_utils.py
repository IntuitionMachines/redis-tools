import logging
import os
import json
import datetime
from hmtredishelp import RedisConn

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10000")) # size of each key-batch
DELETE_KEYS = "true" in os.getenv("DELETE_KEYS", "false").lower() # if true, keys in batch will be deleted after every run
INDIVIDUAL_FILES = "true" in os.getenv("INDIVIDUAL_FILES", "false").lower() # export each key to its own file

LOG = logging.getLogger("redis_dump")
CONN = RedisConn()

fns = []  # type: ignore
'''
These are tools for dumping Redis to S3/minio or your storage of your choice. 
'''

'''
This is a function that takes in a list of matches and processes the raw matches into 
a json format
'''
def load_batch(write_function, matches, batch=BATCH_SIZE, individual_files=INDIVIDUAL_FILES):
    today = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    for match in matches: 
        process_raw(match, today, write_function, individual_files)

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
        cursor, keys = CONN.scan(match=f'{match}_*', cursor=cursor, count=BATCH_SIZE) # match the keys we want to grab
        keys = [key.decode('utf-8') for key in keys if not key == None] # decode keys, throw out blank keys
        if individual_files:
            for key in keys:
                fixed_values = []
                fixed_values = get_data(key) # get each value
                # dump batch to file and reset dict - expire/delete keys here
                filename = f'{match}_{date}_{count}.json'
                zip_and_dump(key, fixed_values, filename, write_function)
        else:
            values = CONN.mget(keys) # grab the formatted keys
            fixed_values = [] #
            # fix values for output, set blank values to an empty dict
            for value in values:
                if not value:
                    value = b'{}'
                fixed_values.append(value.decode('utf-8'))
            filename = f'{match}_{date}_{count}.json'
            zip_and_dump(keys, fixed_values, filename, write_function)
            # delete on flag
        if DELETE_KEYS:
            CONN.delete(*keys) # delete keys
        count += 1
        
'''
This function calls mget on all keys given to it, and returns their values
'''
def get_data(keys): # this will take a individual key or a list of keys
    fixed_values = []
    values = CONN.mget(keys)
    for value in values:
        if not value:
            value = b'{}' # set value to empty dict
        fixed_values.append(value.decode('utf-8'))
    return fixed_values

'''
helper method for zipping the data, and dumping it to a file. 
'''
def zip_and_dump(keys, values, filename, write_function):
    data = {}
    data.update(dict(zip(keys, values)))
    dump_to_file(data, filename, write_function)
