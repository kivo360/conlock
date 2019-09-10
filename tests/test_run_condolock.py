"""
    We're doing a test run of the conditional lock. This is just to see if we can instatiate the code without it breaking (prolly not)
"""

import time
import uuid

from redis import Redis

from condolock import ConditionalLock, ConditionalLockContext
from condolock.conditions import WaitAtLeast

single_hex = uuid.uuid4().hex
red_instance = Redis()
clock = ConditionalLock(red_instance)
clock.add(WaitAtLeast(seconds=10))
with ConditionalLockContext(key=single_hex, lock=clock):
    print("cunt")
with ConditionalLockContext(key=single_hex, lock=clock):
    print("cunt")


time.sleep(11)
with ConditionalLockContext(key=single_hex, lock=clock):
    print("cunt")