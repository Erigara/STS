
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 16:22:26 2019

@author: erigara
"""

from aiohttp import web
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
        self.users = {'admin': 'admin'}
        return self
    
    async def web_handler(self, request):
        redirect_response = web.HTTPSeeOther('ui/index.html')
        return redirect_response
    
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
    
    async def event_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        whandler = await web_handler.WebReqHandler.create(self.db, ws) 
        await self.dispatcher_.add_listener(whandler.raise_warning)
        await self.rtsl_.add_listener(whandler.push_position)
        await whandler.serve()
        await self.dispatcher_.remove_listener(whandler.raise_warning)
        await self.rtsl_.remove_listener(whandler.push_position)
        return ws

def main():
    async def init():
        server = await Server.create()
        loop = asyncio.get_event_loop()
        app = web.Application(loop=loop)
        app.router.add_static('/ui/', path='ui/', name='ui')
        app.add_routes([web.get('/', server.web_handler),
                        web.get('/event', server.event_handler),
                        web.post('/rtsl', server.rtsl_handler),
                        web.post('/dispatcher', server.dispatcher_handler)])
        return app
    web.run_app(init(), port=9000)

if __name__ == "__main__":
    main()