#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 13 20:35:35 2019

@author: erigara
"""

import math
import numpy as np
import db_module

class RTSLReqHandler:
    async def create(db):
        self = RTSLReqHandler()
        self.db = db
        return  self
    
    async def handle(self, data):
        security_id = data['userID']
        time = data['time']
        position = await self.find_position(data)
        check_points = await self.map_check_points(position)
        await self.save_check_points(security_id, time, check_points)
        return security_id, time, position
        
    async def find_position(self, signals):
        """
        Определение координат устройства по уровню сигналов в wifi и bt сетях, 
        совмещение их положений и постпроцессинг.
        signals : {
                    wifi : ([id_1, rssi_1], ...., [id_n, rssi_n]),
                    bluetooth : ([id_1, rssi_1], ...., [id_n, rssi_n])
                   }
        
        
        return position : (x : float, y : float) 
        """
        wifi_signals = signals["wifi"]
        bt_signals = signals["bluetooth"]
        wifi_coords = await self.get_coords(wifi_signals)
        bt_coords = await  self.get_coords(bt_signals)
        pos = await self.avg_coords(wifi_coords, bt_coords, wifi_signals, bt_signals)    
        pos = await self.postprocessing_coords(pos)
        return (pos[0,0], pos[1,0])
    
    
    
    async def get_coords(self, signals):
        """
        Определение координаты по набору устройств и их rssi.
        signals : ([id_1, rssi_1], ...., [id_n, rssi_n])
        
        return position : (x : float, y : float)
        """
        coords = []
        distances = []
        for sensor_id in signals:
            rssi = signals[sensor_id]
            x, y = await self.get_sensor_coords(sensor_id)
            benchmark_rssi = await self.get_benchmark_rssi(sensor_id)
            dist = await self.find_distance(rssi, benchmark_rssi)
            coords.append(np.array((x, y)).reshape(2,1))
            distances.append(dist)
        pos = await self.multilateration(coords, distances)
        return pos
    
    
    async def avg_coords(self, wifi_position, bt_position, wifi_signals, bt_signals):
        """
        Совмещение позиций полученных по wifi и по bluetooth.
        wifi_position : np.array(x :float, y : float) - положение определненное по wifi сети.
        bt_position : np.array(x :float, y : float) - положение определненное по bluetooth сети.
        # TODO посмотреть методы совмещения.
        return - coords : np.array(x : float, y : float)
        """
        # Параметр определяющий насколько суммарная сила одного сигала больше чем у другого.
        avg_wifi_rssi = np.mean([wifi_signals[signal_id] for signal_id in wifi_signals])
        avg_bt_rssi = np.mean([bt_signals[signal_id] for signal_id in bt_signals])
        alpha = avg_wifi_rssi/(avg_wifi_rssi + avg_bt_rssi)
        betha = avg_bt_rssi/(avg_wifi_rssi + avg_bt_rssi)
        coords = alpha*wifi_position + betha*bt_position
        return coords
    
    async def postprocessing_coords(self, pos):
        """
        Постобработка координат для увелечения точности.
        # TODO определить возможные методы построцессинга.
        Фильтр Кармана?
        pos : (x: float, y : float) - положение до постпроцессинга.
        
        return coords : np.array(x : float, y : float)
        """
        return pos
    
    async def get_sensor_coords(self, sensor_id):
        """
        Запрос координат устройства из базы по данному id.
        
        return coords : (x : float, y : float)
        """
        """
        result = await self.db.read_record_by_id(table="Sensor",
                             columns=["x", "y"],
                             id_column="sensor_id",
                             id_='"'+sensor_id+'"')
        """
        condition = "{} = {}"
        result = await (db_module.ReadRecord(self.db)
                                        .add_where(condition)
                                        .execute(table="Sensor", 
                                                 columns=["x", "y"],
                                                 data=["sensor_id", 
                                                 '"{}"'.format(sensor_id)]))
        if result:
            sensor_coords = result[0]
            x = float(sensor_coords["x"])
            y = float(sensor_coords["y"])
        else:
             raise UserWarning((0, "Sensor not found"))
        return x, y
    
    async def get_benchmark_rssi(self, sensor_id):
        """
        Запрос эталонного rssi из базы по данному id.
        
        return benchmark_rssi : int
        """
        """
        result = await self.db.read_record_by_id(table="Sensor",
                             columns=["benchmark_rssi"],
                             id_column="sensor_id",
                             id_='"'+sensor_id+'"')
        """
        condition = "{} = {}"
        result = await (db_module.ReadRecord(self.db)
                                        .add_where(condition)
                                        .execute(table="Sensor", 
                                                 columns=["benchmark_rssi",],
                                                 data=["sensor_id", 
                                                       '"{}"'.format(sensor_id)]))
        if result:
            benchmark_rssi = result[0]["benchmark_rssi"]
        else: 
            raise UserWarning((0, "Sensor not found"))
        return benchmark_rssi
    
    async def find_distance(self, rssi, benchmark_rssi):
        """
        Находит расстояние от устройства до датчика на основе формулы передачи Фрииса.
        rssi : int  - уровень сингала
        benchmark_rssi : int - эталонный уровень сигнала
        
        return dist : float
        """
        n = 2
        benchmark_dist = 1
        delta_rssi = rssi - benchmark_rssi
        dist = 10**(-delta_rssi/(10*n) + math.log10(benchmark_dist))
        return dist
    
    async def  multilateration(self, coords, distances):
        """
        Нахождение положение точки в заданной системе координат на основе опорных точнек и расстояний до них.
        сondition : dict - словарь содержащий (x : float, y : float, dist : float) каждой опроной точки.
        
        return coords : (x : float, y : float)
        """
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
        
    async def map_check_points(self, position):
        """
        Назхождение чекпоинтов, в которые попадает точка.
        position : (x: float, y: float)
        return [{"check_point_id": id}, ....]
        """
        condition = "POWER(x-{},2) + POWER(y-{},2) <= POWER(radius, 2)"
        """
        check_points = await self.db.read_record_by_condition("CheckPoint", 
                                                        ["check_point_id",],
                                                        condition = condition,
                                                        data = position)
        """
        check_points = await (db_module.ReadRecord(self.db)
                                        .add_where(condition)
                                        .execute(table="CheckPoint", 
                                                 columns=["check_point_id",],
                                                 data=position))
        return check_points
    
    async def save_check_points(self, security_id, time, check_points):
        """
        Занести в историю перемещений данные о истории перемещений.
        security_id : int
        time : str
        check_points : [check_point_id, ...]
        """
        for check_point in check_points:
            await self.db.insert_record("MovmentHistory", 
                                        ["security_id", "check_point_id", "time_stamp"], 
                                        [security_id, check_point["check_point_id"], '"'+time+'"'])