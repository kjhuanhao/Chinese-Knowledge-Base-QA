# -*- coding:utf-8 -*-
# @FileName  : dynamic_module.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : 动态化获取代理地址和api_key
from dotenv import load_dotenv
import random
import os
from utils.redis_storage import RedisTool


# load_dotenv(override=True)


def dynamic_key() -> str:
    # api_key = os.getenv("OPENAI_API_KEY")
    redis_tool = RedisTool()
    api_key = redis_tool.get_values("OPENAI_API_KEY:*")

    if api_key is None:
        raise Exception("api_key是空的，请添加您的api_key")
    else:
        api_key = random.choice(api_key)
        return api_key


def dynamic_proxy() -> str:
    proxy = os.getenv("OPENAI_API_BASE")
    if proxy is not None:
        return proxy
    else:
        return "https://api.openai.com/v1/"


def get_key() -> list:
    redis_tool = RedisTool()
    return redis_tool.get_values("OPENAI_API_KEY:*")
