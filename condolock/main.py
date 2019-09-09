from 


class ConditionalLock(object):
    def __init__(self):
        self._conditions = deque()
    

    def add(self, condtional: ConditionInstance):
        """ Here we add conditions related to the keys we want to watch"""
        self._conditions.append(conditional)
    

    def process(self, key):
        if (self._conditions) == 0:
            return False

        previous_result = None
        current_conditions = copy.copy(self.conditions)
        while len(current_conditions) != 0:
            item = current_conditions.pop_left()
            previous_result = item.process(previous_result)
            # Checking if we should quit here
            if previous is not None:
                if previous.is_stop == True:
                    return False # IDK, I should have something here