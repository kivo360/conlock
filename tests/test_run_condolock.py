"""
    We're doing a test run of the conditional lock. This is just to see if we can instatiate the code without it breaking (prolly not)
"""

import time
import uuid
import unittest
import multiprocessing
from random import choice
from collections import Counter

from redis import Redis
from loguru import logger

from conlock import ConditionalLock, ConditionalLockContext
from conlock.conditions import WaitAtLeast


from test_daemon import SimplexDaemon


class CondoLockCases(unittest.TestCase):
    def setUp(self):
        self.cpu_count = multiprocessing.cpu_count()
        self.sending_queue = multiprocessing.Queue()
        self.recieving_queue = multiprocessing.Queue()
        self.test_daemons = [
            SimplexDaemon(self.sending_queue, self.recieving_queue) 
            for _ in range(self.cpu_count)
        ]
        
        



    def test_100_locks(self):
        [x._start() for x in self.test_daemons]
        key = uuid.uuid4().hex
        for i in range(100):
            current_daemon = choice(self.test_daemons)
            self.sending_queue.put(key)
        
        start_time = time.time()
        results = []
        logger.info("Collecting results")
        while True:
            # Collect results here and get the time delta
            current_time = time.time()
            time_delta = current_time - start_time
            res = self.recieving_queue.get(block=True)
            results.append(res)

            if time_delta >= 30 or len(results) == 100:
                break
            logger.debug("Not finished yet ... continuing")
            time.sleep(0.1)
        # Count the results 
        count = Counter(results)
        
        print(count)
        
        # Tear Down Daemons
        self.assertGreaterEqual(count["True"], 30)
        self.assertLessEqual(count["True"], 65)

        self.assertGreaterEqual(count["False"], 30)
        self.assertLessEqual(count["False"], 65)
        [x._stop() for x in self.test_daemons]
        
# single_hex = uuid.uuid4().hex
# red_instance = Redis()
# clock = ConditionalLock(red_instance)
# clock.add(WaitAtLeast(seconds=10))
# with ConditionalLockContext(key=single_hex, lock=clock) as context:
#     context.update("Hello World")

# with ConditionalLockContext(key=single_hex, lock=clock):
#     context.update("Hello World")

# logger.debug("Sleeping like a boss.")
# time.sleep(11)
# with ConditionalLockContext(key=single_hex, lock=clock):
#     context.update("Hello World")

if __name__ == "__main__":
    unittest.main()