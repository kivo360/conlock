import time
import redis

redis_host = "localhost"
redis_port = 6379
redis_password = ""
item_key = 'd59be26104f84fca8dc78dbdf8d64763'

r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

last_edit_time = (time.time() - 700)
r.set(f"{item_key}:last_edit", last_edit_time)

def process():
    print("Further Processing Has Been Completed")

def set_time_and_process():
    nlatest_time = time.time()
    r.set(f"{item_key}:last_edit", nlatest_time)
    process()
min_seconds = 600
current_time = (time.time()) # The last time must be more than this amount of time
red_last_edit_time = r.get(f"{item_key}:last_edit")
if (red_last_edit_time is None):
    print(f"Act as if {min_seconds} seconds have passed since the last timestamp")


time_delta = (current_time - float(red_last_edit_time))
if time_delta > min_seconds:
    print(f"At least {min_seconds} have passed since the last save")