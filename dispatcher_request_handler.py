#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  4 14:42:22 2019

@author: erigara
"""

class DispatcherReqHandler:
    async def create(db):
        self =  DispatcherReqHandler()
        self.db = db
        return  self
    async def handle(self, req):
        header = req["header"]
        data = req["data"]
        await self.command[header](**data)
    async def get_soonest_route_point(current_time):
        pass