# Condolock

Stop Redis race conditions in their tracks. `condolock` (standing for `Cond`itional `Lock`) is a distributed conditional lock library for python. Put repeatable conditions on keys and ensure they don't get changed before you say they're supposed to change. 

**Match Conditions Before Changing**


We're using a form of a strategy pattern to allow dynamically setting conditions for the lock.


### Manual Time Checking -- Modify Data After At Least N seconds have passed

To understand why we'd want to create a replicatable lock. Let's run through a manual example. Lets say we want to save information only after 5 minutes have passed, meaning any time we attempt to save before 600 seconds have passed is skipped. This is good to ensure that when multiple machines have a background scheduler to update a field inside of redis or any other location don't do so. 


5 minutes equals 600 seconds. We provide a editing method for each.


Here's the manual example. Assume that this code would be running on every possible machine inside of a background process or thread, to try updating the models available every few seconds.
```py
import time
import redis

redis_host = "localhost"
redis_port = 6379
redis_password = ""
item_key = 'd59be26104f84fca8dc78dbdf8d64763'

r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

last_edit_time = (time.time() - 600)
r.set(f"{item_key}:last_edit", last_edit_time)

def process():
    print("Further Processing Has Been Completed")

def set_time_and_process(key):
    with r.lock(f"{key}:lock"):
        nlatest_time = time.time()
        r.set(f"{item_key}:last_edit", nlatest_time)
    process()
min_seconds = 600
current_time = (time.time()) # The last time must be more than this amount of time
red_last_edit_time = r.get(f"{item_key}:last_edit")
if (red_last_edit_time is None):
    print(f"Act as if {min_seconds} seconds have passed since the last timestamp")
    set_time_and_process()


time_delta = (current_time - float(red_last_edit_time))
if time_delta > min_seconds:
    print(f"At least {min_seconds} have passed since the last save")
    set_time_and_process()
```

After we check to see if a key is available, we see if the time delta from the previous time equates to 600 or greater. If not, we skip doing further operations.


With `CondoLock` this logic is simplified into a keras-like interface.

```py
from condolock import ConditionalLock, ConditionalContext
from condolock.conditions import MinTime, AccessedPrior
import redis

item_key = 'd59be26104f84fca8dc78dbdf8d64763'
r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Conditional Lock checks that all of the following conditions are true before allowing usage
lock = ConditionalLock(r)
lock.add(MinTime(n=300)) # Wait 300 seconds before allowing for the next update
lock.add(AccessedPrior(key="checking", time=300)) # Check to see if the key was worked on in a given amount of time, and that it was true.

with ConditionContext(key=item_key lock=lock) as context:
    if context.success:
        raise ValueError
    # Do work here
```


Inisde of the example you save yourself from getting the lock improperly done through manual code and make it shorter than the example above, even with .