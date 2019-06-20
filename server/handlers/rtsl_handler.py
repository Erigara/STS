#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 13 20:35:35 2019

@author: erigara
"""

import numpy as np
import server.database.db_module as db_module
import trilateration

class RTSLReqHandler:
    async def create(db):
        self = RTSLReqHandler()
        self.db = db
        self.command = {"locate_security"         : self.locate_security}
        self.listeners = []
        return  self

    async def handle(self, req):
        header = req["header"]
        data = req["data"]
        return await self.command[header](**data)

    async def push_position(self, security_id, position, time):
        print("Security : {} at {} on ({}, {})".format(security_id, time, *position))
        await self.notify_all({"security_id" : security_id,
                               "position"    : position,
                               "time"        : time})

    async def add_listener(self, listener):
        # listener : func to call
        self.listeners.append(listener)
    async def remove_listener(self, listener):
        self.listeners.remove(listener)
    async def notify_all(self, data):
        for listener in self.listeners:
            await listener(data)

    async def locate_security(self, userID, time, signals):
        security_id = userID
        position = await self.find_position(signals)
        print(position)
        check_points = await self.map_check_points(position)
        await self.save_check_points(security_id, time, check_points)
        await self.push_position(security_id, position, time)
        return security_id, time, position


    async def find_position(self, signals):
        """
        Определение координат устройства по уровню сигналов в wifi и bt сетях,
        совмещение их положений и постпроцессинг.
        signals : {
                    wifi : ({id_1 : rssi_1}, ...., {id_n : rssi_n}),
                    bluetooth : ({id_1 : rssi_1}, ...., {id_n : rssi_n})
                   }


        return position : (x : float, y : float)
        """
        wifi_signals = signals["wifi"]
        bt_signals = signals["bluetooth"]
        wifi_coords = await self.get_coords(wifi_signals)
        if not wifi_coords is None:
            print('wifi coords {}'.format(tuple(wifi_coords.flatten())))
        bt_coords = await  self.get_coords(bt_signals)
        if not bt_coords is None:
            print('bt coords {}'.format(tuple(bt_coords.flatten())))
        pos = await self.avg_coords(wifi_coords, bt_coords, wifi_signals, bt_signals)
        pos = await self.postprocessing_coords(pos)
        return (pos[0,0], pos[1,0])



    async def get_coords(self, signals):
        """
        Определение координаты по набору устройств и их rssi.
        signals : ({id_1 : rssi_1}, ...., {id_n : rssi_n})

        return position : (x : float, y : float)
        """
        coords = []
        distances = []
        for sensor_id in signals:
            rssi = signals[sensor_id]
            x, y = await self.get_sensor_coords(sensor_id)
            benchmark_rssi = await self.get_benchmark_rssi(sensor_id)
            std_rssi = await self.get_benchmark_rssi_std(sensor_id)
            dist = trilateration.find_distance_nn(rssi, benchmark_rssi, std_rssi)
            print('{} position {} dist {} m'.format(sensor_id, (x,y),dist))
            coords.append(np.array((x, y)).reshape(2,1))
            distances.append(dist)
        pos = await self.multilateration(coords, distances)
        return pos


    async def avg_coords(self, wifi_coords, bt_coords, wifi_signals, bt_signals):
        """
        Совмещение позиций полученных по wifi и по bluetooth.
        wifi_coords : np.array(x :float, y : float) - положение определненное по wifi сети.
        bt_coords : np.array(x :float, y : float) - положение определненное по bluetooth сети.
        # TODO посмотреть методы совмещения.
        return - coords : np.array(x : float, y : float)
        """
        if wifi_coords is None and bt_coords is None:
            raise UserWarning((1, "Not Enougth Data to find location"))
        elif wifi_coords is None:
            coords = bt_coords
        elif bt_coords is None:
            coords = wifi_coords
        else:
            avg_wifi_rssi = np.mean([wifi_signals[signal_id] for signal_id in wifi_signals])
            avg_bt_rssi = np.mean([bt_signals[signal_id] for signal_id in bt_signals])
             # Параметр определяющий насколько суммарная сила одного сигала больше чем у другого.
            alpha = avg_wifi_rssi/(avg_wifi_rssi + avg_bt_rssi)
            betha = avg_bt_rssi/(avg_wifi_rssi + avg_bt_rssi)
            coords = betha*wifi_coords + alpha* bt_coords
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

    async def get_sensor_coords(self, mac_address):
        """
        Запрос координат устройства из базы по данному id.

        return coords : (x : float, y : float)
        """
        condition = "{} = {}"
        result = await (db_module.ReadRecord(self.db)
                                        .add_where(condition)
                                        .execute(table="Sensor",
                                                 columns=["x", "y"],
                                                 data=["mac_address",
                                                 '"{}"'.format(mac_address)]))
        if result:
            sensor_coords = result[0]
            x = float(sensor_coords["x"])
            y = float(sensor_coords["y"])
        else:
             raise UserWarning((0, "Sensor not found"))
        return x, y

    async def get_benchmark_rssi(self, mac_address):
        """
        Запрос эталонного rssi из базы по данному id.

        return benchmark_rssi : float
        """
        condition = "{} = {}"
        result = await (db_module.ReadRecord(self.db)
                                        .add_where(condition)
                                        .execute(table="Sensor",
                                                 columns=["benchmark_rssi",],
                                                 data=["mac_address",
                                                       '"{}"'.format(mac_address)]))
        if result:
            benchmark_rssi = result[0]["benchmark_rssi"]
        else:
            raise UserWarning((0, "Sensor not found"))
        return benchmark_rssi

    async def get_benchmark_rssi_std(self, mac_address):
        """
        Запрос эталонного rssi из базы по данному id.

        return benchmark_rssi_std : float
        """
        condition = "{} = {}"
        result = await (db_module.ReadRecord(self.db)
                                        .add_where(condition)
                                        .execute(table="Sensor",
                                                 columns=["benchmark_rssi_std",],
                                                 data=["mac_address",
                                                       '"{}"'.format(mac_address)]))
        if result:
            benchmark_rssi = result[0]["benchmark_rssi_std"]
        else:
            raise UserWarning((0, "Sensor not found"))
        return benchmark_rssi


    async def  multilateration(self, coords, distances):
        """
        Нахождение положение точки в заданной системе координат на основе опорных точнек и расстояний до них.
        сondition : dict - словарь содержащий (x : float, y : float, dist : float) каждой опроной точки.

        return coords : (x : float, y : float)
        """
        try:
            return trilateration.nlls_trilateration(coords, distances)
        except:
            return None

    async def map_check_points(self, position):
        """
        Нахождение чекпоинтов, в которые попадает точка.
        position : (x: float, y: float)
        return [{"check_point_id": id}, ....]
        """
        condition = "POWER(x-{},2) + POWER(y-{},2) <= POWER(radius, 2)"
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
        time : str 'YYYY-MM-DD HH:MM:SS(.MMM)'
        check_points : [check_point_id, ...]
        """
        for check_point in check_points:
            await self.db.insert_record("MovmentHistory",
                                        {"security_id" : security_id, "check_point_id" : check_point["check_point_id"], "check_in_time" : time}
                                        )
