#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  3 15:54:07 2019

@author: erigara
"""

import requests
from datetime import datetime
import numpy as np
import math
import random
from time import sleep

def find_dist(x,y, id_):
    sensor_coords = {
                "1:1" : (0,0), "1:2" : (10,0), "1:3" : (0,5),
                "2:1" : (10, 5), "2:2" : (10,0), "2:3" : (0, 5)
            }
    x_, y_ = sensor_coords[id_]
    return ((x-x_)**2+(y-y_)**2)**0.5


def dist_to_rssi(dist, benchmark_rssi):
    return benchmark_rssi - 20*math.log10(dist)

url = 'http://0.0.0.0:9000/rtsl'    


X = np.linspace(0.01, 9.99, 100)
Y = -0.2*X*(X-10)

for (x,y) in zip(X, Y):
    
    data = {"header" : "locate_security",
            "data"  : {
                        "userID"    : 1, 
                        "time"      : str(datetime.now()), 
                        "signals"   : {
                                        "wifi"      : {"1:1" : dist_to_rssi(find_dist(x,y, "1:1"), -40)+random.randint(0,1), 
                                                       "1:2" : dist_to_rssi(find_dist(x,y, "1:2"), -40)+random.randint(0,1), 
                                                       "1:3" : dist_to_rssi(find_dist(x,y,"1:3"), -40)+random.randint(0,1)}, 
                                        "bluetooth" : {"2:1" : dist_to_rssi(find_dist(x,y, "2:1"), -60)+random.randint(0,1), 
                                                       "2:2" : dist_to_rssi(find_dist(x,y, "2:2"), -60)+random.randint(0,1), 
                                                       "2:3" : dist_to_rssi(find_dist(x,y, "2:3"), -60)+random.randint(0,1)}
                                        }
                        }
            }
    res = requests.post(url, json=data)
    
    