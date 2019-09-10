from redis import Redis
from loguru import logger
from conlock.conditions import ConditionInstance, RLLogic
import maya

class WaitAtLeast(ConditionInstance):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock_name = "atleast"

        # Why would we add a microsecond wait? That's so dumb
        self.atleast_sec = kwargs.get("seconds", 5)
        self.atleast_min = kwargs.get("minutes", 0)
        self.atleast_hours = kwargs.get("hours", 0)
        self.atleast_days = kwargs.get("days", 0)
        self.combined_key = ""
        self.combined_key_lock = ""
        self.return_logic = RLLogic()

    def is_exist(self):
        self.existing_val = self.redis_instance.get(self.combined_key)
        logger.info(self.existing_val)
        if self.existing_val is None: return False
        return True

    def setup(self, redis_instance: Redis, **kwargs):
        assert redis_instance is not None, "You're missing an active redis instance"
        self.redis_instance = redis_instance
    
    def is_pass(self):
        """ Checks if the key passes the conditon to make a change """
        # Get the current UTC epoch
        logger.info("Checking to see if the key passes certain conditions")
        now = maya.now().epoch
        existing = float(self.existing_val)
        condition = existing > now
        

        # Existing val should be the next epoch we have set prior to now.
        if condition:
            logger.error("The lock didn't pass the appropiate condition.")
            return False
        logger.success("The lock did pass successfully.")
        return True
    def get_lock_names(self, key):

        self.combined_key = f"{key}:{self.lock_name}"
        self.combined_key_lock = f"{self.combined_key}:lock"
        return self.combined_key, self.combined_key_lock

    def process(self, key, prior=None, **kwargs):
        # Determine if we can mess with the current conditional
        self.get_lock_names(key)
        should_work = self.check_prior(prior)
        if should_work:
            print(self.redis_instance)
            with self.redis_instance.lock(name=self.combined_key_lock):
                if self.is_exist():
                    if self.is_pass():
                        """ At this point we acknowledge that it passes the required conditions"""
                        self.return_logic.success = True
                        self.return_logic.message = "The required conditions returns true"
                    else:
                        self.return_logic.success = False
                        self.return_logic.message = "The lock doesn't pass the text"
                else:
                    # Just work on the code without doing much extra work.
                    self.return_logic.message = "We can run it because the previous location doesn't exist"
                    self.return_logic.success = True
                return self.return_logic
            # Do work here.

        return self.return_logic
        pass
    
    def check_prior(self, prior):
        if self.require_prior == True and prior is None:
            # Return that we failed
            return False
        
        if self.require_prior == True and prior.success == False:
            # Also returned that we failed
            return False
        return True

    def close(self, key):
        """ Changes the required variables at the end of the """
        if self.redis_instance is not None and self.return_logic.success == True:
            with self.redis_instance.lock(self.combined_key_lock):
                next_allowed_time = maya.now().add(seconds=self.atleast_sec, minutes=self.atleast_min, hours=self.atleast_hours, days=self.atleast_days).epoch
                logger.info(next_allowed_time)
                self.redis_instance.set(self.combined_key, next_allowed_time)
            # self.redis_instance.Lock(self.combined_key_lock): 
            #     # Update the information at the __init__
            #     # self.redis_instance
            #     # Get the time difference from now (dealta time)
            #     pass
