# Condolock

This is a conditional lock for Redis. The general reason for this project is that we want to prevent distributed race conditions with redis. This is where you have multiple machines that attempt to access the exact same resource, and overwrite it with its copy of information. For a given resource (everything related to a specific hash), we only want to allow access on that resource given a specific set of condition.


```py
from condolock import ConditionalLock, ConditionalContext
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Conditional Lock checks that all of the following conditions are true before allowing usage
lock = ConditionalLock(r)
lock.add(MinTime(n=300)) # Wait 300 seconds before allowing for the next update
lock.add(IsPrior(key="checking", time=300)) # Check to see if the key was worked on in a given amount of time, and that it was true.

with ConditionContext(lock=lock, lock_name="qdhfG3usduAuw") as context:
    if context.success:
        raise ValueError
    # Do work here
```


---

**Put GIF Here Showing What It Looks Like**

---


## A More Detailed Look

In case you're trying to figure out more. The main purpose to this is to save models and its related data inside of redis. Let's look at an example here about how to store complex objects inside of redis (using python).
 
Your normal code would look like the following.
```py
import pickle
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)
obj = ExampleObject()
pickled_object = pickle.dumps(obj)
r.set('some_key', pickled_object)
unpacked_object = pickle.loads(r.get('some_key'))
obj == unpacked_object
```

You could then pull this object then use it on another machine if you felt like it. The problem arises when I expand that the access to that particular key to +10 cores/threads/machines. Race-conditions. The Redis team was smart. They crafted a distributed lock. 

It looks like this.
```py
with r.lock('my_lock'):
    r.set('foo', 'bar')
```

