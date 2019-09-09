from condolock.conditions import ConditionInstance



class AtLeast(ConditionInstance):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock_name = "atleast"
        self.atleast_min = kwargs.get("minutes")
    
    def setup(self, redis_instance: Redis, **kwargs):
        self.check_setup()

    def process(self, key, prior=None, **kwargs):
        pass