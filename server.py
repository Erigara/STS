#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 16:22:26 2019

@author: erigara
"""

from aiohttp import web
import asyncio 
import db_module
import rtsl

routes = web.RouteTableDef()

class Server:
    pass

@routes.get('/')
async def user_handler(request):
    # Визульное отображение имеющихся на сервере данных
    # Уведомления об отклонении от маршрута и тд.
    return web.Response()

@routes.post('/rtsl')
async def rtsl_handler(request):
    data = await request.json()
    try:
        security_id, time, position = await server.rtsl_.handle(data)
        print("Security : {} at {} on ({}, {})".format(security_id, time, *position))
    except Exception as exp:
        print(exp)
    return web.Response()
    
    

@routes.get('/dispatcher')
async def dispatcher_handler(request):
    # Discription : длительное соединение открытое с помощью веб сокета. 
    # dispatcher выполняет запросы к базе на выгрузку ближайших чекпоинтов
    # dispatcher запрашивает самые новые данные по истории перемещенний и проверяет выполнился ли чекпоинт.
    return web.Response()


server = Server()
async def init():
    server.db = await db_module.STSDataBase.create()
    server.rtsl_ = await rtsl.RTSLReqHandler.create(server.db)
    app = web.Application()
    app.add_routes(routes)
    return app
web.run_app(init(), path="127.0.0.1", port=9000)