import abc
from redis import Redis


class RLLogic(object):
    def __init__(self, *args, **kwargs):
        self.__dict__['success'] = False
        self.__dict__['message'] = "The logic doesn't meet prior conditions"

    def __setattr__(self, name, value):
        self.__dict__[name] = value


class ConditionInstance(abc.ABCMeta):
    def __init__(self, *args, **kwargs):
        self.redis_instance = None
        self.lock_name = ""
        self.require_prior = False

    def check_exist(self, key:str) -> bool:
        """ Check if the key of the given name exists. If not, we return False"""
        raise NotImplementedError("This needs to exist, with proper information of what to do if the key doesn't exist yet.")


    def process(self, key, prior=None, **kwargs):
        """ Gets the prior information and determines if we should do any further processing on the current condition. """
        raise NotImplementedError("Process function wasn't implemented, please overwrite it")
    
    def setup(self, redis_instance: Redis, **kwargs):
        raise NotImplementedError("You need to call a proper setup function.")
    
    def check_setup(self, *args, **kwargs):
        """ Raises an exception if we haven't recieved the required information yet. Usually this is called after setting up the correct function.  """
        if self.redis_instance is None:
            raise NotImplementedError("You should have set a redis instance by now.")
        if self.lock_name == "":
            raise NotImplementedError("This lock needs a name")
    
    def return_dict(self):
        pass