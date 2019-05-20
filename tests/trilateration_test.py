#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 18 20:49:02 2019

@author: erigara
"""
from time import sleep
import matplotlib.pyplot as plt
import trilateration
import math
import numpy as np
import random
import itertools
from scipy.optimize import least_squares

def find_dist(x,y, x_, y_):
    return ((x-x_)**2+(y-y_)**2)**0.5


def dist_to_rssi(dist, benchmark_rssi):
    return benchmark_rssi - 20*math.log10(dist)
   
def rssi_to_dist(rssi, benchmark_rssi):
    n = 2
    benchmark_dist = 1
    delta_rssi = rssi - benchmark_rssi
    dist = benchmark_dist*10**(-delta_rssi/(10*n))
    return dist

#X = np.linspace(1, 8, 100)
#Y = abs(5*np.sin(X))
x = random.randint(0,3)
y = random.randint(0,5)
X = [x for i in range(100)]
Y = [y for i in range(100)]
coords = [np.array([[x,],[y,]]) for x,y in ((0,0), (3,0), (0,5), (3,5))]

#random.seed(0)
for subset in itertools.combinations(coords, 4):
    LS_RES = []
    OPT_RES = []
    SM_RES = []
    for (x,y) in zip(X, Y):         
        dist =[find_dist(x,y, coord[0,0], coord[1,0]) for coord in subset]
        rssi = [dist_to_rssi(d, -40)*random.normalvariate(1, 0.3**2) for d in dist]
        noisy_dist = [rssi_to_dist(r, -40) for r in rssi]
        
        ls_res = trilateration.ls_trilateration(subset, noisy_dist).flatten()
        opt_res = trilateration.ls_trilateration(subset, noisy_dist, method="nlls").flatten()
        sm_res = trilateration.ls_trilateration(subset, noisy_dist, method="sm", eps=0.01, rate=1).flatten()
        LS_RES.append(ls_res)
        OPT_RES.append(opt_res)
        SM_RES.append(sm_res)
        
    LS_RES = np.array(LS_RES)
    unx_mean, uny_mean =np.mean(LS_RES, axis =0)
    ls_std = np.sqrt(np.mean(np.linalg.norm(LS_RES - (x,y), axis=1)**2))
    #plt.scatter(LS_RES[:,0], LS_RES[:,1], color = 'b')
    
    circle = plt.Circle((x,y), ls_std, color='r', fill=False)
    plt.gca().add_artist(circle)
    
    OPT_RES = np.array(OPT_RES)
    x_mean, y_mean =np.mean(OPT_RES, axis =0)
    opt_std = np.sqrt(np.mean(np.linalg.norm(OPT_RES - (x,y), axis=1)**2))
    plt.scatter(OPT_RES[:,0], OPT_RES[:,1], color = 'g')
    
    circle = plt.Circle((x,y), opt_std, color='r', fill=False)
    plt.gca().add_artist(circle)
    
    
    SM_RES = np.array(SM_RES)
    smx_mean, smy_mean =np.mean(SM_RES, axis =0)
    sm_std = np.sqrt(np.mean(np.linalg.norm(SM_RES - (x,y), axis=1)**2))
    plt.scatter(SM_RES[:,0], SM_RES[:,1], color='k')
    
    circle = plt.Circle((x,y), sm_std, color='r', fill=False)
    plt.gca().add_artist(circle)
    
    plt.scatter([x,],[y,], color='r')
    
    plt.scatter(x_mean, y_mean)
    plt.show()
    
    print("------------------------------------------------------------------")
    print("for point ({},{}) computed unoptimized mean is ({},{}) with std {}".format(x,y,unx_mean, uny_mean, ls_std))
    print("for point ({},{}) computed nlls optimized mean is ({},{}) with std {}: ".format(x,y,x_mean, y_mean, opt_std))
    print("for point ({},{}) computed ms optimized mean is ({},{}) with std {}".format(x,y,smx_mean, smy_mean, sm_std))
    print("------------------------------------------------------------------")
