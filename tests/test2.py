#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  4 18:32:04 2019

@author: erigara
"""


import requests
from datetime import datetime
import json
import math

url = 'http://0.0.0.0:9000/'    

req_data = {"header" : "get_movment_history", 
                "data" : {"security_id" : 0,
                          "begin_time"  : "2019-05-09 20:30:00",
                          "end_time"    : "2019-05-09 21:30:00"
                          }
                }
res = requests.post(url, json=req_data)
print(res.status_code)
print(res.text)
print(res.json())