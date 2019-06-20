#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 19:59:43 2019

@author: erigara
"""

import server.database.db_module as db_module
import json
import aiohttp

class WebReqHandler:
    async def create(db, socket):
        self = WebReqHandler()
        self.db = db
        self.socket = socket
        self.post_event = socket.send_json
        self.get_event  = socket.receive_json
        self.command = {"get_size" : self.get_size,
                        "register" : self.register,
                        "handshake": self.handshake,
                        "login"    : self.login,
                        "logout"   : self.logout,
                        "get_data" : self.get_data,
                        "get_column" : self.get_column,
                        "delete_data" : self.delete_data,
                        "modify_data" : self.modify_data,
                        "add_data" : self.add_data
                        }
        return  self
    async def raise_warning(self, data):
        print("Get event")
        await self.post_event(data)
    async def push_position(self, data):
        print("Get event")
        await self.post_event({"header" : "push_position",
                               "data"   : data})
    async def serve(self):
        async for msg in self.socket:
            if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close':
                       await self.socket.close()
                       break
                    else:
                       response = await self.handle(json.loads(msg.data))
                       if response:
                           await self.socket.send_json(response)
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                print("Closed")
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print("Error")
                break

    async def handle(self, req):
        header = req["header"]
        data = req["data"]
        print(req)
        return await self.command[header](**data)

    async def get_size(self):
        return {"header" : "get_size", "data" : {"width": 3, "height" : 5}}


    async def register(self, login, password, admin=False):
        success = True
        try:
            await self.db.insert_record("User", {"login" : login, "password" : password, "admin" : admin})
        except:
            success = False

        return {"header" : "register", "data" : {"success" : success}}


    async def login(self, login, password):
        """
        Функция авторизации пользователя

        return: bool, cookie_id
        """
        success = False
        cookie = ""
        condition = "{} = {}"
        result = await (db_module.ReadRecord(self.db)
                                        .add_where(condition)
                                        .execute(table="User",
                                                 columns=["password", "admin"],
                                                 data=["login",
                                                 '"{}"'.format(login)]))
        if result:
            password_ = result[0]['password']
            admin_ = result[0]['admin']
            if password == password_:
                success = True
                cookie = self.get_status(admin_)
        return {"header" : "login", "data" : {"success" : success, "status" : cookie}}

    async def logout(self, login, password):
        cookie = ""
        return {"header" : "logout", "data" : {"status" : cookie}}

    def get_status(self, admin):
        if admin:
            return 'admin'
        else:
            return 'user'

    async def handshake(self):
        print("Web client say hello!")

    async def get_data(self, table):
        tabledata = await (db_module.ReadRecord(self.db)
                                        .execute(table=table,
                                                 columns=["*",],
                                                 data=[]
                                                 )
                           )
        tabledata = [{key : str(row[key]) for key in row} for row in tabledata]
        where_condition = "table_name = {}"
        columns = await (db_module.ReadRecord(self.db)
                                        .add_where(where_condition)
                                        .execute(table="INFORMATION_SCHEMA.COLUMNS ",
                                                 columns=["COLUMN_NAME", "COLUMN_COMMENT",],
                                                 data=['"{}"'.format(table)]
                                                 )
                           )
        columns = [{'title' : column["COLUMN_COMMENT"], 'field' : column["COLUMN_NAME"]} for column in columns]
        return {"header" : "get_data", "data" : {'columns' : columns, 'tabledata' : tabledata}}

    async def modify_data(self, table, row):
        await self.db.update_record(table, row)
        return {"header" : "modify_data", "data" : {'success': True}}

    async def add_data(self, table, row):
        await self.db.insert_record(table, row)
        where_condition = " AND ".join(['{} = {!r}'.format(key, row[key]).replace("'", '"') for key in row if row[key] != '' and row[key] != 'None'])
        nrow = await (db_module.ReadRecord(self.db)
                                        .add_where(where_condition)
                                        .execute(table=table,
                                                 columns=["*",],
                                                 data=[]
                                                 )
                                        )
        if nrow:
            nrow = {key : str(nrow[-1][key]) for key in nrow[-1]}
            return {"header" : "add_data", "data" : {'success': True, 'row': nrow}}
        else:
            return {"header" : "add_data", "data" : {'success': False, 'row': {}}}

    async def get_column(self, table, column):
        tabledata = await (db_module.ReadRecord(self.db)
                                        .execute(table=table,
                                                 columns=[column,],
                                                 data=[]
                                                 )
                           )
        tabledata = [{key : str(row[key]) for key in row} for row in tabledata]
        print(tabledata)
        return {"header" : "get_column", "data" : {'column' : tabledata}}

    async def delete_data(self, table, rows):
        await self.db.delete_records(table, rows)
        return {"header" : "delete_data", "data" : {"success" : True}}
