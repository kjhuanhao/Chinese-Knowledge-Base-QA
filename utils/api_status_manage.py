# -*- coding:utf-8 -*-
# @FileName  : api_status_manage.py
# @Time      : 2023/7/6
# @Author    : LaiJiahao
# @Desc      : api_key状态管理

from dotenv import load_dotenv
from utils.redis_storage import RedisTool
from common.status_code import HttpStatusCode

load_dotenv(verbose=True)


class ApiStatusManagement:

    @staticmethod
    def get_all_api_keys():
        redis_tool = RedisTool()
        keys = redis_tool.get_keys("OPENAI_API_KEY:*")
        api_keys = []
        for key in keys:
            value = redis_tool.get(key)
            api_key = {
                "email": key.split(":")[1],
                "api_key": value
            }
            api_keys.append(api_key)

        return {
            "code": HttpStatusCode.SUCCESS.value,
            "data": api_keys
        }

    # 添加api_key，dict={email:api_key}
    @staticmethod
    def add_api_key(api_keys: list[dict[str, str]]):
        redis_tool = RedisTool()
        for i in api_keys:
            key = list(i.keys())[0]
            value = list(i.values())[0]
            redis_tool.set("OPENAI_API_KEY:" + key, value)
        return {
            "code": HttpStatusCode.SUCCESS.value,
            "data": api_keys
        }

    @staticmethod
    def delete_api_keys(emails: list[str]):
        redis_tool = RedisTool()
        emails = ["OPENAI_API_KEY:" + email for email in emails]
        result = redis_tool.delete_keys(emails)
        result = {
            "code": HttpStatusCode.SUCCESS.value,
            "fail_emails": result
        }
        return result
