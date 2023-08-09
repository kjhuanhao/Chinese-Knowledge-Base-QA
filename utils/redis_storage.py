# -*- coding:utf-8 -*-
# @FileName  : redis_storage.py
# @Time      : 2023/7/5
# @Author    : LaiJiahao
# @Desc      : redis 存储工具

import redis
import os
import datetime

from dotenv import load_dotenv

load_dotenv(override=True, verbose=True)


class RedisTool:

    def __init__(self):
        self.host = os.getenv("REDIS_HOST")
        self.port = os.getenv("REDIS_PORT")
        self.password = os.getenv("REDIS_PASSWORD")
        self.db = os.getenv("REDIS_DB")
        self.connection = None
        expiration = datetime.timedelta(days=int(os.getenv("EXPIRE_DAYS")))
        self.expire_at = datetime.datetime.now() + expiration
        poll = redis.ConnectionPool(host=self.host,
                                    port=self.port,
                                    password=self.password,
                                    db=self.db,
                                    decode_responses=True)

        r = redis.Redis(connection_pool=poll)
        self.connection = r

    def set(self, key, value: str, nx=False):
        self.connection.set(key, value, nx=nx)
        # 设置过期时间
        self.connection.expireat(key, self.expire_at)

    def get(self, key):
        return self.connection.get(key)

    def delete(self, key):
        self.connection.delete(key)

    def close(self):
        self.connection.close()

    def get_keys(self, directory: str) -> list:
        keys = []
        cursor = "0"
        while cursor != 0:
            cursor, partial_keys = self.connection.scan(cursor=cursor, match=directory)
            keys.extend(partial_keys)
        return keys

    def get_values(self, directory: str) -> list:
        keys = self.get_keys(directory)
        values = self.connection.mget(keys)
        return values

    def delete_keys(self, directory: list[str]) -> list:
        error_keys = []
        for i in directory:
            if not self.connection.delete(i):
                error_keys.append(i)
        return error_keys

    def check_ttl(self, key):
        ttl = self.connection.ttl(key)
        return ttl

# r = RedisTool()
# print(r.get_values("name:*"))
