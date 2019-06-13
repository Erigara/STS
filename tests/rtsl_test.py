#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 14 19:12:45 2019

@author: erigara
"""
import matplotlib.pyplot as plt
import asyncio
import numpy as np
import random
from server.handlers.rtsl_handler import RTSLReqHandler

def create_plot():
    plt.ion()
    fig, ax = plt.subplots()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    fig.show()
    return fig, ax

def update_plot(x,y):
    plt.scatter(x,y)    
    plt.draw()
    plt.pause(.001)
    
def find_dist(x,y, x_, y_):
    return ((x-x_)**2+(y-y_)**2)**0.5

async def run():
    alpha = 0.2
    req =  await (RTSLReqHandler.create(None))
    fig, ax = create_plot()
    
    point = list(map(float, input().split(" ")))
    
    
    coords = [np.array((0, 0)).reshape(2,1),
              np.array((10, 0)).reshape(2,1),
              np.array((0, 5)).reshape(2,1)]
    
    dist = [find_dist(point[0], point[1], coord[0,0], coord[1,0]) for coord in coords]
    for coord, rad in zip(coords, dist):
        circle = plt.Circle(coord.flatten(), rad, color='r', fill=False)
        ax.add_artist(circle)
    true_result = await req.multilateration(coords, dist)
    true_result = true_result.flatten()
    update_plot(true_result[0], true_result[1])
   
    results = []
    for i in range(1000):
        err_dist = [rad*random.normalvariate(1, alpha) for rad in dist]
        result = await req.multilateration(coords, err_dist)
        result = result.flatten()
        results.append(result)
        update_plot(result[0], result[1])
    
    results = np.array(results)
    test_mean = np.mean(results, axis=0)
    print(test_mean)
    
    while True:
        plt.pause(.001)
    
asyncio.run(run())