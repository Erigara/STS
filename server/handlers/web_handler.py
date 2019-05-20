#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 19:59:43 2019

@author: erigara
"""
class WebReqHandler:
    async def create(db, post_event, get_event):
        self = WebReqHandler()
        self.db = db
        self.post_event = post_event
        self.get_event  = get_event
        return  self
    async def raise_warning(self, data):
        print("Get event")
        await self.post_event({"header" : "raise_warning",
                               "data"   : data})
    async def push_position(self, data):
        print("Get event")
        await self.post_event({"header" : "push_position",
                               "data"   : data})
