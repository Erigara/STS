#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 18 18:52:59 2019

@author: erigara
"""
import numpy as np
from scipy.optimize import least_squares

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
    


def optimizer(coords, distances):
    flat_dist = distances.flatten()
    
    def equations( guess ):
            x, y = guess
            residuals = np.diag((coords-guess) @ (coords-guess).T).flatten() - flat_dist 
            return residuals
    return equations

def nonlinear_ls_optimization(X, coords, distances):
    original_shape = X.shape
    X = X.flatten()
    eq = optimizer(coords, distances)
    X = np.array(least_squares(eq, X, method='lm').x)
    X = X.reshape(original_shape)
    return X

def spring_mass_optimization(X, coords, distances, eps=1, rate=1):
    original_shape = X.shape
    X = X.flatten()
    X_prev = np.zeros_like(X)
    
    diff = np.linalg.norm(X_prev - X)
    while diff > eps:
        U = coords - X
        D = np.diag(U @ U.T).reshape(distances.shape)
        D = np.sqrt(D).reshape(distances.shape)
        U = U / D
        F = (distances - D) * U
        F = np.sum(F, axis = 0)
        X_prev = X
        X = X - rate*F
        rate *= 0.99
        diff = np.linalg.norm(X_prev - X)
    if np.nan in X:
        return None
    else:
        X = X.reshape(original_shape)
        return X
def no_optimization(X, coords, distances):
    return X

methods_ = {"sm" : spring_mass_optimization, "nlls": nonlinear_ls_optimization, None : no_optimization}

def ls_trilateration(coords, distances, method=None, **kwargs):
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
        #Оптимизация результата
        
        # Обернуть в функцию постпроцессинга
        #######################################################################
        X = methods_[method](X, coords, distances, **kwargs)
        #######################################################################
        # Обратное преобразование координат
        X = U*X
        X = np.linalg.solve(R, X)
        X = X + displacement.reshape(dim, 1)
    except np.linalg.linalg.LinAlgError:
        return None
    return X
