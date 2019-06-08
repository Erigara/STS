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
                "5e:cf:7f:f2:65:4e" : (0,4), "5e:cf:7f:f2:66:25" : (0,0), "5e:cf:7f:f2:6c:bf" : (3,0),
                "98:D3:32:11:32:1A" : (0, 4), "98:D3:32:11:32:3D" : (3,0), "98:D3:32:31:2B:90" : (0, 0)
            }
    x_, y_ = sensor_coords[id_]
    return ((x-x_)**2+(y-y_)**2)**0.5


def dist_to_rssi(dist, benchmark_rssi):
    return benchmark_rssi - 20*math.log10(dist)

url = 'http://0.0.0.0:9000/rtsl'    


X = np.linspace(0.01, 3, 100)
Y = -0.2*X*(X-10)

for (x,y) in zip(X, Y):
    
    data = {"header" : "locate_security",
            "data"  : {
                        "userID"    : 1, 
                        "time"      : str(datetime.now()), 
                        "signals"   : {
                                        "wifi"      : {"5e:cf:7f:f2:65:4e" : dist_to_rssi(find_dist(x,y, "5e:cf:7f:f2:65:4e"), -40)+random.randint(0,1), 
                                                       "5e:cf:7f:f2:66:25" : dist_to_rssi(find_dist(x,y, "5e:cf:7f:f2:66:25"), -40)+random.randint(0,1), 
                                                       "5e:cf:7f:f2:6c:bf" : dist_to_rssi(find_dist(x,y,"5e:cf:7f:f2:6c:bf"), -40)+random.randint(0,1)}, 
                                        "bluetooth" : {"98:D3:32:11:32:1A" : dist_to_rssi(find_dist(x,y, "98:D3:32:11:32:1A"), -60)+random.randint(0,1), 
                                                       "98:D3:32:11:32:3D": dist_to_rssi(find_dist(x,y, "98:D3:32:11:32:3D"), -60)+random.randint(0,1), 
                                                       "98:D3:32:31:2B:90" : dist_to_rssi(find_dist(x,y, "98:D3:32:31:2B:90"), -60)+random.randint(0,1)}
                                        }
                        }
            }
    res = requests.post(url, json=data)
    
    