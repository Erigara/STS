#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 20:34:11 2019

@author: erigara
"""

import aiohttp
import asyncio
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_plot():
    plt.ion()
    fig, ax = plt.subplots()
    p = patches.Rectangle(
            (0, 0), 3, 5,
            fill=False
    )
    ax.add_artist(p)
    ax.set_xlim(-1, 4)
    ax.set_ylim(-1, 6)
    plt.draw()
    fig.show()
    return fig, ax

def update_plot(x,y, time):
    plt.scatter(x,y)    
    plt.draw()
    plt.pause(.001)
    
class Web:
    def __init__(self):
        self.ws_ = None
    async def close(self):
        if self.ws_:
            await self.ws_.close()   
         
    async def run(self):
        update_plot([],[], "")
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect('http://0.0.0.0:9000/event') as ws:
                self.ws = ws
                while True:
                    update_plot([],[], "")
                    msg = await ws.receive()
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        if msg.data == 'close':
                           await ws.close()
                           break
                        else:
                           data = json.loads(msg.data)
                           if data['header'] == 'push_position':
                               data = data['data']
                               x = [data['position'][0],]
                               y = [data['position'][1],]
                               update_plot(x,y, data['time'])
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        print("Closed")
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break
    

try:
    web = Web()
    create_plot()
    asyncio.run(web.run())
except KeyboardInterrupt:
    print('KeyboardInterrupt')
finally:
    asyncio.run(web.close())