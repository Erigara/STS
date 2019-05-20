#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 14:05:32 2019

@author: erigara
"""
from dispatcher import run

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("Bye!")