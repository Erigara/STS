#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  9 18:32:17 2019

@author: erigara
"""

import sched_sts
import time
import datetime
import requests
import json
import threading

#%%% Вспомогательные функции
def create_datetime(t, day_shift=0):
    """
    Формирует datetime на основе текущей даты и указанного времени.
    t : str "HH:MM:SS" - время которое следует вставить в выбраннную дату.
    day_shift : int - число дней, на которое нужно сдвинуть текущую дату.
    """
    if t == "00:00:00":
        day_shift +=1
    t = list(map(int, t.split(":")))
    t = datetime.time(*t)
    
    d = datetime.date.today() + datetime.timedelta(days=day_shift)
    dt = datetime.datetime.combine(d, t)
    return dt

def create_req_data(header, data):
    req_data = {"header" : header,
                "data"   : data
            }
    return req_data

url = 'http://0.0.0.0:9000/dispatcher'
def send_post_req(header, **data):
    """
    Отправляет POST реквест на сервер.
    header : str - имя команды для исполнения.
    data : пары (key, value), предоставляющие необходимые данные для выполнения запроса.
    """
    res_data = {}
    req_data = create_req_data(header=header, 
                               data=data
                               )
    try:
        res = requests.post(url, json=req_data)
                 
        if res.status_code == 200:
            try:
                res_data = res.json()
            except json.JSONDecodeError:
                print("Error occur while decoding '{}'".format(res.text))
        else:
            print("Server return error code : {}'".format(res.tatus_code))
    except  requests.exceptions.ConnectionError:
        print("Server not avalable")
    return res_data

def wrap_to_thread(func):
    """
    Декоратор для обеспечения выполнения функции в отдельном потоке.
    """
    def wpapper(**kwargs):
        thread = threading.Thread(target=func, kwargs=kwargs, daemon=False)
        return thread.start
    return wpapper

#%%%  Основные методы
@wrap_to_thread
def check_execution(route_point_id, route_id, security_id, check_point_id, begin_time, end_time):
    """
    Запрашивает у сервера историю перемещений и устанавливает, выполнена ли точки.
    В случае невыполнения на сервер посылается warning сообщение.
    route_id : int
    security_id : int 
    Временной интервал запроса истории перемещений:
    begin_time : "YYYY-MM-DD HH:MM:SS"
    end_time : "YYYY-MM-DD HH:MM:SS"
    """
    data = send_post_req(header="get_movment_history", 
                         security_id=security_id,
                         begin_time=begin_time,
                         end_time=end_time
                         )
    warning = False
    if data: 
        points = data["points"]
        if not points:
                warning = True
    if warning:
        print("send warning for route point '{}'-'{}' at '{}'".format(begin_time, end_time, str(datetime.datetime.now())))
        send_post_req(header="raise_warning",
                      security_id=security_id,
                      route_id=route_id,
                      time=str(datetime.datetime.now())
                     )
        
def schedule_points(scheduler, points):
    """
    Добавляет проверку выполнения точек в планировщик задач.
    scheduler : sched.scheduler
    points : [{route_id : int, security_id : int, 
               begin_time : str, end_time : str}, ...]
    """
    for point in points:
        if point["begin_time"] > point["end_time"]:    
            begin_time = create_datetime(point["begin_time"], -1)
        else:
            begin_time = create_datetime(point["begin_time"])
        
        end_time = create_datetime(point["end_time"])
        sched_timestamp = end_time.timestamp()
        point["end_time"] = str(end_time)
        point["begin_time"] = str(begin_time)
        
        scheduler.enterabs(sched_timestamp, 
                           priority=1, 
                           action=check_execution(**point)
                           )
        print("Set check_execution on {}".format(point["end_time"]))
        
def get_soonest_time(t):
    """
    Запрашивает от сервера время начала исполнения ближайшей к времени t точки.
    t : str "YYYY-MM-DD HH:MM:SS"
    """
    data = send_post_req(header="get_soonest_time", 
                         time=t,
                         )
    soonest_time = (datetime.datetime.now() + datetime.timedelta(minutes=10)).time().isoformat(timespec='seconds')
    if data:
        soonest_time = data["soonest_time"]
    return soonest_time

def get_between_route_points(t):
    """
    Запрашивает от сервера точки, выполняющиеся во момент времени t.
    t : str "YYYY-MM-DD HH:MM:SS" - время выполнения.
    """
    data = send_post_req(header="get_between_route_points", 
                         time=t,
                         )
    points = []
    if data:
        points = data["route_points"]
    return points


def get_route_points(t):
    """
    Запрашивает от сервера точки, начинающиеся со времени t.
    t : str "YYYY-MM-DD HH:MM:SS" - время начала.
    """
    data = send_post_req(header="get_route_points", 
                         time=t,
                         )
    points = []
    if data:
        points = data["route_points"]
    return points


@wrap_to_thread
def schedule_between_route_points(scheduler, t):
    print("enter schedule_between_route_points")
    print("planed time : '{}' - actual time : '{}'".format(t, str(datetime.datetime.now())))
    points = get_between_route_points(t)
    if points:
        schedule_points(scheduler, points)
    print("exit schedule_between_route_points")
    
@wrap_to_thread
def schedule_route_points(scheduler, t):
    print("enter schedule_route_points")
    print("planed time : '{}' - actual time : '{}'".format(t, str(datetime.datetime.now())))
    points = get_route_points(t)
    if points:
        schedule_points(scheduler, points)
    print("exit schedule_route_points")


#%%% Функции отвечающие за логику функцонирования
def run():
    """
    Запускает диспетчер : 
    Добавляет в планировщик задач опрос текущих точек.
    Добавляет в планировщик задач первый запуск loop.
    """
    print("enter run")
    scheduler = sched_sts.scheduler(time.time, time.sleep)
    sched_timestamp = datetime.datetime.now().timestamp()
    
    scheduler.enterabs(sched_timestamp, 
                       priority=1, 
                       action=schedule_between_route_points(scheduler=scheduler, 
                                                t=str(datetime.datetime.now()))
                      )
    scheduler.enterabs(sched_timestamp, 
                       priority=0, 
                       action=loop(scheduler=scheduler,  t=str(datetime.datetime.now()))
                      )
    scheduler.run()
    print("exit run")

@wrap_to_thread
def loop(scheduler, t):
    """
    Основной цикл :
    Добавляет в планировщик задач опрос ближайших точек.
    Добавляет в планировщик задач следующий свой запуск.
    """
    print("enter loop")
    print("planed time : '{}' - actual time : '{}'".format(t, str(datetime.datetime.now())))
    soonest_time = get_soonest_time(t)
    soonest_time = create_datetime(soonest_time)
    sched_timestamp = soonest_time.timestamp()
    
    scheduler.enterabs(sched_timestamp, 
                       priority=0, 
                       action=loop(scheduler=scheduler, t=str(soonest_time))
                      )
    print("Set next loop on '{}' at '{}'".format(str(soonest_time), str(datetime.datetime.now())))
    scheduler.enterabs(sched_timestamp, 
                       priority=0, 
                       action=schedule_route_points(scheduler=scheduler, t=str(soonest_time))
                      )
    print("Set schedule_route_points on '{}' at '{}'".format(str(soonest_time), str(datetime.datetime.now())))
    print("exit loop")
    
if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("Bye!")