# -*- coding:utf-8 -*-
# @FileName  : api_status_manage.py
# @Time      : 2023/7/6
# @Author    : LaiJiahao
# @Desc      : api_key状态管理

from dotenv import load_dotenv
from common.dynamic_module import get_key, dynamic_proxy
from utils.redis_storage import RedisTool
from common.status_code import HttpStatusCode
import requests
import datetime

load_dotenv(verbose=True)


class ApiStatusManagement:

    @staticmethod
    def get_billing():
        proxy = dynamic_proxy()
        redis_tool = RedisTool()
        redis_keys = redis_tool.get_keys("OPENAI_API_KEY:*")

        # start_date设置为今天日期前99天
        start_date = (datetime.datetime.now() - datetime.timedelta(days=99)).strftime("%Y-%m-%d")
        # end_date设置为今天日期+1
        end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        usage_url = proxy + "/dashboard/billing/usage"
        subscription_url = proxy + "/dashboard/billing/subscription"
        datas = []
        for redis_key in redis_keys:
            key = redis_tool.get(redis_key)
            headers = {
                "Authorization": "Bearer " + key,
                "Content-Type": "application/json",
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            }

            usage_response = requests.get(usage_url, headers=headers, params=params)
            subscription_response = requests.get(subscription_url, headers=headers)
            total = subscription_response.json()['system_hard_limit_usd']

            data = usage_response.json()
            total_usage = data.get("total_usage") / 100
            daily_costs = data.get("daily_costs")  # 总使用情况
            days = min(5, len(daily_costs))  # 最近5天的使用情况
            recent_usage = []

            for i in range(days):
                cur = daily_costs[-i - 1]
                date = datetime.datetime.fromtimestamp(cur.get("timestamp")).strftime("%Y-%m-%d")
                line_items = cur.get("line_items")
                cost = 0
                for item in line_items:
                    cost += item.get("cost")
                recent_usage.append({"date": date, "cost": cost / 100})

                data = {
                    redis_key.replace("OPENAI_API_KEY:", ""): dict(total=total, total_usage=total_usage,
                                                                   balance=total - total_usage,
                                                                   recent_usage=recent_usage)
                }
            datas.append(data)
        return datas

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

# api = ApiStatusManagement()
# print(api.get_billing())
