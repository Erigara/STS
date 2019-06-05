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
    """
    Класс для составляения SELECT запроса в базу данных.
    """
    def __init__(self, db):
            self.req = "SELECT {} FROM {}"
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
            req = self.req.format(" , ".join(columns), table, *data)
            async with self.db.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(req)
                    answer = await cur.fetchall()
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
    
    
    async def insert_record(self, table, row):
        """
        table : str - имя таблицы
        row : {'column_name' : value, ...}
        """
        columns = [key for key in row if (row[key] != "None" or row[key] != "")]
        values =  ['{!r}'.format(row[key]).replace("'", '"') for key in row if (row[key] != "None" or row[key] != "")]
        if columns:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    req = """
                          INSERT INTO {} ({})
                          VALUES({})
                          """.format(table, " , ".join(columns), 
                          " , ".join(values))
                    
                    await cur.execute(req)
                    await conn.commit()
                    print(await cur.fetchall())
                
    async def delete_record(self, table, row):
        """
        Удалить одну запись.
        table : str - имя таблицы
        row : {'column_name' : value, ...}
        """
        async with self.pool.acquire() as conn:
            eq = "{} = {!r}"
            condition = " AND ".join([eq.format(key, row[key]).replace("'", '"')  for key in row if (row[key] != "None" and row[key] != "")])
            if condition:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    req = """
                          Delete from {} where {}
                          """.format(table, condition)
                    await cur.execute(req)
                    await conn.commit()
                
    async def delete_records(self, table, rows):
        """
        Удалить много записей.
        table : str - имя таблицы
        rows : [{'column_name' : value, ...}, ...]
        """
        async with self.pool.acquire() as conn:
            eq = "{} = {!r}"
            condition = []
            for row in rows:
                record_condition = "({})".format(" AND ".join([eq.format(key, row[key]).replace("'", '"')  for key in row if (row[key] != "None" and row[key] != "")]))
                if record_condition != "()": 
                    condition.append(record_condition)
            condition = " OR ".join(condition)
            if condition:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    req = """
                          Delete from {} where {}
                          """.format(table, condition)
                    await cur.execute(req)
                    await conn.commit()
                    print(await cur.fetchall())
                
    async def update_record(self, table, row):
        """
        Обновить запись в таблице.
        table : str - имя таблицы
        row : {'column_name' : value, ...}
        """
        async with self.pool.acquire() as conn:
            eq = "{} = {!r}"
            pkey = self.findPkey(row)
            condition =  "{} = {!r}".format(pkey, row[pkey]).replace("'", '"')
            updatedRow = " , ".join([eq.format(key, row[key]).replace("'", '"')  for key in row if (row[key] != "None" and row[key] != "")])
            async with conn.cursor(aiomysql.DictCursor) as cur:
                req = """
                      Update  table {} set {} where {}
                      """.format(table, updatedRow, condition)
                await cur.execute(req)
                await conn.commit()
                print(await cur.fetchall())
                
    
    def findPkey(self, row):
        for key in row:
            if "_id" in key:
                return key