#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 01:50:02 2019

@author: erigara
"""

from aiohttp import web
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt


def create_hist(device, data, std, mean, median):
    fig, ax = plt.subplots()
    ax.hist(data)
    ax.set_title("device '{} rssi at 1m'".format(device))
    plt.axvline(x=mean, color='r')
    plt.axvline(x=median, color='c')
    plt.axvline(x=mean+std, color='k')
    plt.axvline(x=mean-std, color='k')
    fig.savefig('../STS_notes/rssi_distribution/{}.png'.format(device))   # save the figure to file
    plt.close(fig) 

class Server:
    def __init__(self):
        self.rssi_bt = {}
        self.rssi_wf = {}
    
    
    async def rtsl_handler(self, request):
        req = await request.json()
        print("get request at '{}'".format(datetime.now()))
        bt = req['data']['signals']['bluetooth']
        for bt_name in bt:
            if not bt_name in self.rssi_bt:
                self.rssi_bt[bt_name] = []
            self.rssi_bt[bt_name].append(bt[bt_name])
            print("bt {} : {}".format(bt_name, self.rssi_bt[bt_name][-1]))
        wf = req['data']['signals']['wifi']
        for wf_name in wf:
            if not wf_name in self.rssi_wf:
                self.rssi_wf[wf_name] = []
            self.rssi_wf[wf_name].append(wf[wf_name])
            print("wf {} : {}".format(wf_name, self.rssi_wf[wf_name][-1]))
        return web.Response()
    
def main():
    server = Server()
    async def init():
        app = web.Application()
        app.add_routes([web.post('/rtsl', server.rtsl_handler)])
        return app
    
    web.run_app(init(), path="127.0.0.1", port=9000)
    for bt in server.rssi_bt:
        median_bt_rssi = np.median(np.array(server.rssi_bt[bt]))
        mean_bt_rssi= np.mean(np.array(server.rssi_bt[bt]))
        std_bt_rssi = np.std(np.array(server.rssi_bt[bt]))
        dev_bt_rssi = np.sqrt(np.mean((np.abs(np.array(server.rssi_bt[bt])- mean_bt_rssi) - std_bt_rssi)**2))
        print("-----------------------------------------------------------")
        print("device {} have median {} bt rssi".format(bt, median_bt_rssi))
        print("device {} have mean {} bt rssi".format(bt, mean_bt_rssi))
        print("device {} have std {} bt rssi".format(bt, std_bt_rssi))
        print("device {} have dev {} bt rssi".format(bt, dev_bt_rssi))
        print("-----------------------------------------------------------")
        create_hist(bt, server.rssi_bt[bt], std_bt_rssi, mean_bt_rssi, median_bt_rssi)
        np.save(bt, server.rssi_bt[bt])
    for wf in server.rssi_wf:
        median_wf_rssi = np.median(np.array(server.rssi_wf[wf]))
        mean_wf_rssi= np.mean(np.array(server.rssi_wf[wf]))
        std_wf_rssi= np.std(np.array(server.rssi_wf[wf]))
        dev_wf_rssi = np.sqrt(np.mean((np.abs(np.array(server.rssi_wf[wf])- mean_wf_rssi) - std_wf_rssi)**2))
        print("-----------------------------------------------------------")
        print("device {} have median {} wf rssi".format(wf, median_wf_rssi))
        print("device {} have mean {} bt rssi".format(wf, mean_wf_rssi))
        print("device {} have std {} bt rssi".format(wf, std_wf_rssi))
        print("device {} have def {} bt rssi".format(wf, dev_wf_rssi))
        print("-----------------------------------------------------------")
        create_hist(wf, server.rssi_wf[wf], std_wf_rssi, mean_wf_rssi, median_wf_rssi)
        np.save(wf, server.rssi_wf[wf])
if __name__ == "__main__":
    main()