"""
    We're doing a test run of the conditional lock. This is just to see if we can instatiate the code without it breaking (prolly not)
"""

import time
import uuid

from redis import Redis
from loguru import logger

from conlock import ConditionalLock, ConditionalLockContext
from conlock.conditions import WaitAtLeast

single_hex = uuid.uuid4().hex
red_instance = Redis()
clock = ConditionalLock(red_instance)
clock.add(WaitAtLeast(seconds=10))
with ConditionalLockContext(key=single_hex, lock=clock) as context:
    context.update("Hello World")

with ConditionalLockContext(key=single_hex, lock=clock):
    context.update("Hello World")

logger.debug("S")
time.sleep(11)
with ConditionalLockContext(key=single_hex, lock=clock):
    context.update("Hello World")