# -*- coding:utf-8 -*-
# @FileName  : dynamic_module.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : 动态化获取代理地址和api_key

import random
import os
from utils.redis_storage import RedisTool


def dynamic_key() -> str:
    redis_tool = RedisTool()
    api_keys = redis_tool.get_values("OPENAI_API_KEY:*")
    error_api_keys = redis_tool.get_values("OPENAI_API_KEY_ERROR:*")
    owe_api_keys = redis_tool.get_values("OPENAI_API_KEY_OWE:*")

    # 过滤掉错误的api_key和欠费的api_key
    valid_api_keys = [key for key in api_keys if key not in error_api_keys and key not in owe_api_keys]

    if not valid_api_keys:
        raise Exception("没有可用的api_key，请检查错误的api_key列表")
    if not api_keys:
        raise Exception("api_key是空的，请添加您的api_key")

    api_key = random.choice(valid_api_keys)

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
