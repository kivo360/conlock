""" Class to test the conditional lock using """
import time
import os
from random import choice
import multiprocessing
import threading
from multiprocessing import Queue

from loguru import logger
from redis import Redis

from conlock import ConditionalLock, ConditionalLockContext
from conlock.conditions import WaitAtLeast

class SimplexDaemon(multiprocessing.Process):
    def __init__(self, message_queue:Queue, result_queue:Queue, **kwargs):
        multiprocessing.Process.__init__(self)
        self.run_interval = kwargs.get("interval", 5)
        self.receive_interval = kwargs.get("interval", 1)
        self.redis_instance = Redis()
        self.daemon = True
        self.target = self.run

        self.message_queue = message_queue
        self.result_queue = result_queue
        self.local_queue = Queue()
        
        # Create a simple conditional lock.
        self.lock = ConditionalLock(self.redis_instance)
        self.lock.add(WaitAtLeast(seconds=3))

        self.recieving_function = threading.Thread(target=self.receivce_data, daemon=True)
        

    def make_change(self, key):
        """ Make change to the conditional lock """
        # Transmit the final result to the result queue.
        

        change_result = choice([True, False])
        self.result_queue.put(str(change_result))
        
    def receivce_data(self):
        """ Recieves the data from the multiprocessing queue in background thread"""
        
        while True:
            i = 0
            while i < 3:
                queue_data = self.message_queue.get()
                self.local_queue.put(queue_data)
                i += 1
            time.sleep(self.receive_interval)

    def _start(self):
        self.start()
        time.sleep(0.1)
        self.recieving_function.start()
        logger.info("Recieving Thread Starting")
        
    def _stop(self):
        self.terminate()
    
    def run(self):
        while True:
            while self.local_queue.qsize() != 0:
                key = self.local_queue.get(block=True)
                # Process the keys we recieve
                self.make_change(key)
            interval = self.run_interval
            logger.debug(f"Processing ... {os.getpid()}")
            time.sleep(interval)