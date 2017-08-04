#!/usr/bin/python
#
# Copyright (c) 2017, Xgrid Inc, http://xgrid.co
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import threading
import Queue

log = logging.getLogger('test' + '.' + __name__)
# Stores result from each thread in a queue
# user needs to call return_queue.get() to retrieve each value
return_queue = Queue.Queue()
# Variable used to synchronize multiple threads
thread_lock = threading.RLock()
# Holds all running threads
thread_queue = Queue.Queue()


class MyThread(threading.Thread):
    """
    Class used to define a thread
    """
    def __init__(self, target=None, args=(), kwargs={}, lock=False):
        """
        Class constructor, called every time a new thread is created
        args:
        target: function that is called in thread
        args: a tuple of arguments for target function
        kwargs: extra arguments for target function
        lock: default is False, true if target function cannot run in parallel
        """
        threading.Thread.__init__(self)
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.lock = lock

    def run(self):
        """
        Thread execution function, called after start() from base class
        """
        # Lock current thread, make other threads wait for unlock
        if self.lock:
            thread_lock.acquire()
        # Check if target is defined
        if self.target is not None:
            try:
                # Run target function and enqueue return value, throw exception if no return value
                return_queue.put(self.target(*self.args, **self.kwargs))
            except ValueError:
                log.info("thread function '%s' did not return a value" % str(self.target))
        # Unlock current thread
        if self.lock:
            thread_lock.release()


def start_thread(target=None, args=(), kwargs={}, lock=False):
    """
    This function creates a new thread class object, starts it and enqueues it in thread_queue
    args:
    target: function that is called in thread
    args: a tuple of arguments for target function
    kwargs: keyword arguments for target function
    lock: default is False, true if target function cannot run in parallel
    """
    thread = MyThread(target=target, args=args, kwargs=kwargs, lock=lock)
    thread.start()
    thread_queue.put(thread)


def join_all():
    """
    This function waits for all threads in the thread_queue to either finish or abort
    """
    while thread_queue.empty() is False:
        thread_queue.get().join()
