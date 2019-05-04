#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 13:55:40 2019

@author: erigara
"""

import asyncio
import aiomysql
import pymysql

class ReadRecord:
        def __init__(self, db):
            self.req = " SELECT {} FROM {}"
            self.db = db
        def add_where(self, condition):
            self.req = "{} WHERE {}".format(self.req, condition)
            return self
        def add_order_by(self, condition):
            self.req = "{} ORDER BY {}".format(self.req, condition)
            return self
        def add_limit(self):
            self.req = "{} LIMIT {}".format(self.req, "{}")
            return self
        async def execute(self, table, columns, data):
            async with self.db.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(self.req.format(" , ".join(columns), table, *data)+";")
                    answer = []
                    while True:
                        row = await cur.fetchone()
                        if row is None:
                            break
                        answer.append(row)
            return answer

class STSDataBase:
    async def create():
        self = STSDataBase()
        self.pool = await aiomysql.create_pool(host='127.0.0.1', 
                                               port=3306,
                                               user='STS_USER', 
                                               password='STS_USER_password_00',
                                               db='STS_DB', 
                                               )
        return self
    
    async def close(self):
        self.pool.close()
        await self.pool.wait_closed()
    
    
    async def insert_record(self, table, columns, data):
        """
        table : str - имя таблицы
        сolumns : str - имена стобцов, в которые будут записаны новые значени.
        data : list - список новых строк на дополнение
        """
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                req = """
                      INSERT INTO {} ({})
                      VALUES({})
                      """.format(table, " , ".join(list(map(str,columns))), 
                      " , ".join(list(map(str, data))))
                
                await cur.execute(req)
                await conn.commit()