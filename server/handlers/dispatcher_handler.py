#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  4 14:42:22 2019

@author: erigara
"""
import server.database.db_module as db_module
import asyncio

class DispatcherReqHandler:
    async def create(db):
        self =  DispatcherReqHandler()
        self.db = db
        self.command = {"get_soonest_time"         : self.get_soonest_time,
                        "get_between_route_points" : self.get_between_route_points,
                        "get_route_points"         : self.get_route_points,
                        "get_movment_history"      : self.get_movment_history,
                        "raise_warning"            : self.raise_warning}
        self.listeners = []
        return  self
    
    async def add_listener(self, listener):
        # listener : func to call
        self.listeners.append(listener)
    async def remove_listener(self, listener):
        self.listeners.remove(listener)
    async def notify_all(self, data):
        for listener in self.listeners:
            await listener(data)
    async def raise_warning(self, security_id, route_id, time):
        print("Get warning at {}".format(time))
        await self.notify_all({'header' : 'raise_warning', 'data' : {"security_id" : security_id,
                               "route_id"    : route_id,
                               "time"        : time}})
            
    async def handle(self, req):
        header = req["header"]
        data = req["data"]
        return await self.command[header](**data)
    
    async def get_soonest_time(self, time):
        """
        Получение ближайшего к заданному времени времени начала route_point.
        time : str (YYYY-MM-DD HH:MM:SS)
        """
        where_condition = "TIME({}) < {}"
        soonest_time = await (db_module.ReadRecord(self.db)
                                        .add_where(where_condition)
                                        .execute(table="RoutePoint", 
                                                 columns=["MIN(begin_time) as soonest_time",],
                                                 data=['"{}"'.format(time),
                                                       "begin_time"]))
        soonest_time = str(soonest_time[0]["soonest_time"])
        if soonest_time == 'None':
            soonest_time = "00:00:00"
        return {"soonest_time" : soonest_time}
        
      
    async def get_between_route_points(self, time):
        """
        Получение route_points у которых время начала и окончания 
        находятся между time.
        time : str (YYYY-MM-DD HH:MM:SS)
        return: dict {"route_points" : [{route_id : int,
                      security_id: int
                      begin_time: str (HH:MM:SS),
                      end_time: str (HH:MM:SS),
                      }, ...]}
        """
        where_condition = "TIME({}) BETWEEN {} AND {}"
        route_points = await (db_module.ReadRecord(self.db)
                                        .add_where(where_condition)
                                        .execute(table="RoutePoint", 
                                                 columns=["*",],
                                                 data=['"{}"'.format(time),
                                                       "begin_time",
                                                       "end_time"]))
        where_condition = "{} = {}"
        for route_point in route_points:
            responsable_security = await (db_module.ReadRecord(self.db)
                                          .add_where(where_condition)
                                          .execute(table="Route", 
                                                 columns=["security_id",],
                                                 data=["route_id", 
                                                       route_point["route_id"]]))
    
            responsable_security = responsable_security[0]["security_id"]
            route_point["begin_time"] = str(route_point["begin_time"])
            route_point["end_time"] = str(route_point["end_time"])
            route_point["security_id"] = responsable_security        
        return {"route_points" : route_points}
    
    async def get_route_points(self, time):
        """
        Получение route_points у которых время начала совпадает с time.
        time : str (YYYY-MM-DD HH:MM:SS)
        return: dict {"route_points" : [{route_id : int,
                      security_id: int
                      begin_time: str (HH:MM:SS),
                      end_time: str (HH:MM:SS),
                      }, ...]}
        """
        where_condition = "TIME({}) = {}"
        route_points = await (db_module.ReadRecord(self.db)
                                        .add_where(where_condition)
                                        .execute(table="RoutePoint", 
                                                 columns=["*",],
                                                 data=['"{}"'.format(time),
                                                       "begin_time"]))
        where_condition = "{} = {}"
        for route_point in route_points:
            responsable_security = await (db_module.ReadRecord(self.db)
                                          .add_where(where_condition)
                                          .execute(table="Route", 
                                                 columns=["security_id",],
                                                 data=["route_id", 
                                                       route_point["route_id"]]))
    
            responsable_security = responsable_security[0]["security_id"]
            route_point["begin_time"] = str(route_point["begin_time"])
            route_point["end_time"] = str(route_point["end_time"])
            route_point["security_id"] = responsable_security        
        return {"route_points" : route_points}
    
    async def get_movment_history(self, security_id, begin_time, end_time):
        """
        Получение истории перемещения охранника по его security_id
        в заданном промежутке времени (begin_time, end_time).
        security_id : int
        begin_time, end_time : str (YYYY-MM-DD HH:MM:SS)
        return : dict {"points": [{"check_point_id" : int,
                                   "check_in_time" : str (YYYY-MM-DD HH:MM:SS)}]}
        """
        where_condition = "{} = {} AND {} BETWEEN {} AND {}"
        visited_check_points = await (db_module.ReadRecord(self.db)
                                        .add_where(where_condition)
                                        .execute(table="MovmentHistory", 
                                                 columns=["check_point_id", "check_in_time"],
                                                 data=["security_id", 
                                                        security_id,
                                                       "check_in_time",
                                                       '"{}"'.format(begin_time),
                                                       '"{}"'.format(end_time)]))
        for visited_check_point in visited_check_points:
            visited_check_point['check_in_time'] = str(visited_check_point['check_in_time'])
        return {"points" : visited_check_points}
