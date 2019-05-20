#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 16:22:26 2019

@author: erigara
"""

from aiohttp import web
import aiohttp
import asyncio 
from database import db_module
from handlers import web_handler, rtsl_handler, dispatcher_handler
from datetime import datetime
routes = web.RouteTableDef()
class Server:
    async def create():
        self = Server()
        self.db = await db_module.STSDataBase.create()
        self.rtsl_ = await rtsl_handler.RTSLReqHandler.create(self.db)
        self.dispatcher_ = await dispatcher_handler.DispatcherReqHandler.create(self.db)
        return self
    
    async def event_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        whandler = await web_handler.WebReqHandler.create(self.db, ws.send_json, ws.receive_json) 
        await self.dispatcher_.add_listener(whandler.raise_warning)
        await self.rtsl_.add_listener(whandler.push_position)
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close':
                       await ws.close()
                       break
                    else:
                       print(msg.data)
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                print("Closed")
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print("Error")
                break
        await self.dispatcher_.remove_listener(whandler.raise_warning)
        await self.rtsl_.remove_listener(whandler.push_position)
        return ws
    
    async def web_handler(self, request):
        # Визульное отображение имеющихся на сервере данных
        # Уведомления об отклонении от маршрута и тд.
        # Discription : длительное соединение открытое с помощью веб сокета. 
        return web.FileResponse("./ui/ui.html")
    
    async def rtsl_handler(self, request):
        req = await request.json()
        print("get request at '{}'".format(datetime.now()))
        print(req)
        security_id, time, position = await self.rtsl_.handle(req)
        return web.Response()
    
    async def dispatcher_handler(self,request):
        req = await request.json()
        res = await self.dispatcher_.handle(req)
        return web.json_response(res)

def main():
    async def init():
        server = await Server.create()
        app = web.Application()
        app.add_routes([web.get('/', server.web_handler),
                        web.get('/event', server.event_handler),
                        web.post('/rtsl', server.rtsl_handler),
                        web.post('/dispatcher', server.dispatcher_handler)])
        return app
    web.run_app(init(), path="127.0.0.1", port=9000)

if __name__ == "__main__":
    main()