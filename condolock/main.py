import copy
from collections import deque

from loguru import logger

from condolock.conditions import ConditionInstance



class ConditionalLock(object):
    def __init__(self, redis_instance):
        # We use a deque here to reduce iteration time from O(n) to O(1)
        # We still have to wait for each item to process, however this shouldn't take too long
        self._conditions = deque()
        self.redis_instance = redis_instance
    

    def add(self, conditional):
        """ Here we add conditions related to the keys we want to watch"""
        try:
            assert isinstance(conditional, ConditionInstance)
            conditional.setup(self.redis_instance)
            self._conditions.append(conditional)
        except AssertionError:
            logger.error("The condition class entered wasn't the correct type")
        
    

    def process(self, key):
        if (self._conditions) == 0:
            return {
                "succ_run": False,
                "latest": None, 
                "collection": []
            }
        result_collection = []
        previous_result = None
        current_conditions = copy.copy(self._conditions)
        while len(current_conditions) != 0:
            item = current_conditions.popleft()
            previous_result = item.process(key, prior=previous_result)
            result_collection.append(previous_result)
        return {
            "succ_run": True,
            "latest": previous_result, 
            "collection": result_collection
        }

class ConditionalLockContext(object):
    def __init__(self, key, lock:ConditionalLock, *args, **kwargs):
        self.lock = lock
        self.key = key
    
    def __enter__(self):
        proc_res = self.lock.process(self.key)
        latest = proc_res['latest']
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exits the lock context")
        