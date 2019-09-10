import copy
from collections import deque

from loguru import logger

from redis import Redis
from conlock.conditions import ConditionInstance



class ConditionalLock(object):
    def __init__(self, redis_instance:Redis):
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

    def close(self, key):
        """ Close the conditions so they wont pass next time, if they shouldn't """
        logger.info("Starting to close the lock")
        
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
            item.close(key)
            # result_collection.append(previous_result)
        

class ConditionalLockContext(object):
    def __init__(self, key, lock:ConditionalLock, *args, **kwargs):
        self.lock = lock
        self.key = key
        self.updater = UpdateContext(self.key, self.lock.redis_instance)
    
    def __enter__(self):
        logger.debug("Entering the context")
        proc_res = self.lock.process(self.key)
        latest = proc_res['latest']
        self.updater.set_active(latest.success)
        return self.updater
        
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Exiting the context")
        self.lock.close(self.key)
        logger.debug("Finished exiting")

class UpdateContext(object):
    def __init__(self, key, redis_instance:Redis, *args, **kwargs):
        """Used to update the lock"""
        self.redis_instance = redis_instance
        self.key = key
        self.default_item_name = "model"
        self.is_active = True

    def set_default_name(self, name):
        self.default_item_name = name
        return self

    def set_active(self, is_active):
        self.is_active = is_active
        return self

    def update(self, item, name=None):
        if name is None:
            name = self.default_item_name
        item_key = f"{self.key}:{self.default_item_name}"
        self.redis_instance.set(item_key, item)
        return self