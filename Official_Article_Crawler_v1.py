#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
原作者：java-tech
日期：2024年2月22日  
公众号ID：java-tech  
公众号：Java实用技术手册  
声明：本文仅供技术研究，请勿用于非法采集，后果自负。
https://blog.csdn.net/kuailebuzhidao/article/details/136490529
"""

"""
Improver：OddMiss
First version：2024年11月
Github: https://github.com/OddMiss
"""

"""
Official_Article_Crawler v1 (2025.1.3)

1. Added the function of saving the cookie, token and next number in json format.
2. Added the function of cmd input for cookie and token.
3. Added the function of automatic opening of the browser to the Wechat Official login page.

"""

import webbrowser # Open the browser
import traceback
import requests
from pprint import pprint
from datetime import datetime
from time import sleep
import json
import random
import os

Link_Path = "D:/AI_data_analysis/BeijingChaoJia-Data/All_Articles_Link/" # Article link save path
FOLD_PATH = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/" # Current file path
msg_json = None # Global variable for article json data
Article_Num = None # Global variable for article number

__session = requests.Session() # Create a session object to save cookies
__headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
} # Request header
__params = {
    "lang": "zh_CN",
    "f": "json",
} # Request parameters

def Timestamp2Date(Timestamp):
    # Given timestamp
    # timestamp = 1729235272

    # Convert the timestamp to a datetime object
    dt_object = datetime.fromtimestamp(Timestamp)

    # Format the datetime object as a string (you can customize the format)
    formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_date

def Find_Min_Max_Date(Date_List):
    # Convert strings to datetime objects
    date_objects = [datetime.strptime(date, "%Y-%m-%d %H:%M:%S") for date in Date_List]

    # Find the minimum and maximum date
    min_date = min(date_objects).strftime("%Y%m%d")
    max_date = max(date_objects).strftime("%Y%m%d")

    return min_date, max_date

def Page_Series(Article_Num, Begin_Num=0, Type="Descending"):
    """
    [Begin_Article_num, Count]
    Type: "Ascending" or "Descending"
    """
    Num = Article_Num - 1
    Series = []
    if Type == "Ascending":
        for i in range(Begin_Num, Num + 1, 5):
            if i + 4 > Num:
                Series.append([i, Num - i + 1])
            else: Series.append([i, 5])
    elif Type == "Descending":
        for i in range(Num + 1 - Begin_Num - 5, -5, -5):
            if i > 0:
                Series.append([i, 5])
            else: Series.append([0, i + 5])
    else: 
        print("Invalid input. Type is 'Ascending' or 'Descending'") 
        return
    return Series

def Json_Dict(Json_Path):
    """
    Json_Path: Path of a json file
    """
    with open(Json_Path, 'r', encoding='utf-8') as file:
        data_dict = json.load(file)  # Read and convert JSON to a dictionary
    return data_dict

def Dict_To_Json(Dict, Json_Path):
    """
    Dict: any dict format variable in python

    Json_Path: Path of a json file
    """
    with open(Json_Path, 'w', encoding='utf-8') as file:
        json.dump(Dict, file, ensure_ascii=False, indent=4)  # Write as formatted JSON

def get_fakeid(nickname, begin=0, count=5):
    search_url = "https://mp.weixin.qq.com/cgi-bin/searchbiz"

    # 增加/更改请求参数
    params = {
        "action": "search_biz",
        "query": nickname,
        "begin": begin,
        "count": count,
        "ajax": "1",
    }
    __params.update(params)

    try:
        search_gzh_rsp = __session.get(search_url, headers=__headers, params=__params)
        rsp_list = search_gzh_rsp.json()
        if "list" in rsp_list.keys():  # {"list": []}
            # If there is a valid response, get the first fakeid
            rsp_list = rsp_list.get("list")
        # print(rsp_list)
        # print(type(rsp_list))
        # print(rsp_list)
            if rsp_list:
                return rsp_list[0].get("fakeid")
        return None # If there is no valid response, return None
    except Exception as e:
        raise Exception(f"获取公众号{nickname}的fakeid失败，e={traceback.format_exc()}")

def get_articles(nickname, fakeid, begin=0, count=5, Get_Num=False):
    art_url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
    art_params = {
        "query": "",
        "begin": begin,
        "count": count,
        "type": 9,
        "action": "list_ex",
        "fakeid": fakeid,
    }
    __params.update(art_params)

    global msg_json, Article_Num
    try:
        rsp_data = __session.get(art_url, headers=__headers, params=__params)
        if rsp_data:
            msg_json = rsp_data.json()
            # pprint(msg_json)
            Link_Dict = {}
            if Get_Num: # If we only get the article number
                if "app_msg_cnt" in msg_json.keys():
                    Article_Num = msg_json.get("app_msg_cnt")
                    return
            if "app_msg_list" in msg_json.keys():
                Time_List = []
                for item in msg_json.get("app_msg_list"):
                    Time = Timestamp2Date(item.get("create_time"))
                    Time_List.append(Time)
                    Link_Dict[Time] = [item.get("title"), item.get("link")]
                # result = [
                #     [item.get("title"), Timestamp2Date(item.get("create_time")), item.get("link")]
                #     for item in msg_json.get("app_msg_list")
                # ]
                # return msg_json.get('app_msg_list')
                Begin_date, End_date = Find_Min_Max_Date(Time_List)
                Json_Name = f"{Begin_date}-{End_date}.json"
                Dict_To_Json(Link_Dict, Link_Path + Json_Name)
                print(f"Articles from {Begin_date} to {End_date} are saved.")
                return Link_Dict
        return []
    except Exception as e:
        raise Exception(f"获取公众号{nickname}的文章失败，e={traceback.format_exc()}")

if __name__ == "__main__":

    Params = Json_Dict(FOLD_PATH + "Params.json") # Params dict from Params.json

    # 登录微信公众号平台，获取微信文章的cookie/token
    COOKIE_TOKEN = True # Boolean variable to determine whether the cookie and token are valid
    nickname = "北京炒家"

    print(f"The nickname is {nickname}. Would you like to change it? (y/n)")
    change = input()
    if change == "y":
        nickname = input("Please enter the nickname: ")

    while True:
        if COOKIE_TOKEN: # If the cookie and token are valid
            cookie = Params["cookie"]
            token = Params["token"]
        else:
            # If the cookie and token are invalid
            # Get user input for cookie and token
            # Open the URL in the default web browser  
            webbrowser.open("https://mp.weixin.qq.com/cgi-bin/loginpage?url=%2Fcgi-bin%2Fappmsg")
            cookie = input("Privious cookie is invalid. Please enter a new cookie: ")
            token = input("Privious token is invalid. Please enter a new token: ")
        
        __headers["Cookie"] = cookie
        __params["token"] = token

        fakeid = get_fakeid(nickname)
        if not fakeid:
            # If the fakeid is not obtained, the cookie and token are invalid, re-enter the cookie and token
            print("Privious cookie is invalid, please re-enter.")
            COOKIE_TOKEN = False
        else:
            try:
                get_articles(nickname, fakeid, Get_Num=True)
                Params["cookie"] = cookie
                Params["token"] = token
                break  # Exit the loop if successful
            except Exception as e:
                print(e)  # Print the error message and ask for input again
                COOKIE_TOKEN = False

    if not Article_Num: 
        Dict_To_Json(Params, FOLD_PATH + "Params.json")
        exit("No article is found.")

    print("All Article Num:", Article_Num)
    print("fakeid:", fakeid)
    print("*" * 60)
    sleep(5)

    Begin_Num = Params["next-begin-num"] # Reverse begin numner
    if Begin_Num >= Article_Num: 
        Dict_To_Json(Params, FOLD_PATH + "Params.json")
        exit("All articles are obtained.")

    Page_List = Page_Series(Article_Num, Begin_Num=Begin_Num, Type="Descending") # Page series
    API_Banned = False # Bealean variable to determine whether the API is banned

    print(f"Computer: from {Page_List[-1][0]} to {Page_List[0][1] if len(Page_List) == 1 else Page_List[0][0]}. Reverse: from {Begin_Num} to the end.")
    
    print("Proceed? (y/n)")
    proceed = input()
    if proceed == "n": 
        Dict_To_Json(Params, FOLD_PATH + "Params.json")
        exit("Exit the program.")

    for Page in Page_List:
        # Generate a random integer time between 10 and 20 (inclusive)
        random_time = random.randint(10, 20)

        Reverse_Begin = Article_Num - Page[0] - Page[1]
        print(f"Begin Article: {Page[0]}, Count: {Page[1]} (Reverse: Begin {Reverse_Begin})")
        article_data = get_articles(nickname, fakeid, Page[0], Page[1])
        if not article_data: 
            print(f"API is banned, try it later. Start at {Reverse_Begin} next time.")
            Params["next-begin-num"] = Reverse_Begin
            API_Banned = True
            break
        pprint(article_data)
        print(f"Sleeping {random_time}s ...")
        sleep(random_time)
    if not API_Banned:
        # Save the next begin number
        Last_Content_Len = len(article_data)
        Next_Start = Reverse_Begin + Last_Content_Len
        print(f"All the article is obtained. Start at {Next_Start} nex time.")
        Params["next-begin-num"] = Next_Start

    Dict_To_Json(Params, FOLD_PATH + "Params.json")