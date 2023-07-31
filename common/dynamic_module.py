# -*- coding:utf-8 -*-
# @FileName  : dynamic_module.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : 动态化获取代理地址和api_key

import random
import os
from common.redis_storage import RedisTool


def dynamic_key() -> str:
    redis_tool = RedisTool()
    api_keys = redis_tool.get_values("OPENAI_API_KEY:*")

    api_key = random.choice(api_keys)

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
