# -*- coding:utf-8 -*-
# @FileName  : api_status_manage.py
# @Time      : 2023/7/6
# @Author    : LaiJiahao
# @Desc      : api_key状态管理

from dotenv import load_dotenv
from common.dynamic_module import dynamic_proxy
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
            value = redis_tool.get(redis_key)
            headers = {
                "Authorization": "Bearer " + value,
                "Content-Type": "application/json",
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            }

            usage_response = requests.get(usage_url, headers=headers, params=params)
            subscription_response = requests.get(subscription_url, headers=headers)
            # 边界处理，处理异常key
            total = subscription_response.json().get('system_hard_limit_usd')
            if total is None:
                error = subscription_response.json().get("error")
                error['msg'] = "异常的api_key"
                datas.append({redis_key.replace("OPENAI_API_KEY:", ""): dict(error=error)})
                # 加入异常key的redis当中
                redis_tool.set("OPENAI_API_KEY_ERROR:" + redis_key.replace("OPENAI_API_KEY:", ""), value)
            else:
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
                    balance = total - total_usage

                    # 欠费的api_key
                    if balance > 0:
                        # 存入欠费名单
                        redis_tool.set("OPENAI_API_KEY_OWE:" + redis_key.replace("OPENAI_API_KEY:", ""), value)
                        # 删除有效api_key
                        redis_tool.delete(redis_key)
                    data = {
                        redis_key.replace("OPENAI_API_KEY:", ""): dict(total=total, total_usage=total_usage,
                                                                       balance=balance,
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

    @staticmethod
    def get_invalid_api_keys():
        redis_tool = RedisTool()
        owe_keys = redis_tool.get_keys("OPENAI_API_KEY_OWE:*")
        error_keys = redis_tool.get_keys("OPENAI_API_KEY_ERROR:*")
        datas = {
            "owe_keys": [],
            "error_keys": []
        }

        for owe_key in owe_keys:
            value = redis_tool.get(owe_key)
            datas['owe_keys'].append({owe_key.replace("OPENAI_API_KEY_OWE:", ""): value})
        for error_key in error_keys:
            value = redis_tool.get(error_key)
            datas['error_keys'].append({error_key.replace("OPENAI_API_KEY_ERROR:", ""): value})

        return datas

    @staticmethod
    def delete_api_keys(emails: list[str]):
        redis_tool = RedisTool()
        # 同时去删除错误和异常的api_key
        for i in emails:
            error_api_key = redis_tool.get("OPENAI_API_KEY_ERROR:" + i)
            owe_api_key = redis_tool.get("OPENAI_API_KEY_OWE:" + i)
            if error_api_key is not None:
                redis_tool.delete("OPENAI_API_KEY_ERROR:" + i)
            if owe_api_key is not None:
                redis_tool.delete("OPENAI_API_KEY_OWE:" + i)

        emails = ["OPENAI_API_KEY:" + email for email in emails]
        result = redis_tool.delete_keys(emails)
        result = {
            "code": HttpStatusCode.SUCCESS.value,
            "fail_emails": result
        }
        return result
# api = ApiStatusManagement()
# print(api.get_billing())
