#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 11 22:59:40 2019

@author: erigara
"""

import sched
import heapq
class scheduler(sched.scheduler):
    def run(self):
        """
        Adaptation of shed.scheduler to fit multithreading needs.
        """
        # localize variable access to minimize overhead
        # and to improve thread safety
        lock = self._lock
        q = self._queue
        delayfunc = self.delayfunc
        timefunc = self.timefunc
        pop = heapq.heappop
        while True:
            delay = True
            with lock:
                if q:
                    time, priority, action, argument, kwargs = q[0]
                    now = timefunc()
                    if time <= now:
                        delay = False
                        pop(q)
            if not delay:
                action(*argument, **kwargs)
            delayfunc(0) # Let other threads run