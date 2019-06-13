#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 18 18:52:59 2019

@author: erigara
"""
import numpy as np
import pickle
from scipy.optimize import least_squares


def find_distance_nn(rssi, benchmark_rssi, std_rssi):
    model = pickle.load(open('./model/nn_model', 'rb'))
    dist = model.predict(np.array([rssi, benchmark_rssi, std_rssi]).reshape(1, -1))[0]
    return dist

def find_distance_poly(rssi, benchmark_rssi):
        """
        Находит расстояние от устройства до датчика на основе формулы передачи Фрииса.
        rssi : int  - уровень сингала
        benchmark_rssi : int - эталонный уровень сигнала
        
        return dist : float
        """
        deg = 3
        coef = [-1.46303883e-04,  1.18935211e-04,  1.63136522e-01,  2.47115842e+00]
        dist = 0
        delta_rssi = rssi - benchmark_rssi  
        for i in range(deg+1):
            add = (-delta_rssi)**(deg-i)*coef[i]
            dist = dist + add
        return dist
    
def find_distance(rssi, benchmark_rssi):
        """
        Находит расстояние от устройства до датчика на основе формулы передачи Фрииса.
        rssi : int  - уровень сингала
        benchmark_rssi : int - эталонный уровень сигнала
        
        return dist : float
        """
        n = 2
        #n = 0.94
        benchmark_dist = 1
        delta_rssi = rssi - benchmark_rssi
        dist = benchmark_dist*10**(-delta_rssi/(10*n))
        return dist

def naive_trilateration(coords, distances):
        """
        Нахождение положение точки в заданной системе координат на основе опорных точнек и расстояний до них.
        coords: list [np.array([[x],[y]]), ...]
        distances list [d, ...]
        
        return coords : (x : float, y : float)
        """
        if len(coords) < 3:
            return None
        displacment = coords[0]
        for i in range(len(coords)):
            coords[i] = coords[i]  - displacment
        U = np.linalg.norm(coords[1])
        V = np.linalg.norm(coords[2])
        c, s = (coords[1]/U).flatten()
        R = np.array(((c,s), (-s, c)))
        for i in range(len(coords)):
            coords[i] = np.matmul(R, coords[i])
        x = (distances[0]**2 - distances[1]**2 + U**2) / (2 * U)
        y = (distances[0]**2 - distances[2]**2 + V**2 - 2*coords[2][0,0]*x) / (2 * coords[2][1,0])
        point_of_interest = np.array([[x,], [y,]])
        point_of_interest = np.linalg.solve(R, point_of_interest)
        point_of_interest = point_of_interest + displacment
        return point_of_interest
    


def nlls_trilateration(coords, distances, X=None):
    def optimizer(coords, distances):
        flat_dist = distances.flatten()
    
        def equations( guess ):
            residuals = np.sqrt(np.diag((coords-guess) @ (coords-guess).T)).flatten() - flat_dist
            return residuals
        return equations


    N = len(coords)
    distances = np.array(distances).reshape(N,1)
    coords = np.array([coord.flatten() for coord in coords])
    dim = coords.shape[1]
    shape = (dim, 1)
    if X:
        X = X.flatten()
    else:  
        X = np.mean(coords, axis=0)
    
    eq = optimizer(coords, distances)
    X = np.array(least_squares(eq, X, method='lm').x)
    X = X.reshape(shape)
    return X

def sm_trilateration(coords, distances, X=None):
    def optimizer(coords, distances):
        def equations( guess ):
            U = coords - guess
            D = np.diag(U @ U.T).reshape(distances.shape)
            D = np.sqrt(D).reshape(distances.shape)
            U = U / D
            F = (D - distances) * U
            F = np.sum(F, axis = 0)
            residuals = F
            return residuals
        return equations


    N = len(coords)
    distances = np.array(distances).reshape(N,1)
    coords = np.array([coord.flatten() for coord in coords])
    dim = coords.shape[1]
    shape = (dim, 1)
    if X:
        X = X.flatten()
    else:  
        X = np.mean(coords, axis=0)
        
    eq = optimizer(coords, distances)
    X = np.array(least_squares(eq, X, method='lm').x)
    X = X.reshape(shape)
    return X
    

def ls_trilateration(coords, distances):
    
    N = len(coords)
    distances = np.array(distances).reshape(N,1)
    coords = np.array([coord.flatten() for coord in coords])
    dim = coords.shape[1]
    # Трансформация координат
    displacement =  coords[0, ...] 
    coords = coords - displacement
    U = np.linalg.norm(coords[N-1, ...])
    c, s = (coords[N-1,...]/U)
    R = np.array(((c,s), (-s, c)))
    coords = (R @ coords.T).T
    coords = coords/U
    distances = distances/U
    
    xn = coords[N-1, 0]
    yn = coords[N-1, 1]
    dn = distances[N-1,0]
    pn = np.array((xn, yn))
    
    A = 2*(coords - pn)[:N-1, :]
    b = coords[:N-1, 0]**2 + coords[:N-1, 1]**2 - distances[:N-1, 0]**2 -xn**2 -yn**2 **2 + dn**2
    ATb = (A.T @ b).reshape(dim, 1)
    
    try:
        X = np.linalg.solve(A.T @ A, ATb)
        # Обратное преобразование координат
        X = U*X
        X = np.linalg.solve(R, X)
        X = X + displacement.reshape(dim, 1)
    except np.linalg.linalg.LinAlgError:
        return None
    return X
